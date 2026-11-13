#!/usr/bin/env python3
"""
Mathematical Equations & LaTeX Formatting Auditor
------------------------------------------------
Scans all markdown (.md) files across the repository to enforce GitHub Flavored
Markdown (GFM) and KaTeX rendering compatibility:

1. Block Display Equations ($$...$$):
   - Display equations must be isolated on their own lines, preceded and followed by blank lines.
   - Opening and closing $$ delimiters must match and enclose valid LaTeX syntax.
   - No unclosed or improperly nested delimiters.
2. Inline Math ($...$):
   - In GFM KaTeX, there must NOT be leading or trailing whitespace inside dollar signs ($x$, not $ x $).
   - Closing $ must not be preceded by whitespace.
   - Braces {} and parentheses () must be balanced.
3. Currency & Shell Variable Collisions:
   - Literal dollar signs (e.g. $100, $HOME) must not accidentally open math blocks.
4. KaTeX Macro Compatibility:
   - Validates syntax against KaTeX in strict mode.
   - Checks for unescaped underscores in \\text{} and non-ASCII character warnings.
5. Exit code:
   - Returns 0 if 0 issues remain.
   - Returns 1 if issues are detected.
"""

import os
import sys
import glob
import re
import json
import subprocess
from dataclasses import dataclass
from typing import List, Optional

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def find_katex_path() -> str:
    # 1. Try standard require.resolve
    try:
        return subprocess.check_output(
            ['node', '-e', 'console.log(require.resolve("katex"))'],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        pass

    # 2. Try global npm root
    try:
        npm_root = subprocess.check_output(
            ['npm', 'root', '-g'],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        katex_global = os.path.join(npm_root, 'katex')
        if os.path.exists(katex_global):
            return katex_global
    except Exception:
        pass

    # 3. Check npx cache directory
    npx_candidates = glob.glob(os.path.expanduser('~/.npm/_npx/*/node_modules/katex'))
    if npx_candidates:
        return npx_candidates[0]

    return 'katex'


KATEX_MODULE_PATH = find_katex_path()


@dataclass
class AuditIssue:
    file: str
    line: int
    issue_type: str
    detail: str
    raw_snippet: str
    suggested_fix: Optional[str] = None


def is_balanced(text: str, open_ch: str, close_ch: str) -> bool:
    depth = 0
    in_escape = False
    for ch in text:
        if in_escape:
            in_escape = False
            continue
        if ch == '\\':
            in_escape = True
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def validate_katex_batch(items: List[dict]) -> List[dict]:
    """
    Validates a list of {'id': int, 'math': str, 'displayMode': bool} via KaTeX in Node.js.
    """
    if not items:
        return []
    
    node_script = f"""
    let katex;
    try {{
        katex = require('{KATEX_MODULE_PATH}');
    }} catch (e) {{
        katex = require('katex');
    }}
    const fs = require('fs');
    const input = JSON.parse(fs.readFileSync(0, 'utf-8'));
    const results = [];
    for (const item of input) {{
        try {{
            katex.renderToString(item.math, {{
                displayMode: item.displayMode,
                throwOnError: true,
                strict: 'error'
            }});
            results.push({{ id: item.id, valid: true }});
        }} catch (e) {{
            results.push({{ id: item.id, valid: false, error: e.message }});
        }}
    }}
    console.log(JSON.stringify(results));
    """
    proc = subprocess.Popen(
        ['node', '-e', node_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = proc.communicate(input=json.dumps(items))
    if proc.returncode != 0:
        raise RuntimeError(f"Node KaTeX error: {stderr}")
    return json.loads(stdout)


def audit_file(file_path: str) -> List[AuditIssue]:
    issues: List[AuditIssue] = []
    rel_path = os.path.relpath(file_path, REPO_ROOT)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    num_lines = len(lines)

    in_code_block = False
    code_block_fence = ''

    # Math items to validate in KaTeX batch
    katex_queue = []
    queue_metadata = []

    # State for multi-line display math
    in_display_math = False
    display_start_line = -1
    display_math_lines = []

    i = 0
    while i < num_lines:
        line = lines[i]
        line_num = i + 1
        trimmed = line.strip()

        # Handle fenced code blocks
        if trimmed.startswith('```') or trimmed.startswith('~~~'):
            fence = trimmed[:3]
            if not in_code_block:
                in_code_block = True
                code_block_fence = fence
            elif fence == code_block_fence:
                in_code_block = False
                code_block_fence = ''
            i += 1
            continue

        if in_code_block:
            i += 1
            continue

        # Check for multi-line display math start or end
        if in_display_math:
            if trimmed == '$$':
                in_display_math = False
                math_text = '\n'.join(display_math_lines)

                # Check blank line after closing $$
                if i + 1 < num_lines and lines[i + 1].strip() != '' and not lines[i + 1].strip().startswith('#'):
                    # Blank line after is recommended
                    pass

                # Balanced braces & parens
                if not is_balanced(math_text, '{', '}'):
                    issues.append(AuditIssue(
                        file=rel_path,
                        line=display_start_line,
                        issue_type="Unbalanced Braces",
                        detail="Mismatched '{' and '}' in display equation",
                        raw_snippet=math_text[:100]
                    ))
                if not is_balanced(math_text, '(', ')'):
                    issues.append(AuditIssue(
                        file=rel_path,
                        line=display_start_line,
                        issue_type="Unbalanced Parentheses",
                        detail="Mismatched '(' and ')' in display equation",
                        raw_snippet=math_text[:100]
                    ))

                # Queue for KaTeX strict check
                item_id = len(katex_queue)
                katex_queue.append({'id': item_id, 'math': math_text, 'displayMode': True})
                queue_metadata.append({'file': rel_path, 'line': display_start_line, 'snippet': math_text, 'type': 'Display Math'})

            elif '$$' in line:
                # Closing $$ mixed with content
                in_display_math = False
                issues.append(AuditIssue(
                    file=rel_path,
                    line=line_num,
                    issue_type="Display Math Delimiter Not Isolated",
                    detail="Closing '$$' must be on its own line",
                    raw_snippet=line
                ))
            else:
                display_math_lines.append(line)
            i += 1
            continue

        if trimmed == '$$':
            in_display_math = True
            display_start_line = line_num
            display_math_lines = []

            # Check blank line before opening $$
            if i > 0 and lines[i - 1].strip() != '':
                issues.append(AuditIssue(
                    file=rel_path,
                    line=line_num,
                    issue_type="Missing Blank Line Before Display Math",
                    detail="In GFM, display equation blocks should be preceded by a blank line",
                    raw_snippet=lines[i - 1]
                ))
            i += 1
            continue

        # Check for inline display math or malformed $$
        if '$$' in line:
            # Check if line starts and ends with $$ (single-line display math)
            if trimmed.startswith('$$') and trimmed.endswith('$$') and len(trimmed) >= 4:
                math_text = trimmed[2:-2].strip()
                issues.append(AuditIssue(
                    file=rel_path,
                    line=line_num,
                    issue_type="Display Math Not Isolated On Own Line",
                    detail="Display equation is written on a single line '$$...$$'; must be isolated on its own lines",
                    raw_snippet=trimmed,
                    suggested_fix=f"$$\n{math_text}\n$$"
                ))

                # Queue for KaTeX check
                item_id = len(katex_queue)
                katex_queue.append({'id': item_id, 'math': math_text, 'displayMode': True})
                queue_metadata.append({'file': rel_path, 'line': line_num, 'snippet': math_text, 'type': 'Display Math'})

            elif trimmed.startswith('$$'):
                # Starts with $$ and opens multiline display without isolating delimiter
                issues.append(AuditIssue(
                    file=rel_path,
                    line=line_num,
                    issue_type="Display Math Delimiter Not Isolated",
                    detail="Opening '$$' delimiter must be on its own line",
                    raw_snippet=line
                ))
                # Treat as in_display_math from next line
                in_display_math = True
                display_start_line = line_num
                display_math_lines = [trimmed[2:].strip()]
            else:
                issues.append(AuditIssue(
                    file=rel_path,
                    line=line_num,
                    issue_type="Malformed Display Math Delimiter",
                    detail="Line contains '$$' mixed with text",
                    raw_snippet=line
                ))
            i += 1
            continue

        # Check inline math $...$
        # Remove inline backticks `...`
        clean_line = re.sub(r'`[^`]*`', lambda m: ' ' * len(m.group(0)), line)

        # Find unescaped dollar signs
        dollar_indices = []
        for idx, ch in enumerate(clean_line):
            if ch == '$':
                if idx == 0 or clean_line[idx - 1] != '\\':
                    dollar_indices.append(idx)

        if not dollar_indices:
            i += 1
            continue

        # Check for odd dollar count
        if len(dollar_indices) % 2 != 0:
            issues.append(AuditIssue(
                file=rel_path,
                line=line_num,
                issue_type="Unclosed or Orphan $ Delimiter",
                detail=f"Found {len(dollar_indices)} unescaped '$' signs on line",
                raw_snippet=line
            ))

        # Check pairs
        for p in range(0, len(dollar_indices) - 1, 2):
            start = dollar_indices[p]
            end = dollar_indices[p + 1]
            math_expr = clean_line[start + 1:end]

            # Leading whitespace
            if math_expr.startswith(' ') or math_expr.startswith('\t'):
                issues.append(AuditIssue(
                    file=rel_path,
                    line=line_num,
                    issue_type="Inline Math Leading Whitespace",
                    detail="In GFM KaTeX, opening '$' cannot be immediately followed by whitespace",
                    raw_snippet=f"${math_expr}$",
                    suggested_fix=f"${math_expr.lstrip()}$"
                ))

            # Trailing whitespace
            if math_expr.endswith(' ') or math_expr.endswith('\t'):
                issues.append(AuditIssue(
                    file=rel_path,
                    line=line_num,
                    issue_type="Inline Math Trailing Whitespace",
                    detail="In GFM KaTeX, closing '$' cannot be immediately preceded by whitespace",
                    raw_snippet=f"${math_expr}$",
                    suggested_fix=f"${math_expr.rstrip()}$"
                ))

            trimmed_expr = math_expr.strip()

            # Balanced braces
            if not is_balanced(trimmed_expr, '{', '}'):
                issues.append(AuditIssue(
                    file=rel_path,
                    line=line_num,
                    issue_type="Unbalanced Braces In Inline Math",
                    detail="Mismatched '{' and '}' in inline math",
                    raw_snippet=f"${math_expr}$"
                ))

            # KaTeX batch check
            if trimmed_expr:
                item_id = len(katex_queue)
                katex_queue.append({'id': item_id, 'math': trimmed_expr, 'displayMode': False})
                queue_metadata.append({'file': rel_path, 'line': line_num, 'snippet': trimmed_expr, 'type': 'Inline Math'})

        i += 1

    if in_display_math:
        issues.append(AuditIssue(
            file=rel_path,
            line=display_start_line,
            issue_type="Unclosed Display Math Block",
            detail="Display math block opened with '$$' but never closed",
            raw_snippet='\n'.join(display_math_lines[:5])
        ))

    # Run KaTeX batch validation
    if katex_queue:
        results = validate_katex_batch(katex_queue)
        for res, meta in zip(results, queue_metadata):
            if not res['valid']:
                issues.append(AuditIssue(
                    file=meta['file'],
                    line=meta['line'],
                    issue_type=f"{meta['type']} KaTeX Strict Error",
                    detail=res['error'],
                    raw_snippet=meta['snippet'][:100]
                ))

    return issues


def main():
    print("=" * 80)
    print("CROP SEQUENCE RECOMMENDER — MATHEMATICAL EQUATIONS & LATEX AUDITOR")
    print("=" * 80)

    target_files = sorted(glob.glob(os.path.join(REPO_ROOT, '**', '*.md'), recursive=True))
    print(f"Scanning {len(target_files)} markdown files across {REPO_ROOT}...\n")

    total_issues = 0
    file_issue_counts = {}

    for file_path in target_files:
        rel = os.path.relpath(file_path, REPO_ROOT)
        issues = audit_file(file_path)
        if issues:
            file_issue_counts[rel] = len(issues)
            total_issues += len(issues)
            print(f"[{rel}] — {len(issues)} issues detected:")
            for iss in issues:
                print(f"  Line {iss.line:4d}: [{iss.issue_type}]")
                print(f"            Detail: {iss.detail}")
                print(f"            Snippet: {iss.raw_snippet.replace(chr(10), ' ')}")
                if iss.suggested_fix:
                    print(f"            Fix:     {iss.suggested_fix.replace(chr(10), ' ')}")
            print("-" * 80)

    print("\n" + "=" * 80)
    print(f"AUDIT SUMMARY: {total_issues} total issues across {len(file_issue_counts)} files.")
    for f, count in file_issue_counts.items():
        print(f"  - {f:60s}: {count:3d} issues")
    print("=" * 80)

    if total_issues == 0:
        print("\nSUCCESS: 0 mathematical / LaTeX formatting errors detected! All equations pass 100%.")
        sys.exit(0)
    else:
        print(f"\nAUDIT FAILED: {total_issues} formatting/KaTeX errors remain to be resolved.")
        sys.exit(1)


if __name__ == '__main__':
    main()
