import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.core.driver_cache import DriverCacheManager


class DataManagement():

    def __init__(self):
        self.driver = self.get_driver()
        self.driver.implicitly_wait(10)

    def get_driver(self):
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
        return driver

    # Fetch Roster
    def fetch_roster(self, team):

        # Clean up the team name
        team = team.replace("é", "e").replace(".", "").replace(" ", "-").lower()
        self.driver.get(f"https://www.dailyfaceoff.com/teams/{team}/line-combinations/")

        # Get Skaters
        f = []
        f_paths = [
            [1, "div/", 4, 1], [1, "div/", 4, 2], [1, "div/", 4, 3],
            [1, "div/", 5, 1], [1, "div/", 5, 2], [1, "div/", 5, 3],
            [1, "div/", 6, 1], [1, "div/", 6, 2], [1, "div/", 6, 3],
            [1, "div/", 7, 1], [1, "div/", 7, 2], [1, "div/", 7, 3],
        ]
        for path in f_paths:
            try: sk8r = self.driver.find_element("xpath", f"//section[@id='line_combos']/div[{path[0]}]/{path[1]}div[{path[2]}]/div[{path[3]}]/div/div[2]/a/span").text
            except: sk8r = "Not Found"
            f.append(sk8r)

        # Get Defensemen
        d = []
        d_paths = [
            [2, "", 2, 1], [2, "", 2, 2],
            [2, "", 3, 1], [2, "", 3, 2],
            [2, "", 4, 1], [2, "", 4, 2],
        ]
        for path in d_paths:
            try: sk8r = self.driver.find_element("xpath", f"//section[@id='line_combos']/div[{path[0]}]/{path[1]}div[{path[2]}]/div[{path[3]}]/div/div[2]/a/span").text
            except: sk8r = "Not Found"
            d.append(sk8r)

        # Get Goaltenders
        g = []
        for num in [1,2]:
            try: g0ly = self.driver.find_element("xpath", f"//section[@id='line_combos']/div[9]/div[2]/div[{num}]/div/div[2]/a/span").text
            except: g0ly = "Not Found"
            g.append(g0ly)
        
        # Return info
        return {"F": f, "D": d, "G": g}

    # Fetch Data
    def fetch_data(self, player, position):
        self.driver.get(f"https://www.hockey-reference.com/")
        searchbar = self.driver.find_element("xpath", 
            f"//div[@id='header']/div[@class='search']/form/div/div"
        )
        searchbar.click()
        actions = ActionChains(self.driver)
        actions.send_keys(player.title())
        actions.send_keys(Keys.RETURN)
        actions.perform()
        htmlsource=self.driver.find_element("xpath", 
            f"//div[@id='div_last5']/table"
        )
        table=pd.read_html(htmlsource.get_attribute('outerHTML'))[0]
        table.columns = [ii[1] for ii in table.columns.tolist()]
        table["Name"] = player.title()
        table["Position"] = position
        if position is not "G":
            table["GA"] = None
            table["SV"] = None
            table["SV%"] = None
        else:
            table["G"] = None
            table["A"] = None
            table["SOG"] = None
            table["BLK"] = None
            table["HIT"] = None
        table = table[["Name", "Date", "G", "A", "SOG", "BLK", "HIT", "GA", "SV", "SV%", "TOI"]]
        return table

    # Fetch Odds from Sportsbook
    def fetch_odds(self, odds_key):
        games = []
        sport='icehockey_nhl'    
        regions = 'us'
        markets = 'h2h,spreads,totals'
        bookmaker = 'fanduel'
        odds_format = 'american'
        url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={odds_key}&regions={regions}&markets={markets}&bookmakers={bookmaker}&oddsFormat={odds_format}'
        resp = requests.get(url).json()
        for r in resp:
            if len(r['bookmakers']) > 0:
                home = r['home_team']
                away = r['away_team']
                if len(r['bookmakers'][0]['markets']) >= 2:
                    mtype = [mm['key'] for mm in  r['bookmakers'][0]['markets']]
                    h2hidx = mtype.index("h2h")
                    totidx = mtype.index("totals")
                    if r['bookmakers'][0]['markets'][h2hidx]['outcomes'][0]['name'] == home:
                        home_price = r['bookmakers'][0]['markets'][h2hidx]['outcomes'][0]['price']
                        away_price = r['bookmakers'][0]['markets'][h2hidx]['outcomes'][1]['price']
                    else:
                        home_price = r['bookmakers'][0]['markets'][h2hidx]['outcomes'][1]['price']
                        away_price = r['bookmakers'][0]['markets'][h2hidx]['outcomes'][0]['price']
                    games.append({
                        'home': home,
                        'away': away,
                        'date': r['commence_time'],
                        'home_odds': home_price,
                        'away_odds': away_price,
                        'over_odds': r['bookmakers'][0]['markets'][totidx]['outcomes'][0]['price'],
                        'under_odds': r['bookmakers'][0]['markets'][totidx]['outcomes'][1]['price'],
                        'ou_points': r['bookmakers'][0]['markets'][totidx]['outcomes'][0]['point']
                    })
        return games

    # Convert string TOI to float minutes
    def toi_to_minutes(toi):
        min, sec = toi.split(":")
        real_toi = float(min) + float(sec)/60
        return real_toi
