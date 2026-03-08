#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# t247_login_and_download_today_excel.py
# -*- coding: utf-8 -*-

import os, time, glob, re, shutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, ElementClickInterceptedException, NoSuchElementException,
    InvalidSessionIdException, WebDriverException
)

# ----------------- Config -----------------
URL_KEYWORD     = "https://www.tender247.com/keyword/dakra+tenders"
URL_TENDER      = "https://www.tender247.com/auth/tender"
URL_RESULT      = "https://www.tender247.com/auth/result"
URL_BOQ_TENDER  = "https://www.tender247.com/auth/userboq/boq-tender"
URL_BOQ_RESULT  = "https://www.tender247.com/auth/userboq/boq-result"

EMAIL    = os.getenv("T247_EMAIL", "diptender@rashmigroup.com")
PASSWORD = os.getenv("T247_PASSWORD", "Rashmi@2025")

BASE_DIR        = r"D:\Tender247_Live_Data_Extract"
TENDER_DIR      = os.path.join(BASE_DIR, "Tender")
RESULT_DIR      = os.path.join(BASE_DIR, "Result")
BOQ_TENDER_DIR  = os.path.join(BASE_DIR, "BOQ", "Tender")
BOQ_RESULT_DIR  = os.path.join(BASE_DIR, "BOQ", "Result")

WAIT_SECS = 30
# ------------------------------------------

def mkdirs():
    for p in (TENDER_DIR, RESULT_DIR, BOQ_TENDER_DIR, BOQ_RESULT_DIR):
        os.makedirs(p, exist_ok=True)

def build_driver(download_dir: str):
    mkdirs()
    opts = uc.ChromeOptions()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
    }
    opts.add_experimental_option("prefs", prefs)
    driver = uc.Chrome(options=opts)
    try:
        driver.set_page_load_timeout(90)
    except Exception:
        pass
    set_download_dir(driver, TENDER_DIR)
    return driver

def set_download_dir(driver, folder: str):
    os.makedirs(folder, exist_ok=True)
    try:
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": folder})
    except Exception as e:
        print(f"[!] Could not switch download folder via CDP: {e}")

def is_visible(el):
    try:
        return el.is_displayed() and el.value_of_css_property("visibility") != "hidden" and el.value_of_css_property("opacity") != "0"
    except Exception:
        return False

def scroll_then_safe_click(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.15)
    try:
        el.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", el)

def js_set_value(driver, el, value: str):
    driver.execute_script("""
        const el = arguments[0], v = arguments[1];
        const s = Object.getOwnPropertyDescriptor(el.__proto__, 'value')?.set;
        if (s) s.call(el, v); else el.value = v;
        el.dispatchEvent(new Event('input', {bubbles:true}));
        el.dispatchEvent(new Event('change', {bubbles:true}));
    """, el, value)

def newest_file_in(folder: str):
    files = [p for p in glob.glob(os.path.join(folder, "*")) if os.path.isfile(p)]
    return max(files, key=os.path.getmtime) if files else None

def wait_for_download(folder: str, start_marker: float, timeout: int = 180):
    end = time.time() + timeout
    while time.time() < end:
        cand = newest_file_in(folder)
        if cand and os.path.getmtime(cand) >= start_marker:
            if cand.endswith(".crdownload") or os.path.exists(cand + ".crdownload"):
                time.sleep(0.4); continue
            if not any(p.startswith(cand) and p.endswith(".crdownload") for p in glob.glob(os.path.join(folder, "*.crdownload"))):
                return cand
        time.sleep(0.4)
    return None

def rename_boq_file(path: str, label: str):
    if not path: return path
    dirname, fname = os.path.dirname(path), os.path.basename(path)
    tag_map = {"water":"Water", "di pipe":"DI_Pipe", "ductile iron":"Ductile_Iron"}
    tag = tag_map.get(label.lower().strip(), label.replace(" ", "_"))
    new = re.sub(r"\((\d{2}-\d{2}-\d{4})\)\.xlsx$", rf"{tag}_(\1).xlsx", fname)
    if new == fname:
        root, ext = os.path.splitext(fname)
        new = f"{root}-{tag}{ext}"
    new_path = os.path.join(dirname, new)
    try:
        os.replace(path, new_path)
        return new_path
    except Exception:
        try:
            shutil.copy2(path, new_path); os.remove(path)
            return new_path
        except Exception:
            return path

# ---------- Login ----------
def get_visible_login_dialog(driver, timeout=2):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@role='dialog' and .//h2[normalize-space()='Login']]"))
        )
    except TimeoutException:
        return None

def click_signup_login_header(wait):
    triggers = [
        "//button[@aria-haspopup='dialog' and contains(normalize-space(.), 'Sign Up') and contains(normalize-space(.), 'log in')]",
        "//button[normalize-space(.)='Sign Up/log in']",
        "//button[normalize-space(.)='Login']",
        "//a[normalize-space(.)='Login']",
    ]
    for xp in triggers:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            btn.click()
            return True
        except ElementClickInterceptedException:
            return True
        except TimeoutException:
            continue
    return False

def ensure_login_dialog(driver, wait):
    dlg = get_visible_login_dialog(driver, timeout=2)
    if dlg:
        return dlg
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept') or contains(., 'Agree') or contains(translate(.,'ACEPT','acept'),'accept')]"))
        ).click()
    except TimeoutException:
        pass
    if not click_signup_login_header(wait):
        raise TimeoutException("Couldn't click the 'Sign Up/log in' button")
    dlg = get_visible_login_dialog(driver, timeout=12)
    if not dlg:
        driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        if not click_signup_login_header(wait):
            raise TimeoutException("Login dialog didn't open after clicking trigger.")
        dlg = get_visible_login_dialog(driver, timeout=8)
    if not dlg:
        raise TimeoutException("Login dialog not visible.")
    return dlg

def ensure_login_tab(dlg):
    if dlg.find_elements(By.XPATH, ".//h2[normalize-space()='Login']"):
        return
    for xp in [".//button[normalize-space(.)='Login']", ".//button[normalize-space(.)='Log in']"]:
        for b in dlg.find_elements(By.XPATH, xp):
            if is_visible(b):
                b.click(); time.sleep(0.2); return

def fill_and_submit(driver, dlg, email, password):
    def find_input(name, placeholder=None):
        cand = [e for e in dlg.find_elements(By.NAME, name) if is_visible(e)]
        if cand: return cand[0]
        if placeholder:
            try:
                e = dlg.find_element(By.XPATH, f".//input[@placeholder={placeholder!r}]")
                if is_visible(e): return e
            except NoSuchElementException:
                pass
        return None
    ensure_login_tab(dlg)
    email_el = find_input("emailId", "Email Id*")
    pass_el  = find_input("password", "Password*")
    if not email_el or not pass_el:
        raise TimeoutException("Email/password inputs not visible in Login dialog.")
    for el, val in ((email_el, email), (pass_el, password)):
        el.click()
        try: el.clear()
        except Exception: pass
        js_set_value(driver, el, val)
    btns = [b for b in dlg.find_elements(By.XPATH, ".//button[@type='submit' or normalize-space(.)='Submit']") if is_visible(b)]
    if not btns:
        raise TimeoutException("Submit button not found.")
    try:
        btns[0].click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", btns[0])

def wait_for_success(driver, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        dialogs = driver.find_elements(By.XPATH, "//div[@role='dialog' and .//h2[normalize-space()='Login']]")
        if not any(is_visible(d) for d in dialogs):
            return True
        if driver.find_elements(By.XPATH, "//*[contains(., 'Logout') or contains(., 'My Account') or contains(., 'Dashboard')]"):
            return True
        time.sleep(0.3)
    return False

def robust_login(download_dir):
    attempts = 2
    last_e = None
    for i in range(1, attempts + 1):
        try:
            driver = build_driver(download_dir)
            wait = WebDriverWait(driver, WAIT_SECS)
            driver.get(URL_KEYWORD)
            time.sleep(2)
            dlg = ensure_login_dialog(driver, wait)
            fill_and_submit(driver, dlg, EMAIL, PASSWORD)
            if wait_for_success(driver, 30):
                print(f"[OK] Logged in as {EMAIL}")
                return driver, wait
            else:
                print("[-] Login not detected. Retrying fresh browser…")
                try: driver.quit()
                except: pass
        except (InvalidSessionIdException, WebDriverException) as e:
            last_e = e
            print(f"[!] Browser/session issue on attempt {i}: {e.__class__.__name__}. Restarting…")
            try: driver.quit()
            except: pass
            time.sleep(1.5)
        except Exception as e:
            last_e = e
            print(f"[x] Unexpected error on attempt {i}: {e}. Restarting…")
            try: driver.quit()
            except: pass
            time.sleep(1.0)
    raise RuntimeError(f"Could not start browser & login after {attempts} attempts. Last error: {last_e}")

# ---------- Tender ----------
def go_to_indian_tenders(driver, wait):
    driver.get(URL_TENDER)
    try:
        indian_tab = WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Indian']"))
        )
        if is_visible(indian_tab):
            scroll_then_safe_click(driver, indian_tab)
    except TimeoutException:
        pass
    WebDriverWait(driver, WAIT_SECS).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Today Tenders')]"))
    )

def click_today_tenders_excel(driver, wait):
    for xp in [
        "//*[contains(normalize-space(.),'Today Tenders')]//img[@alt='Download Excel']",
        "//*[contains(normalize-space(.),'Today Tenders')]//img[contains(@src,'download-excel')]",
        "(//img[@alt='Download Excel' or contains(@src,'download-excel')])[1]",
    ]:
        try:
            el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xp)))
            scroll_then_safe_click(driver, el); return True
        except TimeoutException:
            continue
    return False

# ---------- Result ----------
def ensure_result_menu_open_and_indian_selected(driver, wait):
    try:
        res_li = WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.XPATH, "//li[.//span[contains(normalize-space(.),'Result')]]"))
        )
        scroll_then_safe_click(driver, res_li); time.sleep(0.2)
    except TimeoutException:
        pass
    try:
        indian_link = WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/auth/result' and contains(normalize-space(.),'Indian')]"))
        )
        scroll_then_safe_click(driver, indian_link); time.sleep(0.2)
    except TimeoutException:
        pass

def go_to_indian_results(driver, wait):
    driver.get(URL_RESULT)
    WebDriverWait(driver, WAIT_SECS).until(EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(.),'Result')]")))
    ensure_result_menu_open_and_indian_selected(driver, wait)
    WebDriverWait(driver, WAIT_SECS).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Today Results')]")))

def click_today_results_tile(driver, wait):
    for xp in [
        "//div[contains(@class,'cursor-pointer')][.//p[normalize-space()='Today Results'] or .//img[@alt='Today Results']]",
        "//*[contains(@class,'cursor-pointer') and .//*[contains(normalize-space(),'Today Results')]]",
    ]:
        try:
            el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xp)))
            scroll_then_safe_click(driver, el); time.sleep(0.4); return True
        except TimeoutException:
            continue
    return False

def click_today_results_excel(driver, wait):
    for xp in [
        "//*[.//p[normalize-space()='Today Results'] or .//img[@alt='Today Results'] or .//div[contains(normalize-space(),'Today Results')]]//span[.//img[@alt='Download Excel']]",
        "//span[.//img[@alt='Download Excel']]",
        "//img[@alt='Download Excel']",
    ]:
        try:
            t = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xp)))
            if t.tag_name.lower() == "img":
                try:
                    t = t.find_element(By.XPATH, "./ancestor::*[self::span or self::button][1]")
                except Exception:
                    pass
            scroll_then_safe_click(driver, t); return True
        except TimeoutException:
            continue
    return False

# ---------- BOQ Result ----------
def go_to_boq_result(driver, wait):
    driver.get(URL_BOQ_RESULT)
    WebDriverWait(driver, WAIT_SECS).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Today BOQ') or contains(normalize-space(),'BOQ')]"))
    )
    for xp in [
        "//div[contains(@class,'cursor-pointer') and .//p[contains(normalize-space(),'Today BOQ')]]",
        "//div[contains(@class,'cursor-pointer') and .//img[@alt='TodayTenders']]",
        "//*[contains(@class,'cursor-pointer') and .//*[contains(normalize-space(),'Today BOQ')]]",
    ]:
        try:
            el = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, xp)))
            scroll_then_safe_click(driver, el)
            time.sleep(0.6)
            break
        except TimeoutException:
            continue

def click_boq_result_excel(driver, wait):
    for xp in [
        "//*[.//p[contains(normalize-space(),'Today BOQ')] or .//p[contains(normalize-space(),'Today Results')]]//img[@alt='Download Excel']",
        "//span[.//img[@alt='Download Excel']]",
        "//img[@alt='Download Excel']",
    ]:
        try:
            n = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xp)))
            if n.tag_name.lower() == "img":
                try:
                    n = n.find_element(By.XPATH, "./ancestor::*[self::span or self::button][1]")
                except Exception:
                    pass
            scroll_then_safe_click(driver, n); return True
        except TimeoutException:
            continue
    return False

# ---------- BOQ Tender: page + helpers ----------
def go_to_boq_tender(driver, wait):
    driver.get(URL_BOQ_TENDER)
    WebDriverWait(driver, WAIT_SECS).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Today BOQ') or contains(normalize-space(),'Tender BOQ')]"))
    )
    for xp in [
        "//div[contains(@class,'cursor-pointer') and .//p[contains(normalize-space(),'Today BOQ')]]",
        "//div[contains(@class,'cursor-pointer') and .//img[@alt='TodayTenders']]",
        "//*[contains(@class,'cursor-pointer') and .//*[contains(normalize-space(),'Today BOQ')]]",
    ]:
        try:
            tile = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, xp)))
            scroll_then_safe_click(driver, tile)
            time.sleep(0.6)
            break
        except TimeoutException:
            continue

# --- NEW: inline accordion opener for "Tender BOQ Search" ---
def open_inline_tender_boq_search(driver):
    """
    Ensures the 'Tender BOQ Search' section is expanded and returns its panel element.
    """
    # Target the H2 header with text 'Tender BOQ Search'
    hdr = WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.XPATH, "//h2[.//span[normalize-space()='Tender BOQ Search']]"))
    )
    scroll_then_safe_click(driver, hdr)
    time.sleep(0.4)

    # The panel is the immediate following sibling div
    panel = hdr.find_element(By.XPATH, "./following-sibling::div[1]")

    # If still hidden (class has 'hidden' or 'opacity-0' / 'max-h-0'), toggle once more
    def _panel_visible(p):
        try:
            cls = (p.get_attribute("class") or "").lower()
            return p.is_displayed() and ('hidden' not in cls) and ('opacity-0' not in cls) and ('max-h-0' not in cls)
        except Exception:
            return False

    if not _panel_visible(panel):
        scroll_then_safe_click(driver, hdr)
        time.sleep(0.5)

    # As a last resort, force-show via JS if present but still collapsed
    if not _panel_visible(panel):
        try:
            driver.execute_script("""
                const p = arguments[0];
                p.classList.remove('hidden','opacity-0');
                p.style.maxHeight = 'unset';
                p.style.opacity = '1';
                p.style.display = 'block';
            """, panel)
            time.sleep(0.3)
        except Exception:
            pass

    # Sanity: verify inputs exist and are interactable
    try:
        inpt = panel.find_element(By.XPATH, ".//input[@placeholder='Search BOQ / Raw Material']")
        if not inpt.is_displayed():
            raise Exception("Inline input not visible yet.")
    except Exception:
        # Try one more click on header if needed
        try:
            scroll_then_safe_click(driver, hdr); time.sleep(0.4)
        except Exception:
            pass

    return panel

# Drawer helpers (kept as fallback)
def _drawer_el(driver):
    try:
        return driver.find_element(By.XPATH, "//div[contains(@class,'fixed') and contains(@class,'right-0') and contains(@class,'shadow-xl')]")
    except Exception:
        return None

def _drawer_visible(drawer):
    try:
        cls = drawer.get_attribute("class") or ""
        if "translate-x-full" in cls or "w-0" in cls:
            return False
        return drawer.is_displayed()
    except Exception:
        return False

def _force_open_drawer(driver, drawer):
    try:
        driver.execute_script("""
            const d = arguments[0];
            d.classList.remove('translate-x-full');
            d.style.transform = 'translateX(0)';
            let p = d.parentElement;
            if (p && p.classList.contains('w-0')) p.classList.remove('w-0');
        """, drawer)
        time.sleep(0.4)
    except Exception:
        pass

def open_boq_tender_filter(driver):
    dr = _drawer_el(driver)
    if dr and _drawer_visible(dr):
        return dr
    for xp in [
        "//svg[contains(@class,'lucide-chevron-down') and contains(@class,'float-right')]",
        "//*[contains(normalize-space(),'Filter')]/following::*[name()='svg' and contains(@class,'lucide-chevron-down')][1]",
    ]:
        try:
            svg = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xp)))
            scroll_then_safe_click(driver, svg); time.sleep(0.6)
            dr = _drawer_el(driver)
            if dr and _drawer_visible(dr):
                return dr
        except TimeoutException:
            continue
    # Fallback: try force open if exists
    dr = _drawer_el(driver)
    if dr and not _drawer_visible(dr):
        print("   [!] Forcing BOQ filter drawer open via JS…")
        _force_open_drawer(driver, dr)
        if _drawer_visible(dr):
            return dr
    return None

def close_boq_tender_filter(panel):
    try:
        close_btn = panel.find_element(By.XPATH, ".//button[normalize-space()='×' or @aria-label='Close']")
        scroll_then_safe_click(driver=panel.parent, el=close_btn)  # type: ignore
        time.sleep(0.25)
    except Exception:
        pass

def _type_into(el, text, driver=None):
    if driver:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    el.click()
    try: el.clear()
    except Exception: pass
    el.send_keys(text)

# ---------- Scope selection ----------
def find_boq_filter_scope(driver):
    """
    Prefer the inline 'Tender BOQ Search' accordion panel.
    If not present/expandable, fall back to the side drawer panel.
    """
    try:
        panel = open_inline_tender_boq_search(driver)
        if panel and panel.is_displayed():
            return ("inline", panel)
    except Exception:
        pass

    # Drawer fallback
    dr = open_boq_tender_filter(driver)
    if dr and _drawer_visible(dr):
        return ("drawer", dr)

    return (None, None)

# ---------- Fill + Search (works for both inline panel and drawer) ----------
def click_search_in_scope(scope, driver):
    # Scope-local SEARCH and also page-level fallback
    for xp in [
        ".//button[translate(normalize-space(.),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')='SEARCH']",
        ".//button[normalize-space()='SEARCH']",
    ]:
        try:
            btn = scope.find_element(By.XPATH, xp)
            scroll_then_safe_click(driver, btn)
            return True
        except Exception:
            continue
    # Inline section sometimes has SEARCH just below — try nearby:
    try:
        btn = driver.find_element(By.XPATH, "//button[normalize-space()='SEARCH']")
        scroll_then_safe_click(driver, btn)
        return True
    except Exception:
        return False

def fill_boq_filters_and_search(scope_kind, scope_el, driver, keyword, min_lakh=None, exact=True):
    # 1) Keyword
    ws = None
    for xp in [
        ".//input[@placeholder='Search BOQ / Raw Material']",
        ".//input[@placeholder='Word Search']",
    ]:
        try:
            ws = scope_el.find_element(By.XPATH, xp)
            break
        except Exception:
            continue
    if not ws:
        print("   [!] Could not find 'Search BOQ / Raw Material' / 'Word Search' input in scope.")
        return False
    _type_into(ws, keyword, driver)

    # 2) Optional: Search Within (drawer has it sometimes)
    try:
        sw = scope_el.find_element(By.XPATH, ".//input[@placeholder='Search Within']")
        _type_into(sw, keyword, driver)
    except Exception:
        pass

    # 3) Exact Search (drawer only; inline does not show it)
    if exact:
        try:
            chk = scope_el.find_element(By.XPATH, ".//button[@role='checkbox' and @id='exactsarch']")
            if (chk.get_attribute("data-state") or "").lower() != "checked":
                scroll_then_safe_click(driver, chk)
        except Exception:
            pass

    # 4) Tender Value (>= … Lakh)
    if min_lakh is not None:
        val = None
        for xp in [
            ".//input[@type='number' and (@placeholder='Value' or contains(@placeholder,'Value'))]",
        ]:
            try:
                val = scope_el.find_element(By.XPATH, xp)
                break
            except Exception:
                continue
        if val:
            _type_into(val, str(min_lakh), driver)
        else:
            print("   [i] Tender Value input not found; continuing.")

    # 5) SEARCH
    if not click_search_in_scope(scope_el, driver):
        print("   [!] SEARCH button not found in scope.")
        return False

    time.sleep(1.2)
    return True

def click_boq_tender_excel(driver, wait):
    # Wait for a Download Excel to appear after search
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//img[@alt='Download Excel' and contains(@src,'download-excel')]"))
        )
    except TimeoutException:
        pass

    for xp in [
        "(//img[@alt='Download Excel' and contains(@src,'download-excel')])[1]",
        "(//span[.//img[@alt='Download Excel' and contains(@src,'download-excel')]])[1]",
        "//img[@alt='Download Excel' and contains(@src,'download-excel')]",
    ]:
        try:
            n = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, xp)))
            if n.tag_name.lower() == "img":
                try:
                    n = n.find_element(By.XPATH, "./ancestor::*[self::span or self::button or self::a][1]")
                except Exception:
                    pass
            scroll_then_safe_click(driver, n)
            return True
        except TimeoutException:
            continue
    return False

def do_boq_tender_keyword(driver, wait, keyword: str, value_min_lakh=None, label=None, _retry=False):
    try:
        print(f"[*] BOQ Tender → '{keyword}' (within='{keyword}', exact=True, min_lakh={value_min_lakh})")
        go_to_boq_tender(driver, wait)

        scope_kind, scope_el = find_boq_filter_scope(driver)
        if not scope_el:
            print("[-] BOQ Tender: Could not open inline/drawer filters.")
            return None

        ok = fill_boq_filters_and_search(scope_kind, scope_el, driver, keyword, value_min_lakh, exact=True)
        if not ok:
            print("[-] BOQ Tender: Could not fill/search filters.")
            return None

        # If drawer used, try to close (so results area is clickable)
        if scope_kind == "drawer":
            try: close_boq_tender_filter(scope_el)
            except Exception: pass
            time.sleep(0.3)

        click_t = time.time()
        if not click_boq_tender_excel(driver, wait):
            print("[-] BOQ Tender: Download Excel icon not found.")
            return None

        fpath = wait_for_download(BOQ_TENDER_DIR, start_marker=click_t, timeout=180)
        if not fpath:
            print("[-] BOQ Tender: No file detected after clicking Excel.")
            return None

        final = rename_boq_file(fpath, label or keyword)
        print(f"[✓] BOQ Tender Excel: {final}")
        return final

    except (InvalidSessionIdException, WebDriverException) as e:
        msg = str(e).lower()
        if (("invalid session id" in msg or "disconnected" in msg) and not _retry):
            print("[!] Chrome session dropped during BOQ Tender. Recovering…")
            new_driver, new_wait = restart_and_relogin(download_dir=BOQ_TENDER_DIR)
            return do_boq_tender_keyword(new_driver, new_wait, keyword, value_min_lakh, label, _retry=True)
        else:
            print(f"[x] BOQ Tender unrecoverable error: {e}")
            return None

# ---------- Restart helper ----------
def restart_and_relogin(download_dir):
    driver = build_driver(download_dir)
    wait = WebDriverWait(driver, WAIT_SECS)
    driver.get(URL_KEYWORD)
    time.sleep(2)
    dlg = ensure_login_dialog(driver, wait)
    fill_and_submit(driver, dlg, EMAIL, PASSWORD)
    if not wait_for_success(driver, 30):
        print("❌ Re-login failed.")
    else:
        print("[OK] Re-login successful.")
    set_download_dir(driver, download_dir)
    return driver, wait

# ----------------- MAIN -----------------
def main():
    print("[*] Tender dir:", TENDER_DIR)
    print("[*] Result dir:", RESULT_DIR)
    print("[*] BOQ Tender dir:", BOQ_TENDER_DIR)
    print("[*] BOQ Result dir:", BOQ_RESULT_DIR)

    driver, wait = robust_login(TENDER_DIR)

    try:
        # TENDER
        go_to_indian_tenders(driver, wait)
        t0 = time.time()
        if click_today_tenders_excel(driver, wait):
            tf = wait_for_download(TENDER_DIR, t0, 180)
            if tf: print(f"[✓] Tender Excel: {tf}")
            else:  print("[-] Tender: no file detected.")
        else:
            print("[-] Tender: download icon not found.")

        # RESULT
        set_download_dir(driver, RESULT_DIR)
        go_to_indian_results(driver, wait)
        click_today_results_tile(driver, wait)
        r0 = time.time()
        if click_today_results_excel(driver, wait):
            rf = wait_for_download(RESULT_DIR, r0, 180)
            if rf: print(f"[✓] Result Excel: {rf}")
            else:  print("[-] Result: no file detected.")
        else:
            print("[-] Result: download icon not found.")

        # BOQ RESULT
        set_download_dir(driver, BOQ_RESULT_DIR)
        go_to_boq_result(driver, wait)
        b0 = time.time()
        if click_boq_result_excel(driver, wait):
            br = wait_for_download(BOQ_RESULT_DIR, b0, 180)
            if br: print(f"[✓] BOQ Result Excel: {br}")
            else:  print("[-] BOQ Result: no file detected.")
        else:
            print("[-] BOQ Result: download icon not found.")

        # BOQ TENDER (Water ≥ 40 Lakh, DI Pipe, Ductile Iron)
        set_download_dir(driver, BOQ_TENDER_DIR)
        do_boq_tender_keyword(driver, wait, keyword="water",        value_min_lakh=40,  label="Water")
        do_boq_tender_keyword(driver, wait, keyword="di pipe",      value_min_lakh=None, label="DI_Pipe")
        do_boq_tender_keyword(driver, wait, keyword="ductile iron", value_min_lakh=None, label="Ductile_Iron")

        print("ℹ️ Window will stay open. Close Chrome when you're done, or press Ctrl+C here.")
        while True:
            try:
                if not driver.window_handles: break
                time.sleep(1)
            except Exception:
                break

    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user.")
    finally:
        try: driver.quit()
        except Exception: pass

if __name__ == "__main__":
    main()


# In[ ]:




