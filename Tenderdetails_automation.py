#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import time
import shutil
import glob
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============================
# ---- USER CONFIG HERE  -----
# ============================
# Root folder on OneDrive
BASE_DIR = r"C:\Users\Jaydeb\OneDrive - RASHMI METALIKS LIMITED\RML_DATA\Dailydata_tenderdetails"

# Browser downloads here first; then we move to final subfolders
BROWSER_DOWNLOAD_DIR = BASE_DIR

# Credentials
TENDERDETAIL_USERNAME = "dredgingtender@rashmigroup.com"
TENDERDETAIL_PASSWORD = "Rashmi@2022"

# Browser: "chrome" or "edge"
BROWSER = "chrome"

# URLs
LOGIN_URL = "https://www.tenderdetail.com/Account/LogOn"
DASHBOARD_URL = "https://www.tenderdetail.com/registeruser/dashboard"

# Category config (slug -> (query_id, dashboard row text))
CATEGORIES = {
    "water": ("342140", "water"),
    "di_pipe": ("342118", "di pipe"),
    "ductile_iron": ("342141", "ductile iron"),
}

# Destination folders (exact paths) — UPDATED
DEST_FOLDERS = {
    # Inbox (mail) downloads
    "mail": os.path.join(BASE_DIR, "live_data", "Mail_Live"),

    # WATER
    "water_live": os.path.join(BASE_DIR, "live_data", "Water_live"),
    "water_close": os.path.join(BASE_DIR, "Close_data", "Water_close"),

    # DI PIPE
    "di_pipe_live": os.path.join(BASE_DIR, "live_data", "Di_live"),
    "di_pipe_close": os.path.join(BASE_DIR, "Close_data", "Di_pipe_close"),

    # DUCTILE IRON
    "ductile_iron_live": os.path.join(BASE_DIR, "live_data", "Ductile_Iron_live"),
    "ductile_iron_close": os.path.join(BASE_DIR, "Close_data", "Ductile_iron_close"),
}

# Dates
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

SHORT, MED, LONG = 5, 15, 30


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _new_driver(download_dir: str):
    _ensure_dir(download_dir)
    if BROWSER.lower() == "edge":
        from selenium.webdriver.edge.options import Options as EdgeOptions
        opts = EdgeOptions()
        opts.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": True,
        })
        opts.add_argument("--start-maximized")
        return webdriver.Edge(options=opts)

    from selenium.webdriver.chrome.options import Options as ChromeOptions
    opts = ChromeOptions()
    opts.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    })
    opts.add_argument("--start-maximized")
    return webdriver.Chrome(options=opts)


def wait_click(driver, by, locator, timeout=LONG):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, locator)))
    el.click()
    return el


def wait_visible(driver, by, locator, timeout=LONG):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, locator)))


def click_resilient(driver, el):
    try:
        el.click(); return True
    except Exception:
        pass
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.2)
        el.click(); return True
    except Exception:
        pass
    try:
        driver.execute_script("arguments[0].click();", el); return True
    except Exception:
        return False


def _scroll_center(driver, el):
    driver.execute_script(
        "const r=arguments[0].getBoundingClientRect();"
        "window.scrollTo({top: window.scrollY + r.top - (window.innerHeight/2) + (r.height/2)});",
        el
    )
    time.sleep(0.25)


def login(driver):
    driver.get(LOGIN_URL)

    # Optional cookie banner
    try:
        cookie_btn = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Accept') or contains(.,'Got it')]"))
        )
        click_resilient(driver, cookie_btn)
    except Exception:
        pass

    # Activate "UserName" tab
    try:
        tab = WebDriverWait(driver, MED).until(
            EC.element_to_be_clickable((By.ID, "custom-tabs-four-profile-tab"))
        )
        click_resilient(driver, tab)
    except TimeoutException:
        pass

    u = WebDriverWait(driver, MED).until(EC.presence_of_element_located((By.ID, "txtUserName")))
    p = WebDriverWait(driver, MED).until(EC.presence_of_element_located((By.ID, "Password")))
    if not u.get_attribute("value"):
        u.clear(); u.send_keys(TENDERDETAIL_USERNAME)
    if not p.get_attribute("value"):
        p.clear(); p.send_keys(TENDERDETAIL_PASSWORD)

    btn = WebDriverWait(driver, MED).until(EC.presence_of_element_located((By.ID, "btnLogin")))
    if not click_resilient(driver, btn):
        raise TimeoutException("Login button not clickable")

    WebDriverWait(driver, LONG).until(
        EC.any_of(
            EC.url_contains("/registeruser"),
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[src='/Content/Img/RegisterSectionLogo.png']")),
        )
    )
    driver.get(DASHBOARD_URL)
    wait_visible(driver, By.CSS_SELECTOR, "img[src='/Content/Img/RegisterSectionLogo.png']")


def go_back_to_dashboard(driver):
    wait_click(driver, By.CSS_SELECTOR, "img[src='/Content/Img/RegisterSectionLogo.png']")
    WebDriverWait(driver, LONG).until(EC.url_contains("/dashboard"))


# ---------- Inbox ----------
def _latest_download(source_dir: str, after_ts: float):
    time.sleep(2)
    c = [p for p in glob.glob(os.path.join(source_dir, "*")) if os.path.getmtime(p) >= after_ts]
    if not c:
        c = glob.glob(os.path.join(source_dir, "*"))
    return max(c, key=os.path.getmtime) if c else None


def _download_wait_and_move(source_dir: str, dest_dir: str, base_name: str, timeout_sec: int = 120):
    _ensure_dir(dest_dir)
    start = time.time()
    end = start + timeout_sec
    while time.time() < end:
        path = _latest_download(source_dir, start)
        if path and not (path.endswith(".crdownload") or path.endswith(".part")):
            _, ext = os.path.splitext(path)
            target = os.path.join(dest_dir, f"{base_name}{ext}")
            if os.path.abspath(path) != os.path.abspath(target):
                if os.path.exists(target):
                    os.remove(target)
                shutil.move(path, target)
            return target
        time.sleep(1)
    raise TimeoutException("Download did not appear")


def _try_click_download_like_links(driver):
    selectors = [
        (By.XPATH, "//a[.//i[contains(@class,'fa-download')]]"),
        (By.XPATH, "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'download')]"),
        (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'download')]"),
        (By.XPATH, "//a[contains(@href,'download')]"),
    ]
    for by, xp in selectors:
        try:
            el = driver.find_element(by, xp)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            try:
                el.click(); return True
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", el); return True
                except Exception:
                    continue
        except NoSuchElementException:
            continue
    return False


def download_first_inbox_item(driver):
    # Dashboard → inbox
    try:
        inbox_link = WebDriverWait(driver, MED).until(EC.element_to_be_clickable((By.ID, "anchordominbox")))
        click_resilient(driver, inbox_link)
    except Exception:
        driver.get("https://www.tenderdetail.com/registeruser/inbox")

    WebDriverWait(driver, LONG).until(EC.url_contains("/registeruser/inbox"))

    # Try direct download on list
    if _try_click_download_like_links(driver):
        saved = _download_wait_and_move(BROWSER_DOWNLOAD_DIR, DEST_FOLDERS["mail"], f"tenderdetails-{TODAY}")
        print(f"Saved: {saved}")
        return

    # Otherwise open first item then download
    for xp in [
        "//table//tr[.//a][1]//a[1]",
        "(//div[contains(@class,'mail') or contains(@class,'list') or contains(@class,'inbox')]//a)[1]",
        "(//a[contains(.,'View') or contains(.,'Open')])[1]",
    ]:
        try:
            first_link = WebDriverWait(driver, MED).until(EC.element_to_be_clickable((By.XPATH, xp)))
            _scroll_center(driver, first_link)
            click_resilient(driver, first_link)
            break
        except Exception:
            continue

    if not _try_click_download_like_links(driver):
        try:
            att = WebDriverWait(driver, SHORT).until(
                EC.element_to_be_clickable((By.XPATH, "(//a[contains(@href,'file') or contains(@href,'attachment')])[1]"))
            )
            click_resilient(driver, att)
        except Exception:
            raise TimeoutException("No download/attachment link found in inbox item")

    saved = _download_wait_and_move(BROWSER_DOWNLOAD_DIR, DEST_FOLDERS["mail"], f"tenderdetails-{TODAY}")
    print(f"Saved: {saved}")


# ---------- Listing pages ----------
def open_category_view(driver, query_id: str, tendertype: int, row_label: str):
    href = f"/registeruser/indiantenders/{query_id}?tendertype={tendertype}"
    try:
        wait_click(driver, By.XPATH, f"//a[@href='{href}' and @tendertype='{tendertype}']")
    except TimeoutException:
        row = wait_visible(
            driver,
            By.XPATH,
            f"//td[translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{row_label}']/parent::tr"
        )
        if tendertype == 2:
            view = row.find_element(By.XPATH, ".//a[contains(@href, 'tendertype=2') and contains(., 'View')]")
        else:
            view = row.find_element(By.XPATH, ".//a[contains(@href, 'tendertype=4') and contains(., 'View')]")
        driver.execute_script("arguments[0].click();", view)

    wait_visible(driver, By.ID, "freshTenders")
    wait_visible(driver, By.ID, "DivMain")


def open_datepicker(driver):
    try:
        wait_click(driver, By.ID, "drpRegisterUserDD")
    except Exception:
        pass
    for sel in (
        (By.CSS_SELECTOR, "div.daterangepicker[style*='display: block']"),
        (By.XPATH, "//div[contains(@class,'daterangepicker') and not(contains(@style,'display: none'))]"),
        (By.CSS_SELECTOR, "div.daterangepicker"),
    ):
        try:
            return WebDriverWait(driver, MED).until(EC.visibility_of_element_located(sel))
        except TimeoutException:
            continue
    return None


def _force_close_date(driver, start_ddmmyyyy: str, end_ddmmyyyy: str):
    driver.execute_script("""
        (function(s, e){
            var from = document.getElementById('hdnRDomesticddf');
            var to   = document.getElementById('hdnRDomesticddt');
            if (from) from.value = s;
            if (to)   to.value   = e;

            // Close-specific guards
            var tt = document.getElementById('hdnTenderType');
            if (tt) tt.value = '4';
            var sb = document.getElementById('hdnSearchBoundary');
            if (sb) sb.value = '4';

            // Update label
            var span = document.querySelector('#drpRegisterUserDD span');
            if (span) span.textContent = s + ' - ' + e;

            // Sync daterangepicker if present
            try {
                if (window.jQuery) {
                    var $ = window.jQuery;
                    var w = $('#drpRegisterUserDD').data('daterangepicker');
                    if (w && w.setStartDate && w.setEndDate) {
                        w.setStartDate(s);
                        w.setEndDate(e);
                    }
                }
            } catch (err) {}
        })(arguments[0], arguments[1]);
    """, start_ddmmyyyy, end_ddmmyyyy)


def _set_hidden_close_dates(driver, start_ddmmyyyy: str, end_ddmmyyyy: str):
    driver.execute_script("""
        (function(s, e){
            var from = document.getElementById('hdnRDomesticddf');
            var to   = document.getElementById('hdnRDomesticddt');
            if (from) from.value = s;
            if (to)   to.value   = e;
            var span = document.querySelector('#drpRegisterUserDD span');
            if (span) span.textContent = s + ' - ' + e;
        })(arguments[0], arguments[1]);
    """, start_ddmmyyyy, end_ddmmyyyy)


def pick_closing_date_range(driver, mode: str, start_date: str = None, end_date: str = None, *, force_close: bool = False):
    def to_ddmmyyyy(dstr):
        return datetime.strptime(dstr, "%Y-%m-%d").strftime("%d/%m/%Y")

    if mode == "today":
        s_iso = e_iso = datetime.now().strftime("%Y-%m-%d")
    else:
        s_iso, e_iso = start_date, end_date

    s_val, e_val = to_ddmmyyyy(s_iso), to_ddmmyyyy(e_iso)

    if force_close:
        _force_close_date(driver, s_val, e_val)
        return

    open_datepicker(driver)
    ui_succeeded = False
    try:
        if mode == "today":
            for xp in (
                "//div[contains(@class,'daterangepicker')]//li[normalize-space()='Today']",
                "//div[contains(@class,'ranges')]//li[normalize-space()='Today']",
            ):
                try:
                    li = driver.find_element(By.XPATH, xp)
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", li)
                    li.click(); ui_succeeded = True; break
                except Exception:
                    continue
        else:
            for xp in (
                "//div[contains(@class,'daterangepicker')]//li[@data-range-key='Custom Range']",
                "//div[contains(@class,'daterangepicker')]//li[normalize-space()='Custom Range']",
            ):
                try:
                    li = driver.find_element(By.XPATH, xp)
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", li)
                    li.click(); break
                except Exception:
                    continue
            for (by, loc), val in [((By.NAME, "daterangepicker_start"), s_val),
                                   ((By.NAME, "daterangepicker_end"), e_val)]:
                try:
                    box = driver.find_element(by, loc)
                    driver.execute_script("arguments[0].value='';", box)
                    box.clear(); box.send_keys(val)
                except Exception:
                    pass
            ui_succeeded = True

        if ui_succeeded:
            for xp in (
                "//div[contains(@class,'daterangepicker')]//button[normalize-space()='Apply']",
                "//div[contains(@class,'daterangepicker')]//button[contains(.,'Apply')]",
                "//div[contains(@class,'daterangepicker')]//button[contains(@class,'apply')]",
            ):
                try:
                    btn = driver.find_element(By.XPATH, xp)
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                        btn.click(); return
                    except Exception:
                        driver.execute_script("arguments[0].click();", btn); return
                except NoSuchElementException:
                    continue
    except Exception:
        pass

    _set_hidden_close_dates(driver, s_val, e_val)


# ---------- NEW: robust Search clicker ----------
def _click_search_any(driver, timeout=LONG):
    """
    Click whatever visible Search button exists on the page.
    Works for Fresh/Close pages.
    """
    candidates = [
        (By.ID, "btnFilterRegisterFreshTender"),
        (By.ID, "btnFilterRegisterCloseTender"),
        (By.ID, "btnRegisterUserFilter"),
        (By.XPATH, "//button[normalize-space()='Search']"),
        (By.XPATH, "//a[normalize-space()='Search']"),
        (By.XPATH, "//input[@type='button' and (translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='search')]"),
        (By.XPATH, "//*[self::button or self::a or self::input][contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'search')]"),
    ]
    for by, loc in candidates:
        try:
            btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((by, loc)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            return True
        except Exception:
            continue
    return False


# ---------- REPLACED: result detection after Search ----------
def click_search_and_detect_results(driver, timeout=LONG):
    """
    Click SEARCH and return True if a download is available, False if no records.
    Handles Fresh/Close pages and multiple UI variants.
    """
    # Click search (robust)
    if not _click_search_any(driver):
        # Fall back to the original Fresh ID once, just in case
        try:
            wait_click(driver, By.ID, "btnFilterRegisterFreshTender")
        except Exception:
            pass

    def _either_condition(d):
        # Any recognizable download control
        download_variants = [
            (By.ID, "anchordownload"),
            (By.ID, "anchordownloadcsv"),
            (By.XPATH, "//a[contains(@href,'download') and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'download')]"),
            (By.XPATH, "//*[self::a or self::button][contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'download')]"),
        ]
        for by, loc in download_variants:
            try:
                el = d.find_element(by, loc)
                if el.is_displayed():
                    return "DOWNLOAD"
            except Exception:
                continue

        # Common 'No record' banners/labels across tabs
        empty_variants = [
            (By.ID, "error"),
            (By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no record')]"),
            (By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no results')]"),
            (By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no data')]"),
        ]
        for by, loc in empty_variants:
            try:
                el = d.find_element(by, loc)
                if el.is_displayed():
                    return "EMPTY"
            except Exception:
                continue

        return False

    try:
        result = WebDriverWait(driver, timeout).until(_either_condition)
    except TimeoutException:
        result = "EMPTY"  # conservative default

    return result == "DOWNLOAD"


def click_download_excel(driver):
    # Support either ID (some pages use anchordownloadcsv)
    for loc in [(By.ID, "anchordownload"), (By.ID, "anchordownloadcsv")]:
        try:
            btn = WebDriverWait(driver, SHORT).until(EC.visibility_of_element_located(loc))
            break
        except Exception:
            btn = None
    if not btn:
        btn = WebDriverWait(driver, LONG).until(EC.visibility_of_element_located((By.ID, "anchordownload")))

    try:
        driver.execute_script("""
            if (document.activeElement) document.activeElement.blur();
            var ta = document.querySelector('.tt-menu, .typeahead, .twitter-typeahead');
            if (ta) { ta.style.display = 'none'; ta.style.visibility = 'hidden'; }
        """)
    except Exception:
        pass
    _scroll_center(driver, btn)
    try:
        WebDriverWait(driver, MED).until(EC.element_to_be_clickable((By.XPATH, "."))); btn.click(); return
    except Exception:
        pass
    try:
        driver.execute_script("arguments[0].click();", btn); return
    except Exception:
        pass
    try:
        driver.execute_script("if (typeof myfunction1==='function'){ myfunction1(); }"); return
    except Exception:
        pass
    raise TimeoutException("Download button could not be clicked (intercepted by overlay/header).")


def download_and_move(driver, dest_dir: str, base_name: str):
    before = time.time()
    click_download_excel(driver)
    _ensure_dir(dest_dir)
    end = time.time() + 120
    while time.time() < end:
        path = _latest_download(BROWSER_DOWNLOAD_DIR, before)
        if path and not (path.endswith(".crdownload") or path.endswith(".part")):
            _, ext = os.path.splitext(path)
            target = os.path.join(dest_dir, f"{base_name}{ext}")
            if os.path.abspath(path) != os.path.abspath(target):
                if os.path.exists(target):
                    os.remove(target)
                shutil.move(path, target)
            return target
        time.sleep(1)
    raise TimeoutException("Download did not appear")


def run_category(driver, slug: str, query_id: str, row_label: str):
    # LIVE (today)
    open_category_view(driver, query_id=query_id, tendertype=2, row_label=row_label)
    pick_closing_date_range(driver, mode="today", force_close=False)
    has_results = click_search_and_detect_results(driver)
    if has_results:
        live_name = f"{slug}_live_{TODAY}"
        live_dest = DEST_FOLDERS[f"{slug}_live"]
        saved_live = download_and_move(driver, live_dest, live_name)
        print(f"Saved: {saved_live}")
    else:
        print(f"No results for {slug} LIVE — skipped download.")
    go_back_to_dashboard(driver)

    # CLOSE (yesterday) — try UI first, then forced hidden-field fallback
    open_category_view(driver, query_id=query_id, tendertype=4, row_label=row_label)

    # Try via UI
    pick_closing_date_range(driver, mode="custom", start_date=YESTERDAY, end_date=YESTERDAY, force_close=False)
    has_results = click_search_and_detect_results(driver)

    # If still no results, try forced hidden-field set
    if not has_results:
        pick_closing_date_range(driver, mode="custom", start_date=YESTERDAY, end_date=YESTERDAY, force_close=True)
        has_results = click_search_and_detect_results(driver)

    if has_results:
        close_name = f"{slug}_close_{TODAY}"
        close_dest = DEST_FOLDERS[f"{slug}_close"]
        saved_close = download_and_move(driver, close_dest, close_name)
        print(f"Saved: {saved_close}")
    else:
        print(f"No results for {slug} CLOSE — skipped download.")
    go_back_to_dashboard(driver)


def run_all_flows():
    # Ensure folders exist
    _ensure_dir(BROWSER_DOWNLOAD_DIR)
    for path in DEST_FOLDERS.values():
        _ensure_dir(path)

    driver = _new_driver(BROWSER_DOWNLOAD_DIR)
    try:
        login(driver)

        # 0) Inbox
        try:
            download_first_inbox_item(driver)
        except Exception as e:
            print(f"Inbox download skipped: {e}")
        go_back_to_dashboard(driver)

        # 1) Water → 2) DI Pipe → 3) Ductile Iron
        for slug in ("water", "di_pipe", "ductile_iron"):
            qid, label = CATEGORIES[slug]
            try:
                run_category(driver, slug=slug, query_id=qid, row_label=label)
            except Exception as e:
                print(f"{slug} flow skipped due to error: {e}")
                go_back_to_dashboard(driver)

        print("Inbox + all categories (live & close) flows completed (with skips if no results).")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    if not os.path.isdir(BASE_DIR) or "OneDrive" not in BASE_DIR:
        raise SystemExit("Please set BASE_DIR to your OneDrive\\Dailydata_tenderdetails path before running.")
    run_all_flows()


# In[ ]:




