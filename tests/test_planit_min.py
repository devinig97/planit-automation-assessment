from decimal import Decimal
import os, re, pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

BASE_URL = "http://jupiter.cloud.planittesting.com"
PRICES = {
    "Stuffed Frog": Decimal("10.99"),
    "Fluffy Bunny": Decimal("9.99"),
    "Valentine Bear": Decimal("14.99"),
}

# driver
def make_driver():
    opts = Options()
    if os.getenv("HEADLESS") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1600,1000")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

# Page objects
class Home:
    def __init__(self, d): 
        self.d, self.w = d, WebDriverWait(d, 15)

    def open(self):
        self.d.get(BASE_URL)
        self.w.until(EC.visibility_of_element_located((By.LINK_TEXT, "Contact")))
        return self

    def go(self, link_text):
        if link_text.strip().lower() == "cart":
            try:
                self.w.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='#/cart']"))).click()
            except Exception:
                self.w.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Cart"))).click()
        else:
            self.w.until(EC.element_to_be_clickable((By.LINK_TEXT, link_text))).click()
        return self

class Contact:
    FN     = (By.ID, "forename")
    EMAIL  = (By.ID, "email")
    MSG    = (By.ID, "message")
    SUBMIT = (By.XPATH, "//a[normalize-space()='Submit']")
    FN_ERR    = (By.ID, "forename-err")
    EMAIL_ERR = (By.ID, "email-err")
    MSG_ERR   = (By.ID, "message-err")

    SUCCESS = (By.CSS_SELECTOR, "div.alert-success")

    def __init__(self, d):
        self.d = d
        self.w = WebDriverWait(d, 15)

    def submit_empty(self):
        self.w.until(EC.element_to_be_clickable(self.SUBMIT)).click()
        self.w.until(
            lambda _:
                any(EC.visibility_of_element_located(loc)(self.d)
                    for loc in (self.FN_ERR, self.EMAIL_ERR, self.MSG_ERR))
        )

    def assert_errors_present(self):
        for loc in (self.FN_ERR, self.EMAIL_ERR, self.MSG_ERR):
            el = self.w.until(EC.visibility_of_element_located(loc))
            assert el.text.strip() != ""

    def fill_mandatory(self, name, email, message):

        fn = self.w.until(EC.visibility_of_element_located(self.FN))
        fn.clear(); fn.send_keys(name); fn.send_keys(Keys.TAB)

        em = self.d.find_element(*self.EMAIL)
        em.clear(); em.send_keys(email); em.send_keys(Keys.TAB)

        ms = self.d.find_element(*self.MSG)
        ms.clear(); ms.send_keys(message); ms.send_keys(Keys.TAB)

        try:
            self.d.find_element(By.TAG_NAME, "h1").click()
        except Exception:
            pass

    def assert_errors_cleared(self):
        def cleared(loc):
            try:
                el = self.d.find_element(*loc)
            except Exception:
                return True
            return (not el.is_displayed()) or (el.text.strip() == "")

        WebDriverWait(self.d, 20).until(
            lambda _: all(cleared(loc) for loc in (self.FN_ERR, self.EMAIL_ERR, self.MSG_ERR))
        )

    def assert_errors_gone(self):
        self.assert_errors_cleared()

    def submit(self):
        self.w.until(EC.element_to_be_clickable(self.SUBMIT)).click()

    def assert_success(self, name: str):
        self.d.execute_script("window.scrollTo(0, 0);")
        banner = WebDriverWait(self.d, 30).until(EC.visibility_of_element_located(self.SUCCESS))
        WebDriverWait(self.d, 5).until(lambda _: "Thanks" in banner.text)
        assert "Thanks" in banner.text and name in banner.text

class Shop:
    def __init__(self, d): self.d, self.w = d, WebDriverWait(d, 15)
    def price_of(self, name):
        el=self.w.until(EC.visibility_of_element_located(
            (By.XPATH, f"//h4[normalize-space()='{name}']/following-sibling::p[1]//span")))
        return Decimal(el.text.replace("$","").strip())
    def buy(self, name, times=1):
        btn=(By.XPATH,f"//h4[normalize-space()='{name}']/following-sibling::p//a[normalize-space()='Buy']")
        for _ in range(times): self.w.until(EC.element_to_be_clickable(btn)).click()

class Cart:
    def __init__(self, d): self.d, self.w = d, WebDriverWait(d, 15)
    def row(self, name):
        return self.w.until(EC.visibility_of_element_located(
            (By.XPATH,f"//table//td[normalize-space()='{name}']/parent::tr")))
    def unit_price(self, name):
        return Decimal(self.row(name).find_element(By.XPATH,"./td[2]").text.replace("$","").strip())
    def qty(self, name):
        return int(self.row(name).find_element(By.XPATH,".//input[@type='number' or contains(@class,'input-mini')]").get_attribute("value"))
    def subtotal(self, name):
        return Decimal(self.row(name).find_element(By.XPATH,"./td[4]").text.replace("$","").strip())
    def total(self):
        el=self.w.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"strong.total")))
        txt=el.text.strip()              # e.g., "Total: 116.90"
        m=re.search(r"(\d+\.\d{2})",txt) # capture 116.90
        return Decimal(m.group(1)) if m else Decimal(txt.split(":")[-1].strip())

# Test case 01
def test_case_1_contact_validation():
    d = make_driver()
    try:
        Home(d).open().go("Contact")
        c = Contact(d)
        c.submit_empty()
        c.assert_errors_present()
        c.fill_mandatory("TestUser_01","testuser_01@example.com","Feedback")
        c.assert_errors_gone()
    finally:
        d.quit()

# Test case 02
@pytest.mark.parametrize("i", range(5))
def test_case_2_contact_submit_5x(i):
    d = make_driver()
    try:
        Home(d).open().go("Contact")
        c = Contact(d)

        name = f"TestUser_{i+1}"
        c.fill_mandatory(name, f"{name}@example.com", "Feedback")
        c.submit()
        c.assert_success(name)
    finally:
        d.quit()

# Test case 03
def test_case_3_shop_cart_totals():
    d = make_driver()
    try:
        Home(d).open().go("Shop")
        s = Shop(d)
        assert s.price_of("Stuffed Frog")   == PRICES["Stuffed Frog"]
        assert s.price_of("Fluffy Bunny")   == PRICES["Fluffy Bunny"]
        assert s.price_of("Valentine Bear") == PRICES["Valentine Bear"]

        s.buy("Stuffed Frog",2); s.buy("Fluffy Bunny",5); s.buy("Valentine Bear",3)
    
        Home(d).go("Cart")
        cart = Cart(d)

        items=[("Stuffed Frog",2),("Fluffy Bunny",5),("Valentine Bear",3)]
        for name, q in items:
            unit = cart.unit_price(name)
            assert unit == PRICES[name]
            assert cart.qty(name) == q
            assert cart.subtotal(name) == unit * q
        total_expected = sum((cart.subtotal(name) for name, _ in items), start=Decimal("0.00"))
        assert cart.total() == total_expected
    finally:
        d.quit()
