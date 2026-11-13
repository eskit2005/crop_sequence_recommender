# 🌾 Scientific Evaluation Audit Across 20 Diverse Bangladesh Scenarios
### Crop Sequence Evaluator Decision Support System (DSS) Benchmark

This document summarizes the diagnostic evaluation and targeted remediation for **20 representative agricultural scenarios** across Bangladesh, evaluated deterministically by our 6-Stage Evaluator Decision Support System ([`src/evaluator/`](../src/evaluator/)).

---

## 📊 Evaluation Methodology & Scoring Rules

The rotation composite score ($S_{\text{total}} \in [0, 100]$) is computed across 5 biophysical and socio-economic dimensions:
$$S_{\text{total}} = 0.20 \cdot S_{\text{climate}} + 0.20 \cdot S_{\text{hydro}} + 0.20 \cdot S_{\text{biology}} + 0.20 \cdot S_{\text{soil}} + 0.20 \cdot S_{\text{economics}}$$

### Grading & Risk Tiers
* **$85.0 \le S_{\text{total}} \le 100.0$ (`Grade A / A+`):** `AGRO_ECOLOGICAL_EXCELLENCE` (Resilient, regenerative rotation).
* **$65.0 \le S_{\text{total}} < 85.0$ (`Grade B / C+`):** `MODERATE_OPPORTUNITY` (Viable sequence with minor optimization opportunities).
* **$40.0 \le S_{\text{total}} < 65.0$ (`Grade C / D+`):** `HIGH_AGRONOMIC_RISK` (Significant pest, soil degradation, or turnaround risk).
* **$S_{\text{total}} < 40.0$ (`Grade D- / F`):** `CRITICAL_BLOCKER` (**Strict Hard Cap**: any fatal biophysical failure—such as crop drowning in flash floods, 100% pulse mortality under salinity, or impossible negative turnaround overlaps—strictly caps the overall score at **$\le 38.0$** regardless of economic profitability).

---

## 📋 Comprehensive 20-Scenario Benchmark Table

| # | Location & Agro-Ecological Zone | Evaluated Crop Sequence & Cultivars | Score | Grade | Diagnostic Risk Status | Key Agronomic Finding & Targeted Smart Swap |
| :- | :--- | :--- | :---: | :---: | :--- | :--- |
| **01** | **Bogura - Adamdighi**<br>*(Tista Meander Floodplain, AEZ 3)* | Potato [Diamond] ➔ Tomato [Summer] ➔ T. Aman Rice [BRRI dhan49] | **59.8** | `C` | HIGH_AGRONOMIC_RISK | **Issue:** সোলানেসি উইল্ট ও কৃমি রোগচক্র (*Ralstonia* & *Meloidogyne* bridge)<br>**Swap:** Mungbean (BARI Mung-6) to break pathogen carryover (+40 kg N/ha) |
| **02** | **Bogura - Shibganj**<br>*(Level Barind / Tista, AEZ 25)* | Potato [Granola] ➔ Boro Rice [BRRI dhan28] ➔ T. Aman Rice [BRRI dhan49] | **38.0** | `D-` | CRITICAL_BLOCKER | **Issue:** সময়সূচির তীব্র সাংঘর্ষিকতা ও জমি জট (Turnaround clash & soft rot risk)<br>**Swap:** Short-Duration T. Aman (ব্রি ধান৭৫ / ব্রি ধান৭১) |
| **03** | **Satkhira - Shyamnagar**<br>*(Coastal Saline Belt, AEZ 13)* | Lentil [BARI Masur-8] ➔ Mungbean [BARI Mung-6] ➔ T. Aman Rice [Local] ($EC_e = 7.8$) | **38.0** | `D-` | CRITICAL_BLOCKER | **Issue:** মারাত্মক লবণাক্ততায় ডাল ফসলের নিশ্চিত মৃত্যু (100% pulse mortality at $7.8\text{ dS/m}$)<br>**Swap:** Sunflower (হীরা-১ / BARI Surjamukhi-2; salt threshold $5.5\text{ dS/m}$) |
| **04** | **Khulna - Dacope**<br>*(Ganges Tidal Saline Plain, AEZ 13)* | Sunflower [Hysun-33] ➔ Fallow ➔ T. Aman Rice [BRRI dhan73] ($EC_e = 6.5$) | **76.0** | `B` | MODERATE_OPPORTUNITY | **Issue:** লবণাক্ততার বিরুদ্ধে স্থিতিস্থাপক আদর্শ বিন্যাস (Coastal polder benchmark)¹<br>**Swap:** **Optimal (No swap required)** |
| **05** | **Rajshahi - Godagari**<br>*(High Barind Tract, AEZ 26)* | Boro Rice [BRRI dhan29] ➔ Fallow ➔ T. Aman Rice [BRRI dhan51] | **71.0** | `C+` | MODERATE_OPPORTUNITY | **Issue:** বরেন্দ্র উঁচু জমিতে ভূগর্ভস্থ পানির ভয়াবহ অবনমন (Aquifer overdraft)<br>**Swap:** Chickpea / Mustard (বারি ছোলা-৯ / বারি সরিষা-১৪; low-water staple) |
| **06** | **Naogaon - Niamatpur**<br>*(High Barind Drought Belt, AEZ 26)* | Chickpea [BARI Chola-5] ➔ Aus Rice [BRRI dhan48] ➔ T. Aman Rice [BRRI dhan71] | **73.6** | `C+` | MODERATE_OPPORTUNITY | **Issue:** জমি প্রস্তুতির স্বল্প সময় ও খরা ঝুঁকি (Moisture deficit in dry transition)<br>**Swap:** Chickpea / Barley (বারি ছোলা-৯ / বারি বার্লি-৬) |
| **07** | **Sunamganj - Tahirpur**<br>*(Haor Basin Wetland, AEZ 21)* | Boro Rice [Late HYV - BRRI dhan29] ➔ Fallow ➔ Fallow | **38.0** | `D-` | CRITICAL_BLOCKER | **Issue:** ১৫ই এপ্রিল মেঘালয়ের পাহাড়ি ঢলে ফসল তলিয়ে যাওয়ার নিশ্চিত ঝুঁকি (Pre-monsoon flash flood)<br>**Swap:** BRRI dhan88 / BRRI dhan96 (স্বল্পমেয়াদী ১৪০ দিনের আগাম বোরো জাত) |
| **08** | **Kishoreganj - Nikli**<br>*(Haor Basin Wetland, AEZ 21)* | Boro Rice [BRRI dhan88 (Early)] ➔ Fallow ➔ Fallow | **80.7** | `B` | MODERATE_OPPORTUNITY | **Issue:** আগাম জাত দিয়ে সফলভাবে পাহাড়ি ঢল এড়ানো হাওর বিন্যাস (Flood escape benchmark)²<br>**Swap:** **Optimal (No swap required)** |
| **09** | **Rangpur - Mithapukur**<br>*(Tista Meander Floodplain, AEZ 3)* | Potato [Cardinal] ➔ Maize [NK-40] ➔ T. Aman Rice [BRRI dhan49] | **73.0** | `C+` | MODERATE_OPPORTUNITY | **Issue:** তীব্র পুষ্টি ক্ষয় ও খরিপ-২ রোপণে বিলম্ব (Nutrient mining -410 kg N/ha & delay)<br>**Swap:** Short-Duration T. Aman (ব্রি ধান৭৫ / ব্রি ধান৭১) |
| **10** | **Dinajpur - Birganj**<br>*(Old Himalayan Piedmont Plain, AEZ 1)* | Wheat [BARI Gom-28] ➔ Mungbean [BARI Mung-6] ➔ T. Aman Rice [BRRI dhan34] | **70.0** | `C+` | MODERATE_OPPORTUNITY | **Issue:** অম্লীয় মাটি (pH 5.5) ও গম কাটার পর বিলম্ব (Terminal heat & acidity)<br>**Swap:** Sesbania (সবুজ সার ধৈঞ্চা) + ডলোচুন প্রয়োগ (1.5 t/ha) |
| **11** | **Mymensingh - Trishal**<br>*(Old Brahmaputra Floodplain, AEZ 9)* | Boro Rice [BRRI dhan28] ➔ Aus Rice [BRRI dhan48] ➔ T. Aman Rice [BRRI dhan49] | **38.0** | `D-` | CRITICAL_BLOCKER | **Issue:** টানা তিন ধান চাষে জমি তৈরির সময়সূচির সংঘর্ষ (-29 days) ও লাঙলের তল শক্ত হওয়া<br>**Swap:** Dhaincha (সবুজ সার ধৈঞ্চা - *Sesbania aculeata*) |
| **12** | **Jamalpur - Islampur**<br>*(Active Brahmaputra Charland, AEZ 7)* | Mustard [Tori-7] ➔ Jute [O-9897] ➔ T. Aman Rice [BRRI dhan52] | **74.5** | `C+` | MODERATE_OPPORTUNITY | **Issue:** চরাঞ্চলে পরবর্তী রবি ফসল দেরিতে বপনের ঝুঁকি (Charland wrap-around delay)<br>**Swap:** Mustard (বারি সরিষা-১৪ / বারি সরিষা-১৭; short 80-day oilseed) |
| **13** | **Cumilla - Chandina**<br>*(Old Meghna Estuary, AEZ 19)* | Potato ➔ Boro Rice ➔ T. Aman Rice ➔ Potato ➔ Boro Rice ➔ T. Aman Rice (2-Year) | **38.0** | `D-` | CRITICAL_BLOCKER | **Issue:** নিবিড় ত্রি-ফসলি চক্রে সময়সূচির সংঘর্ষ ও সোলানেসি রোগ জীবাণু দীর্ঘস্থায়িত্ব<br>**Swap:** Short-Duration T. Aman (ব্রি ধান৭৫ / ব্রি ধান৭১) |
| **14** | **Noakhali - Subarnachar**<br>*(Young Meghna Estuary, AEZ 18)* | Grass pea [Local Khesari] ➔ Fallow ➔ T. Aman Rice [Rajasail] ($EC_e = 4.5$) | **78.8** | `B` | MODERATE_OPPORTUNITY | **Issue:** রিলে খেসারি সফল কিন্তু রবি খরার ঝুঁকি (Residual moisture relay system)<br>**Swap:** Sunflower (হীরা-১ / BARI Surjamukhi-2) |
| **15** | **Barishal - Babuganj**<br>*(Ganges Tidal Non-Saline, AEZ 12)* | Boro Rice [BRRI dhan29] ➔ Aus Rice [BRRI dhan48] ➔ T. Aman Rice [BRRI dhan49] | **38.0** | `D-` | CRITICAL_BLOCKER | **Issue:** একটানা ধান চাষে মাটির শক্ত তল তৈরি ও দস্তা-গন্ধক ঘাটতি (Plow-pan compaction & -290 kg N deficit)<br>**Swap:** Dhaincha (সবুজ সার ধৈঞ্চা - *Sesbania aculeata*) |
| **16** | **Patuakhali - Kalapara**<br>*(Ganges Tidal Saline Belt, AEZ 13)* | Mungbean [BARI Mung-6] ➔ Fallow ➔ T. Aman Rice [Sadashail] ($EC_e = 6.0$) | **38.0** | `D-` | CRITICAL_BLOCKER | **Issue:** উপকূলীয় রবি লবণাক্ততা ও অনাবাদি খরার মারাত্মক ঝুঁকি (Fatal pulse salinity failure)<br>**Swap:** Sunflower (হীরা-১ / BARI Surjamukhi-2) |
| **17** | **Jashore - Jhikargachha**<br>*(High Ganges Floodplain, AEZ 11)* | Cauliflower [Snowball] ➔ Jute [Tossa] ➔ T. Aman Rice [BRRI dhan49] | **74.5** | `C+` | MODERATE_OPPORTUNITY | **Issue:** বাণিজ্যিক সবজি তোলার পর পাট ও আমন চাষে সময়ের টানাটানি (Turnaround delay)<br>**Swap:** Mustard (বারি সরিষা-১৪ / বারি সরিষা-১৭) |
| **18** | **Kushtia - Daulatpur**<br>*(High Ganges River Floodplain, AEZ 11)* | Tobacco [Virginia] ➔ Sesame [BARI Til-4] ➔ T. Aman Rice [BRRI dhan49] | **74.5** | `C+` | MODERATE_OPPORTUNITY | **Issue:** তামাক চাষে মাটির মারাত্মক পুষ্টি ক্ষয় ও বিষাক্ত প্রভাব (Tobacco nutrient mining & allelopathy)<br>**Swap:** Mustard (বারি সরিষা-১৪ / বারি সরিষা-১৭) |
| **19** | **Sylhet - Golapganj**<br>*(Surma-Kushiyara Acid Lowland, AEZ 20)* | Boro Rice [BRRI dhan28] ➔ Fallow ➔ T. Aman Rice [BRRI dhan49] (Soil pH 4.8) | **65.0** | `C+` | MODERATE_OPPORTUNITY | **Issue:** তীব্র অম্লত্বে ফসফরাস আবদ্ধতা ও অ্যালুমিনিয়াম বিষাক্ততা (Soil acidity stress at pH 4.8)<br>**Swap:** Mustard (বারি সরিষা-১৪) + ডলোচুন প্রয়োগ (1.5 টন/হেক্টর) |
| **20** | **Bandarban - Sadar**<br>*(Chittagong Hill Tracts, AEZ 29)* | Maize [Pacific-984] ➔ Fallow ➔ T. Aman Rice [Pajam] (Sloping Upland) | **38.0** | `D-` | CRITICAL_BLOCKER | **Issue:** সেচবিহীন রবি খরা ও পাহাড়ের ঢালে ভূমিক্ষয় ঝুঁকি (Rainfed winter drought & soil erosion)<br>**Swap:** Chickpea / Barley (বারি ছোলা-৯ / বারি বার্লি-৬; zero-irrigation hardy crops) |

---

### 📝 Footnotes on Optimal Benchmark Sequences
* **¹ Scenario 04 (Khulna - Dacope):** Acclaimed coastal polder adaptation model. Sunflower utilizes deep residual moisture before peak dry-season salinity arrives; Kharif-1 fallow allows monsoonal rains to leach surface salts without crop risk; saline-tolerant BRRI dhan73 thrives during Kharif-2.
* **² Scenario 08 (Kishoreganj - Nikli):** Premier Haor flood-escape strategy. Utilizing short-duration BRRI dhan88 (140 days) completes flowering and harvesting by April 5–10, escaping the catastrophic April 15 Meghalaya pre-monsoon flash floods that drown late-maturing crops (BRRI dhan29).
