import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random

class TestCodeVault:
    
    @pytest.fixture
    def driver(self):
        """Setup headless Chrome driver for Jenkins"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        driver.quit()
    
    def generate_unique_username(self):
        return f"testuser_{int(time.time())}_{random.randint(1000, 9999)}"
    
    def test_01_homepage_loads(self, driver):
        driver.get("http://localhost:5000")
        assert "CODEVAULT" in driver.page_source or "SNIPPET VAULT" in driver.page_source
        print("✓ Test 1 passed")
    
    def test_02_register_page_loads(self, driver):
        driver.get("http://localhost:5000/register")
        assert driver.find_element(By.ID, "username")
        assert driver.find_element(By.ID, "email")
        assert driver.find_element(By.ID, "password")
        assert driver.find_element(By.ID, "confirm")
        print("✓ Test 2 passed")
    
    def test_03_successful_registration(self, driver):
        driver.get("http://localhost:5000/register")
        username = self.generate_unique_username()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        assert "Account created" in driver.page_source
        print("✓ Test 3 passed")
    
    def test_04_registration_password_mismatch(self, driver):
        driver.get("http://localhost:5000/register")
        driver.find_element(By.ID, "username").send_keys("testuser")
        driver.find_element(By.ID, "email").send_keys("test@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.ID, "confirm").send_keys("different123")
        driver.find_element(By.ID, "register-btn").click()
        assert "Passwords do not match" in driver.page_source
        print("✓ Test 4 passed")
    
    def test_05_registration_duplicate_user(self, driver):
        driver.get("http://localhost:5000/register")
        username = "duplicate_test_user"
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        driver.get("http://localhost:5000/register")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys("different@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        assert "Username or email already exists" in driver.page_source
        print("✓ Test 5 passed")
    
    def test_06_login_page_loads(self, driver):
        driver.get("http://localhost:5000/login")
        assert driver.find_element(By.ID, "username")
        assert driver.find_element(By.ID, "password")
        print("✓ Test 6 passed")
    
    def test_07_successful_login(self, driver):
        driver.get("http://localhost:5000/register")
        username = self.generate_unique_username()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        driver.get("http://localhost:5000/login")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "login-btn").click()
        assert f"Welcome back, {username}" in driver.page_source
        print("✓ Test 7 passed")
    
    def test_08_login_invalid_credentials(self, driver):
        driver.get("http://localhost:5000/login")
        driver.find_element(By.ID, "username").send_keys("nonexistent_user")
        driver.find_element(By.ID, "password").send_keys("wrongpassword")
        driver.find_element(By.ID, "login-btn").click()
        assert "Invalid username or password" in driver.page_source
        print("✓ Test 8 passed")
    
    def test_09_logout_functionality(self, driver):
        driver.get("http://localhost:5000/register")
        username = self.generate_unique_username()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        driver.get("http://localhost:5000/login")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "login-btn").click()
        driver.find_element(By.LINK_TEXT, "[ LOGOUT ]").click()
        assert "You have been logged out" in driver.page_source
        print("✓ Test 9 passed")
    
    def test_10_add_snippet_requires_login(self, driver):
        driver.get("http://localhost:5000/add")
        assert "login" in driver.current_url
        print("✓ Test 10 passed")
    
    def test_11_add_snippet_successfully(self, driver):
        driver.get("http://localhost:5000/register")
        username = self.generate_unique_username()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        driver.get("http://localhost:5000/login")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "login-btn").click()
        driver.get("http://localhost:5000/add")
        driver.find_element(By.ID, "title").send_keys("Binary Search in Python")
        driver.find_element(By.ID, "language").send_keys("Python")
        driver.find_element(By.ID, "code").send_keys("def binary_search(arr, target):\n    left, right = 0, len(arr)-1\n    while left <= right:\n        mid = (left+right)//2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid+1\n        else:\n            right = mid-1\n    return -1")
        driver.find_element(By.ID, "save-btn").click()
        assert "Snippet saved to the vault" in driver.page_source
        print("✓ Test 11 passed")
    
    def test_12_view_snippet_details(self, driver):
        self.test_11_add_snippet_successfully(driver)
        driver.get("http://localhost:5000")
        driver.find_element(By.CSS_SELECTOR, ".snippet-card").click()
        assert "Binary Search in Python" in driver.page_source
        print("✓ Test 12 passed")
    
    def test_13_search_snippets(self, driver):
        self.test_11_add_snippet_successfully(driver)
        driver.get("http://localhost:5000")
        driver.find_element(By.ID, "search-input").send_keys("Binary Search")
        driver.find_element(By.ID, "search-input").send_keys(Keys.RETURN)
        assert "Binary Search in Python" in driver.page_source
        print("✓ Test 13 passed")
    
    def test_14_filter_by_language(self, driver):
        self.test_11_add_snippet_successfully(driver)
        driver.get("http://localhost:5000")
        driver.find_element(By.ID, "lang-filter").send_keys("Python")
        driver.find_element(By.ID, "search-btn").click()
        assert "Python" in driver.page_source
        print("✓ Test 14 passed")
    
    def test_15_empty_search_shows_message(self, driver):
        driver.get("http://localhost:5000")
        driver.find_element(By.ID, "search-input").send_keys("xyz_nonexistent_snippet_12345")
        driver.find_element(By.ID, "search-input").send_keys(Keys.RETURN)
        assert "No snippets match" in driver.page_source or "VAULT IS EMPTY" in driver.page_source
        print("✓ Test 15 passed")
    
    def test_16_dashboard_requires_login(self, driver):
        driver.get("http://localhost:5000/dashboard")
        assert "login" in driver.current_url
        print("✓ Test 16 passed")
    
    def test_17_dashboard_shows_user_snippets(self, driver):
        self.test_11_add_snippet_successfully(driver)
        driver.find_element(By.LINK_TEXT, "[ DASHBOARD ]").click()
        assert "Binary Search in Python" in driver.page_source
        print("✓ Test 17 passed")
    
    def test_18_edit_snippet(self, driver):
        self.test_11_add_snippet_successfully(driver)
        driver.get("http://localhost:5000")
        driver.find_element(By.CSS_SELECTOR, ".snippet-card").click()
        driver.find_element(By.ID, "edit-btn").click()
        title_field = driver.find_element(By.ID, "title")
        title_field.clear()
        title_field.send_keys("Updated: Binary Search")
        driver.find_element(By.ID, "update-btn").click()
        assert "Updated: Binary Search" in driver.page_source
        print("✓ Test 18 passed")
    
    def test_19_delete_snippet(self, driver):
        self.test_11_add_snippet_successfully(driver)
        driver.get("http://localhost:5000")
        driver.find_element(By.CSS_SELECTOR, ".snippet-card").click()
        driver.find_element(By.ID, "delete-btn").click()
        driver.switch_to.alert.accept()
        assert "Snippet deleted" in driver.page_source
        print("✓ Test 19 passed")
