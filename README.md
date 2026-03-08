# 🕷️ Web Scraping & Data Mining – Tender Intelligence Suite

A comprehensive collection of Python-based web scraping and data mining tools focused on **government tender portals**, **international development bank projects**, and **supply chain intelligence** for the infrastructure and water supply sector.

---

## 📌 Project Overview

This repository contains Jupyter Notebooks and Python automation scripts built to automate the collection, extraction, classification, and processing of tender data from multiple government and financial institution portals. The primary domain focus is **Ductile Iron (DI) pipes**, **water supply projects**, and **AMRUT/urban infrastructure tenders** across Indian states and international development banks.

---

## 🗂️ Project Modules

### 1. 🌐 Multi-Portal Tender Scraping

**Files:** `Tender247.ipynb`, `tENDER247_ALL_LIVE_DATA.ipynb`, `Department_tender247.ipynb`, `West_Bengal_tender247.ipynb`, `Amrut_teender247.ipynb`

Scrapes live and historical tender data from [Tender247](https://tender247.in) using Selenium. Extracts tender ID, title, department, deadline, BOQ links, and bid values. Supports department-wise and state-wise filtering.

---

### 2. 🦈 TenderShark Scraper

**File:** `Tendershark.com.ipynb`

Automated scraper for [TenderShark](https://tendershark.com) that extracts sector-wise tender listings including tender type, estimated value, and submission dates using BeautifulSoup + Selenium.

---

### 3. 🔍 Tenderdetails.com Scraper & Automation

**Files:** `Tenderdetails_scraping_without_login.ipynb`, `Webscrap_tenderdetails.ipynb`, `Dailytenderdetails.py`, `Tenderdetails_automation.py`

Full automation pipeline for [TenderDetail](https://www.tenderdetail.com) — supports login, category-based filtering (water, DI pipe, ductile iron), daily data download, and organized storage into dated folder structures on OneDrive.

---

### 4. 🐯 Tiger Tender Scraper

**Files:** `Tigher_tender_scriping.ipynb`, `Tiger_tender_keyword_data.ipynb`, `TighertenderDownloadzip.ipynb`, `tIGHERTENDER_EXTRAC_DISPLAY DATA.ipynb`

Scrapes tender listings from Tiger Tender portal. Supports keyword-based search, ZIP file downloads of tender documents, and structured data extraction into Excel.

---

### 5. 🏛️ State Government Tender Portals

Dedicated scrapers for individual Indian state e-procurement portals:

| Notebook | Portal |
|---|---|
| `Odisha_eprocurment.ipynb` | Odisha eProcurement (tendersodisha.gov.in) |
| `Odisha_Govsite_Scrape_past_data.ipynb` | Odisha Government – Historical Data |
| `Jharkhan_Govt_data.ipynb` | Jharkhand eProcurement (JUIDCO World Bank) |
| `Bengal.ipynb` / `west_Bengal.ipynb` | West Bengal Government Tender Portal |
| `TelanganaUDC.ipynb` | Telangana Urban Development Corp |
| `MPUDC_DATA.ipynb` | Madhya Pradesh Urban Development Corp |
| `Assam_govt_past_departmentwise.ipynb` | Assam Government – Department-wise Past Tenders |

Each scraper handles dynamic page rendering, pagination, and exports structured data to Excel.

---

### 6. 🏦 International Development Bank Scrapers

Scrapers for multilateral funding institution project databases:

| Notebook | Institution |
|---|---|
| `aiib.ipynb` / `aiib_f...ipynb` | Asian Infrastructure Investment Bank (AIIB) |
| `EIB.ipynb` / `EIB_Bank_data.ipynb` | European Investment Bank (EIB) |
| `NDB1.ipynb` / `NDB_Final_code.ipynb` | New Development Bank (NDB) |
| `worldbank_API.ipynb` / `World_bank_project_scraper.ipynb` | World Bank Projects API |
| `AFD (1).ipynb` | Agence Française de Développement (AFD) |
| `CDB.ipynb` | Caribbean Development Bank |
| `CAF.ipynb` | CAF – Development Bank of Latin America |
| `europe_coMISSION.ipynb` | European Commission Funding Projects |
| `KPPP_AWARDED.ipynb` | KPPP Awarded Projects |

---

### 7. 📄 BOQ (Bill of Quantities) Downloader & Classifier

**Files:** `BOQ_NIT_BOQ_DOWNLOAD (1).ipynb`, `Tender_details_BOQ_Download (2).ipynb`, `Tender_details_tdr_BOQ_NIT_DOWNLOAD.ipynb`, `tdrwiseboqnitdownload (2).ipynb`

Automates downloading of BOQ/NIT documents from tender portals given a list of Tender Reference Numbers (TDRs). Organizes downloads into folder structures keyed by TDR number.

---

### 8. 🔎 DI Pipe Scope Finder in BOQ Sheets

**Files:** `DIPIPE_SCOPE_FIND_BOQSHEET.ipynb`, `DI_SCOPE_USING ZIP FILE (1).ipynb`, `SCOPE (2).ipynb`, `Find_DIpe_inBOQ_sheet_eachfolder_ (2).ipynb`, `findeachtdr folder boq in di pipe.ipynb`

Parses downloaded BOQ Excel files to detect and classify Ductile Iron (DI) pipe references. Extracts pipe class (K7, K9, K12, etc.), diameter, and quantity from unstructured BOQ data using regex and keyword matching.

---

### 9. 📊 BOQ Data Consolidation & Class Filtering

**Files:** `BOQFilter (1).ipynb`, `all_boq_dipipe_onesheet (2).ipynb`, `all_boq_to_onesheet_find CLASS.ipynb`, `BOQSHEET TO CLASS FIND.ipynb`, `File wise DI class (2).ipynb`, `TDR sub folderwise BOQ.ipynb`

Merges BOQ data from multiple TDR folders into a single consolidated sheet. Identifies and filters rows containing DI pipe class specifications, enabling bulk analysis of supply scope across hundreds of tenders.

---

### 10. 🏗️ AMRUT Tender Data Processing

**Files:** `AMRUT-31.ipynb`, `amrut_tender_scriping.ipynb`, `Govt_boqsummary_extract.ipynb`

Processes AMRUT (Atal Mission for Rejuvenation and Urban Transformation) tender BOQ files. Extracts item descriptions, quantities, and unit rates from raw government Excel BOQ formats.

---

### 11. 🔗 Ensun DI Pipe & Distributor Intelligence

**Files:** `Ensun_web_scraping (1).ipynb`, `DI_ENSUN.ipynb`, `Ensun_DI.ipynb`, `Ensun_UPVC.ipynb`, `Ductile Iron Pipe_ensun.ipynb`, `DI_Company_scraping_ensun.ipynb`, `DI_fitting_distributer.ipynb`, `Common_di_company_list.ipynb`

Scrapes [Ensun](https://ensun.io) for DI pipe manufacturers, UPVC suppliers, and fitting distributors. Extracts company names, locations, product categories, and contact details to build market intelligence databases.

---

### 12. 💼 LinkedIn Company Scraper

**File:** `Linkedin_Scraping.ipynb`

Automates LinkedIn browsing (post-manual login) to extract company profiles, employee counts, and industry data relevant to infrastructure and pipe manufacturing sectors.

---

### 13. 📡 Nexizo / BidAssist Scraper

**Files:** `Nexizo_Bidassist.ipynb`, `nexizo_url.ipynb`

Uses cookie-based authentication to scrape tender listings from [Nexizo](https://nexizo.ai). Automates document downloads and organizes them into dated folder structures.

---

### 14. 🔁 Tender Data Merging & Deduplication

**Files:** `Teder_Details_Merging (1).ipynb`, `alldata_fetched.ipynb`, `livetender_alldata.ipynb`, `Keyword_search_tender_details.ipynb`

Merges tender data from multiple sources and portals into unified datasets. Supports keyword-based filtering, deduplication by tender ID, and export to Excel for downstream reporting.

---

### 15. 📋 Revenue & Data Cleaning

**Files:** `revenue_clean_data.ipynb`, `Scaper_Excel.ipynb`, `scrapingwithexcel.ipynb`, `OPVC.ipynb`

Cleans and standardizes scraped revenue and tender data. Handles messy Excel structures, removes illegal characters, normalizes column headers, and prepares data for analysis.

---

### 16. ⚙️ Automation Scripts (Production)

**Files:** `Dailytenderdetails.py`, `Tenderdetails_automation.py`, `Tender247automationdailydata.py`

Production-ready Python scripts for scheduled daily data collection. Run via Windows Task Scheduler or cron. Supports configurable categories, automatic folder creation, OneDrive sync paths, and multi-browser support (Chrome/Edge).

**Run instructions:** See `run_dailytender.txt`, `run_tenderdetails.txt`, `run_tender247.txt`

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `Selenium` | Dynamic web page automation & scraping |
| `BeautifulSoup` | HTML parsing |
| `Pandas` | Data manipulation & Excel I/O |
| `openpyxl` | Excel file generation |
| `Requests` | REST API calls (World Bank API) |
| `webdriver-manager` | Automatic ChromeDriver management |
| `Python 3.x` | Core language |
| `Jupyter Notebook` | Development & exploration |

---

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/web-scraping-tender-intelligence.git
cd web-scraping-tender-intelligence
pip install selenium webdriver-manager pandas openpyxl beautifulsoup4 requests
```

> **Note:** Google Chrome must be installed. ChromeDriver is managed automatically via `webdriver-manager`.

---

## 🚀 Quick Start

1. Open any `.ipynb` file in Jupyter Notebook or JupyterLab.
2. Update file paths and credentials in the config section at the top of each notebook.
3. Run all cells sequentially.
4. Output Excel files will be saved to the configured directory.

For production automation scripts, update `BASE_DIR` and credentials in the `.py` files, then schedule with Task Scheduler or cron.

---

## 📁 Repository Structure

```
📦 web-scraping-tender-intelligence
 ┣ 📂 CODE/
 ┃ ┣ 📓 [Portal Scrapers].ipynb
 ┃ ┣ 📓 [BOQ Processors].ipynb
 ┃ ┣ 📓 [Bank Data Scrapers].ipynb
 ┃ ┣ 🐍 Dailytenderdetails.py
 ┃ ┣ 🐍 Tenderdetails_automation.py
 ┃ ┣ 🐍 Tender247automationdailydata.py
 ┃ ┗ 📄 run_*.txt
 ┗ 📄 README.md
```

---

## ⚠️ Disclaimer

These scripts are developed for **internal business intelligence and market research** purposes. Always ensure your usage complies with the **Terms of Service** of each website being scraped. Do not use for unauthorized data collection.

---

## 👤 Author

**Jaydeb** – Data Engineer / Automation Developer  
Rashmi Metaliks Limited  

---

## 📄 License

This project is for private/internal use. Contact the author for licensing inquiries.
