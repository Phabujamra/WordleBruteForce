from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Browser:
    def __init__(self, driver_path: str,  url: str, headless: bool = True) -> None:
        self.driver_path = driver_path
        self.url = url
        self.headless = headless
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        options = Options()

        # Headless mode
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        # General options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-inforbars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--incognito")

        # User-Agent spoofing
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")

        # Performance optimizations
        options.add_argument("--start-maximized")
        options.add_argument("--disable-logging")

        # Initialize the driver
        service = Service(executable_path=self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        return driver
    

    def get_driver(self):
        return self.driver
    

    def wait_for_element(self, by: By, value: str, timeout: int):
        """Wait for an element to be present on the page"""
        try:
            element = WebDriverWait(driver=self.driver, timeout=timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Element not found: {by} = {value}")
            return None
        

    def click_element(self, by: By, value: str, timeout: int):
        """Click on an element"""
        element = WebDriverWait(driver=self.driver, timeout=timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        if element:
            element.click()
            print(f"Element clicked {by} = {value}")
        else:
            print(f"No clickable element at {by} = {value}")


    def send_keys_to_element(self, by: By, value: str, timeout: int, keys: str):
        """Send keys to an element"""
        element = self.wait_for_element(by=by, value=value, timeout=timeout)
        if element:
            element.send_keys(keys)
        else:
            print(f"Unable to send keys to {by} = {value}")


    def get_element_text(self, by: By, value: str, timeout: int):
        """Get text from an element"""
        element = self.wait_for_element(by=by, value=value, timeout=timeout)
        if element:
            return element.text
        else:
            print(f"Unable to get text from: {by} = {value}")

    
    def get_element_property(self, element, property_name):
        return element.get_property(name=property_name)

    
    def quit(self):
        """Close the WebDriver"""
        self.driver.quit()

    
    def goto(self, url: str):
        """Go to URL"""
        self.driver.get(url)
