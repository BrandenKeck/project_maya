import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

# Fetch Roster
def fetch_roster(team):

    # Clean up the team name
    team = team.replace("é", "e").replace(".", "").replace(" ", "-").lower()

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
    driver.get(f"https://www.dailyfaceoff.com/teams/{team}/line-combinations/")
    driver.implicitly_wait(10)

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

# Fetch Odds from Sportsbook
def fetch_odds(odds_key):
    
    # API Call
    games = []
    sport='icehockey_nhl'    
    regions = 'us'
    markets = 'h2h,spreads,totals'
    bookmaker = 'fanduel'
    format = 'american'
    url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={odds_key}&regions={regions}&markets={markets}&bookmakers={bookmaker}&oddsFormat={format}'
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

# Fetch Historical Data Function - NHL API
def fetch_games(start="2015-10-01", end="2023-10-01"):

    # Get a set of Game IDs in the date range
    games, teams, skaters, goaltenders = [], [], [], []
    url = f'https://statsapi.web.nhl.com/api/v1/schedule?startDate={start}&endDate={end}'
    resp = requests.get(url).json()
    for d in resp['dates']:
        for g in d['games']:
            if g['gameType'] == 'R': games.append(g['gamePk'])

    # Append data for each game
    for game in games:

        # Get date of game
        url = f'https://statsapi.web.nhl.com/api/v1/game/{game}/feed/live'
        resp = requests.get(url).json()

        # Get and parse game data
        if resp['gameData']['status']['detailedState'] == 'Final':
            game_date = resp['gameData']['datetime']['dateTime']
            game_date = game_date.replace("T", " ").replace("Z", "")
            url = f'https://statsapi.web.nhl.com/api/v1/game/{game}/boxscore'
            resp = requests.get(url).json()
            tt, ss, gg = parse_game(game, game_date, resp)
            teams = teams + tt
            skaters = skaters + ss
            goaltenders = goaltenders + gg

        # Update console
        print(f"Added Game {game}")

    return teams, skaters, goaltenders

# Update subfunction - handle game statistics
def parse_game(game_id, date, data):

    # Parse Data Objects
    home_team = data['teams']['home']['team']
    home_players = data['teams']['home']['players']
    away_team = data['teams']['away']['team']
    away_players = data['teams']['away']['players']

    # Handle Player Stats
    homeskaters, homedefencemen, homegoaltenders = parse_player_stats(home_players, game_id, home_team['id'], away_team['id'], date, 1)
    awayskaters, awaydefencemen, awaygoaltenders = parse_player_stats(away_players, game_id, away_team['id'], home_team['id'], date, 0)
    skaters = homeskaters + awayskaters
    goaltenders = homegoaltenders + awaygoaltenders

    # Get Average Statistics
    home_avg_goals = float(sum(d['goals_toi'] for d in homeskaters)) / len(homeskaters)
    home_avg_assists = float(sum(d['assists_toi'] for d in homeskaters)) / len(homeskaters)
    home_avg_shots = float(sum(d['shots_toi'] for d in homeskaters)) / len(homeskaters)
    home_avg_blocks = float(sum(d['blocks_toi'] for d in homeskaters)) / len(homeskaters)
    home_avg_hits = float(sum(d['hits_toi'] for d in homeskaters)) / len(homeskaters)
    home_avg_takeaways = float(sum(d['takeaways_toi'] for d in homeskaters)) / len(homeskaters)
    home_avg_giveaways = float(sum(d['giveaways_toi'] for d in homeskaters)) / len(homeskaters)
    home_avg_dblocks = float(sum(d['blocks_toi'] for d in homedefencemen)) / len(homedefencemen)
    home_avg_dhits = float(sum(d['hits_toi'] for d in homedefencemen)) / len(homedefencemen)
    home_avg_shots_against = float(sum(d['shots_against_toi'] for d in homegoaltenders)) / len(homegoaltenders)
    home_avg_goals_against = float(sum(d['goals_against_toi'] for d in homegoaltenders)) / len(homegoaltenders)
    home_avg_save_percentage = float(sum(d['save_percentage_toi'] for d in homegoaltenders)) / len(homegoaltenders)
    away_avg_goals = float(sum(d['goals_toi'] for d in awayskaters)) / len(awayskaters)
    away_avg_assists = float(sum(d['assists_toi'] for d in awayskaters)) / len(awayskaters)
    away_avg_shots = float(sum(d['shots_toi'] for d in awayskaters)) / len(awayskaters)
    away_avg_blocks = float(sum(d['blocks_toi'] for d in awayskaters)) / len(awayskaters)
    away_avg_hits = float(sum(d['hits_toi'] for d in awayskaters)) / len(awayskaters)
    away_avg_takeaways = float(sum(d['takeaways_toi'] for d in awayskaters)) / len(awayskaters)
    away_avg_giveaways = float(sum(d['giveaways_toi'] for d in awayskaters)) / len(awayskaters)
    away_avg_dblocks = float(sum(d['blocks_toi'] for d in awaydefencemen)) / len(awaydefencemen)
    away_avg_dhits = float(sum(d['hits_toi'] for d in awaydefencemen)) / len(awaydefencemen)
    away_avg_shots_against = float(sum(d['shots_against_toi'] for d in awaygoaltenders)) / len(awaygoaltenders)
    away_avg_goals_against = float(sum(d['goals_against_toi'] for d in awaygoaltenders)) / len(awaygoaltenders)
    away_avg_save_percentage = float(sum(d['save_percentage_toi'] for d in awaygoaltenders)) / len(awaygoaltenders)

    # Complete Team Stats
    teams = [
        {
            "team_id": str(int(home_team['id'])),
            "team_name": home_team['name'],
            "game_id": str(int(game_id)),
            "date": date,
            "is_home": 1,
            "skater_goals_toi": home_avg_goals,
            "skater_assists_toi": home_avg_assists,
            "skater_shots_toi": home_avg_shots,
            "skater_blocks_toi": home_avg_blocks,
            "skater_hits_toi": home_avg_hits,
            "skater_takeaways_toi": home_avg_takeaways,
            "skater_giveaways_toi": home_avg_giveaways,
            "defenseman_blocks_toi": home_avg_dblocks,
            "defenseman_hits_toi": home_avg_dhits,
            "goaltender_shots_against_toi": home_avg_shots_against,
            "goaltender_goals_against_toi": home_avg_goals_against,
            "goaltender_save_percentage_toi": home_avg_save_percentage,
            "record_id": int(f"{int(home_team['id'])}{int(game_id)}")
        },
        {
            "team_id": str(int(away_team['id'])),
            "team_name": away_team['name'],
            "game_id": str(int(game_id)),
            "date": date,
            "is_home": 0,
            "skater_goals_toi": away_avg_goals,
            "skater_assists_toi": away_avg_assists,
            "skater_shots_toi": away_avg_shots,
            "skater_blocks_toi": away_avg_blocks,
            "skater_hits_toi": away_avg_hits,
            "skater_takeaways_toi": away_avg_takeaways,
            "skater_giveaways_toi": away_avg_giveaways,
            "defenseman_blocks_toi": away_avg_dblocks,
            "defenseman_hits_toi": away_avg_dhits,
            "goaltender_shots_against_toi": away_avg_shots_against,
            "goaltender_goals_against_toi": away_avg_goals_against,
            "goaltender_save_percentage_toi": away_avg_save_percentage,
            "record_id": f"{int(away_team['id'])}{int(game_id)}"
        }
    ]

    return teams, skaters, goaltenders

# Update subfunction - handle individual player stats
def parse_player_stats(players, game_id, team_id, opp_id, date, is_home):
    skaters, defencemen, goaltenders = [], [], []
    for player in players:
        if players[player]['stats']:
            p_id = players[player]["person"]["id"]
            p_name = players[player]["person"]["fullName"]
            p_pos = players[player]["position"]["code"]
            if p_pos == 'G':
                p_stat = players[player]['stats']['goalieStats']
                p_toi = toi_to_minutes(p_stat['timeOnIce'])
                goaltenders.append({
                    "goaltender_id": str(int(p_id)),
                    "goaltender_name": p_name,
                    "team_id": str(int(team_id)),
                    "opp_id": str(int(opp_id)),
                    "game_id": str(int(game_id)),
                    "date": date,
                    "is_home": is_home,
                    "toi": p_toi,
                    "saves": p_stat['saves'],
                    "shots_against": p_stat['shots'],
                    "goals_against": p_stat['shots'] - p_stat['saves'],
                    "save_percentage": p_stat['saves']/p_stat['shots'] if p_stat['shots']>0 else 0,
                    "shots_against_toi": p_stat['shots']/p_toi if p_toi>0 else 0,
                    "goals_against_toi": (p_stat['shots']-p_stat['saves'])/p_toi if p_toi>0 else 0,
                    "save_percentage_toi": (p_stat['saves']/p_stat['shots'])/p_toi if p_stat['shots'] and p_toi>0 else 0,
                    "record_id": f'{int(p_id)}{int(game_id)}'
                })
            else:
                p_stat = players[player]['stats']['skaterStats']
                p_toi = toi_to_minutes(p_stat['timeOnIce'])
                datarow = {
                    "skater_id": str(int(p_id)),
                    "skater_name": p_name,
                    "team_id": str(int(team_id)),
                    "opp_id": str(int(opp_id)),
                    "game_id": str(int(game_id)),
                    "date": date,
                    "is_home": is_home,
                    "toi": p_toi,
                    "goals": p_stat['goals'],
                    "assists": p_stat['assists'],
                    "shots": p_stat['shots'],
                    "blocks": p_stat['blocked'],
                    "hits": p_stat['hits'],
                    "takeaways": p_stat['takeaways'],
                    "giveaways": p_stat['giveaways'],
                    "goals_toi": p_stat['goals']/p_toi if p_toi>0 else 0,
                    "assists_toi": p_stat['assists']/p_toi if p_toi>0 else 0,
                    "shots_toi": p_stat['shots']/p_toi if p_toi>0 else 0,
                    "blocks_toi": p_stat['blocked']/p_toi if p_toi>0 else 0,
                    "hits_toi": p_stat['hits']/p_toi if p_toi>0 else 0,
                    "takeaways_toi": p_stat['takeaways']/p_toi if p_toi>0 else 0,
                    "giveaways_toi": p_stat['giveaways']/p_toi if p_toi>0 else 0,
                    "record_id": f'{int(p_id)}{int(game_id)}'
                }
                skaters.append(datarow)
                if p_pos == 'D': defencemen.append(datarow)

    return skaters, defencemen, goaltenders

def toi_to_minutes(toi):
    min, sec = toi.split(":")
    real_toi = float(min) + float(sec)/60
    return real_toi
