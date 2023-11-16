from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

from data.datafetch import fetch_roster

players = fetch_roster("Pittsburgh Penguins")

naota = players['skaters'][0]

# Driver options
cache_manager=DriverCacheManager("./driver")
driver = ChromeDriverManager(cache_manager=cache_manager).install()
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--log-level=3")
options.add_argument("--disable-notifications")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)
driver.get(f"https://www.hockey-reference.com/")
thefuck = driver.find_element("xpath", f"//input[@type='search']")
thefuck.clear()
thefuck.Type(naota.title())
thefuckingfuck = driver.find_element("xpath", f"//input[@type='submit']")
thefuckingfuck.send_keys(Keys.RETURN)





# Get Skaters
s18 = []
sk_paths = [
    [1, "div/", 4, 1], [1, "div/", 4, 2], [1, "div/", 4, 3],
    [1, "div/", 5, 1], [1, "div/", 5, 2], [1, "div/", 5, 3],
    [1, "div/", 6, 1], [1, "div/", 6, 2], [1, "div/", 6, 3],
    [1, "div/", 7, 1], [1, "div/", 7, 2], [1, "div/", 7, 3],
    [2, "", 2, 1], [2, "", 2, 2],
    [2, "", 3, 1], [2, "", 3, 2],
    [2, "", 4, 1], [2, "", 4, 2],
]
for path in sk_paths:
    try: sk8r = driver.find_element("xpath", f"//section[@id='line_combos']/div[{path[0]}]/{path[1]}div[{path[2]}]/div[{path[3]}]/div/div[2]/a/span").text
    except: sk8r = "Not Found"
    s18.append(sk8r)

# Get Goaltenders
g2 = []
for num in [1,2]:
    try: g0ly = driver.find_element("xpath", f"//section[@id='line_combos']/div[9]/div[2]/div[{num}]/div/div[2]/a/span").text
    except: g0ly = "Not Found"
    g2.append(g0ly)

# Return info
return {"skaters": s18, "goaltenders": g2}