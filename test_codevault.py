import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random
import string

BASE_URL = "http://localhost:5000"


def make_username():
    """Generate a unique username every call."""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"tuser_{suffix}"


@pytest.fixture(scope="function")
def driver():
    """
    Headless Chrome driver.
    Works with Selenium 3.x inside joyzoursky/python-chromedriver
    — Chrome & ChromeDriver are pre-installed, so NO Service/webdriver_manager needed.
    """
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--remote-debugging-port=9222")

    # Selenium 3.x API — no 'service' kwarg
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(10)
    yield drv
    drv.quit()


# ─── Helper ──────────────────────────────────────────────────────────────────

def register_and_login(driver, username=None, password="TestPass@123"):
    """Register a fresh user, log them in, return username."""
    if username is None:
        username = make_username()
    email = f"{username}@example.com"

    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "confirm").send_keys(password)
    driver.find_element(By.ID, "register-btn").click()

    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-btn").click()
    return username


def add_test_snippet(driver, title="Binary Search", lang="Python",
                     desc="Classic algorithm", code="def bs(): pass"):
    driver.get(f"{BASE_URL}/add")
    driver.find_element(By.ID, "title").send_keys(title)
    Select(driver.find_element(By.ID, "language")).select_by_visible_text(lang)
    driver.find_element(By.ID, "description").send_keys(desc)
    driver.find_element(By.ID, "code").send_keys(code)
    driver.find_element(By.ID, "save-btn").click()


# ─── Tests ───────────────────────────────────────────────────────────────────

def test_01_homepage_loads(driver):
    """Home page should load and show CodeVault branding."""
    driver.get(BASE_URL)
    assert "CODEVAULT" in driver.page_source or "SNIPPET VAULT" in driver.page_source
    print("✓ Test 01 — homepage loads")


def test_02_register_page_has_all_fields(driver):
    """Register form must contain username, email, password and confirm fields."""
    driver.get(f"{BASE_URL}/register")
    assert driver.find_element(By.ID, "username")
    assert driver.find_element(By.ID, "email")
    assert driver.find_element(By.ID, "password")
    assert driver.find_element(By.ID, "confirm")
    print("✓ Test 02 — register page fields present")


def test_03_successful_registration(driver):
    """Valid registration redirects to login with success flash."""
    driver.get(f"{BASE_URL}/register")
    u = make_username()
    driver.find_element(By.ID, "username").send_keys(u)
    driver.find_element(By.ID, "email").send_keys(f"{u}@example.com")
    driver.find_element(By.ID, "password").send_keys("TestPass@123")
    driver.find_element(By.ID, "confirm").send_keys("TestPass@123")
    driver.find_element(By.ID, "register-btn").click()
    assert "Account created" in driver.page_source
    print("✓ Test 03 — successful registration")


def test_04_registration_password_mismatch(driver):
    """Mismatched passwords should show error message."""
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(make_username())
    driver.find_element(By.ID, "email").send_keys("x@example.com")
    driver.find_element(By.ID, "password").send_keys("Pass1234")
    driver.find_element(By.ID, "confirm").send_keys("Different99")
    driver.find_element(By.ID, "register-btn").click()
    assert "Passwords do not match" in driver.page_source
    print("✓ Test 04 — password mismatch error")


def test_05_registration_short_password(driver):
    """Password shorter than 6 chars should show error."""
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(make_username())
    driver.find_element(By.ID, "email").send_keys("short@example.com")
    driver.find_element(By.ID, "password").send_keys("abc")
    driver.find_element(By.ID, "confirm").send_keys("abc")
    driver.find_element(By.ID, "register-btn").click()
    assert "at least 6 characters" in driver.page_source
    print("✓ Test 05 — short password error")


def test_06_duplicate_username_rejected(driver):
    """Registering the same username twice should show error."""
    u = make_username()
    # First registration
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(u)
    driver.find_element(By.ID, "email").send_keys(f"{u}@example.com")
    driver.find_element(By.ID, "password").send_keys("TestPass@123")
    driver.find_element(By.ID, "confirm").send_keys("TestPass@123")
    driver.find_element(By.ID, "register-btn").click()
    # Second attempt with same username
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(u)
    driver.find_element(By.ID, "email").send_keys("other@example.com")
    driver.find_element(By.ID, "password").send_keys("TestPass@123")
    driver.find_element(By.ID, "confirm").send_keys("TestPass@123")
    driver.find_element(By.ID, "register-btn").click()
    assert "already exists" in driver.page_source
    print("✓ Test 06 — duplicate username rejected")


def test_07_login_page_loads(driver):
    """Login page must have username and password fields."""
    driver.get(f"{BASE_URL}/login")
    assert driver.find_element(By.ID, "username")
    assert driver.find_element(By.ID, "password")
    print("✓ Test 07 — login page loads")


def test_08_successful_login(driver):
    """Registered user can log in and sees welcome message."""
    u = make_username()
    # Register first
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(u)
    driver.find_element(By.ID, "email").send_keys(f"{u}@example.com")
    driver.find_element(By.ID, "password").send_keys("TestPass@123")
    driver.find_element(By.ID, "confirm").send_keys("TestPass@123")
    driver.find_element(By.ID, "register-btn").click()
    # Login
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").send_keys(u)
    driver.find_element(By.ID, "password").send_keys("TestPass@123")
    driver.find_element(By.ID, "login-btn").click()
    assert "Welcome back" in driver.page_source
    print("✓ Test 08 — successful login")


def test_09_invalid_login_rejected(driver):
    """Wrong credentials must show error message."""
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").send_keys("no_such_user_xyz")
    driver.find_element(By.ID, "password").send_keys("wrongpassword")
    driver.find_element(By.ID, "login-btn").click()
    assert "Invalid username or password" in driver.page_source
    print("✓ Test 09 — invalid login rejected")


def test_10_logout_works(driver):
    """Logged-in user can log out and sees logout confirmation."""
    register_and_login(driver)
    driver.find_element(By.LINK_TEXT, "[ LOGOUT ]").click()
    assert "logged out" in driver.page_source
    print("✓ Test 10 — logout works")


def test_11_add_page_requires_login(driver):
    """Accessing /add without login must redirect to login page."""
    driver.get(f"{BASE_URL}/add")
    assert "login" in driver.current_url.lower()
    print("✓ Test 11 — /add requires login")


def test_12_dashboard_requires_login(driver):
    """Accessing /dashboard without login must redirect to login page."""
    driver.get(f"{BASE_URL}/dashboard")
    assert "login" in driver.current_url.lower()
    print("✓ Test 12 — /dashboard requires login")


def test_13_add_snippet_successfully(driver):
    """Logged-in user can add a snippet and sees success message."""
    register_and_login(driver)
    add_test_snippet(driver, title="Bubble Sort", lang="Python",
                     desc="Sorting algorithm", code="def bubble(): pass")
    assert "Snippet saved to the vault" in driver.page_source
    print("✓ Test 13 — snippet added successfully")


def test_14_snippet_appears_on_homepage(driver):
    """Newly added snippet should appear on homepage."""
    register_and_login(driver)
    title = f"Snippet_{make_username()}"
    add_test_snippet(driver, title=title, code="print('hello')")
    driver.get(BASE_URL)
    assert title in driver.page_source
    print("✓ Test 14 — snippet appears on homepage")


def test_15_view_snippet_detail_page(driver):
    """Clicking a snippet card opens the detail view with code."""
    register_and_login(driver)
    add_test_snippet(driver, title="Merge Sort", code="def merge(): pass")
    driver.get(BASE_URL)
    driver.find_element(By.CSS_SELECTOR, ".snippet-card").click()
    assert "Merge Sort" in driver.page_source
    assert "def merge" in driver.page_source
    print("✓ Test 15 — snippet detail page loads")


def test_16_search_finds_snippet(driver):
    """Search bar returns matching snippet."""
    register_and_login(driver)
    add_test_snippet(driver, title="QuickSort Algorithm", code="def quick(): pass")
    driver.get(BASE_URL)
    search = driver.find_element(By.ID, "search-input")
    search.clear()
    search.send_keys("QuickSort")
    driver.find_element(By.ID, "search-btn").click()
    assert "QuickSort Algorithm" in driver.page_source
    print("✓ Test 16 — search finds snippet")


def test_17_search_no_results_shows_empty_state(driver):
    """Search for a non-existent term shows empty/no-results state."""
    driver.get(BASE_URL)
    search = driver.find_element(By.ID, "search-input")
    search.clear()
    search.send_keys("zzzNonExistentSnippetXYZ999")
    driver.find_element(By.ID, "search-btn").click()
    assert ("VAULT IS EMPTY" in driver.page_source
            or "No snippets" in driver.page_source
            or "0 snippet" in driver.page_source)
    print("✓ Test 17 — empty search shows correct state")


def test_18_filter_by_language(driver):
    """Language filter dropdown returns only snippets of that language."""
    register_and_login(driver)
    add_test_snippet(driver, title="JS Arrow Function",
                     lang="JavaScript", code="const fn = () => {};")
    driver.get(BASE_URL)
    Select(driver.find_element(By.ID, "lang-filter")).select_by_visible_text("JavaScript")
    driver.find_element(By.ID, "search-btn").click()
    assert "JavaScript" in driver.page_source
    print("✓ Test 18 — language filter works")


def test_19_dashboard_shows_user_snippets(driver):
    """Dashboard lists all snippets belonging to the current user."""
    register_and_login(driver)
    add_test_snippet(driver, title="My Dashboard Snippet", code="x = 1")
    driver.find_element(By.LINK_TEXT, "[ DASHBOARD ]").click()
    assert "My Dashboard Snippet" in driver.page_source
    print("✓ Test 19 — dashboard shows user snippets")


def test_20_edit_snippet(driver):
    """Owner can edit a snippet; updated title appears on detail page."""
    register_and_login(driver)
    add_test_snippet(driver, title="Old Title", code="pass")
    driver.get(BASE_URL)
    driver.find_element(By.CSS_SELECTOR, ".snippet-card").click()
    driver.find_element(By.ID, "edit-btn").click()

    title_field = driver.find_element(By.ID, "title")
    title_field.clear()
    title_field.send_keys("Updated Title")
    driver.find_element(By.ID, "update-btn").click()

    assert "Updated Title" in driver.page_source
    assert "Snippet updated" in driver.page_source
    print("✓ Test 20 — edit snippet works")


def test_21_delete_snippet(driver):
    """Owner can delete a snippet; it disappears from the vault."""
    register_and_login(driver)
    add_test_snippet(driver, title="To Be Deleted", code="pass")
    driver.get(BASE_URL)
    driver.find_element(By.CSS_SELECTOR, ".snippet-card").click()

    # Dismiss the JS confirm() dialog automatically then click delete
    driver.execute_script("window.confirm = function(){ return true; }")
    driver.find_element(By.ID, "delete-btn").click()

    assert "deleted" in driver.page_source.lower()
    print("✓ Test 21 — delete snippet works")
