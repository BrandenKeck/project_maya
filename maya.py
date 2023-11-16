# Imports
import numpy as np
import pandas as pd
from sqlalchemy import text
from datetime import datetime

# Custom Imports
from data.database import LakshmiDatabase
from model.model import SkaterDataset, SkaterModel

# Master Class
class Maya():

    def __init__(self):
        self.db = LakshmiDatabase()

    def new_db(self):
        self.db.create()
    
    def get_roster(self, team):
        return self.db.get_roster(team)

    def update_odds(self):
        xx = self.db.update_odds()
        print(xx)

    def update_games(self):
        self.db.update_games()
    
    def train_model(self, skater_id=8471675):
        data = self.db.ppdb.search(self.ppq.skater_id==skater_id)
        dataset = SkaterDataset(data, "cpu")
        mod = SkaterModel(id=skater_id, device="cpu")
        mod.train_network(dataset)
        mod.save()

    
    
    

    # # Run Subfunction - Get Player Goals Distributions
    # def predict_player(self, sk, te, op, gt, da, ha, network=True):
    #     if sk and sk.data.shape[0] > 30:
    #         sk.generate_models(mods=['goals'])
    #         sk.generate_regressors(regs=['goals'])
    #         params = sk.predict_next(te, op, gt, da, ha, network=network)
    #     else: params = None
    #     return params

    # # Run Subfunction - Use Average Stats
    # def use_average(self, sk):
    #     try:
    #         mu = np.average(sk.data.loc[:, "goals"],
    #             weights=np.arange(len(sk.data.loc[:, "goals"])))
    #         if mu > 0.005:
    #             params = [1-mu, mu, 0, 0, 0]
    #         else:
    #             params = [0.995, 0.005, 0, 0, 0]
    #     except:
    #         params = [0.995, 0.005, 0, 0, 0]
    #     return params

    # # Run Subfunction - Create Team Goals Histogram
    # def build_team_histogram(self, data):
    #     file = f'F:/floating_repos/lakshmi/reports/img/{str(uuid.uuid4())}.png'
    #     fig = plt.figure(figsize=(5, 5))
    #     plt.hist(data, bins=np.arange(13))
    #     plt.savefig(file)
    #     plt.close('all')
    #     return file

    # # Run Subfunction - Create Player Goals Histogram
    # def build_player_histogram(self, data):
    #     file = f'F:/floating_repos/lakshmi/reports/img/{str(uuid.uuid4())}.png'
    #     fig = plt.figure(figsize=(5, 5))
    #     plt.bar(np.arange(len(data)), np.array(data))
    #     plt.savefig(file)
    #     plt.close('all')
    #     return file
        
    # def generate_report(self):
        # report_data.append({
        #     "home": {
        #         "name": h_name.replace("é", "e"),
        #         "in_goal": hgt,
        #         "distribution": self.build_team_histogram(odd_res["Home Goals Distribution"]),
        #         "players": [{
        #             "name": hsk[kk].replace("Ü", "U"),
        #             "predtype": home_types[kk],
        #             "average": float(np.dot(np.arange(5), home_dists[kk])),
        #             "distribution": self.build_player_histogram(home_dists[kk])}
        #             for kk in np.arange(len(home_dists))]
        #     },
        #     "away": {
        #         "name": a_name.replace("é", "e"),
        #         "in_goal": agt,
        #         "distribution": self.build_team_histogram(odd_res["Away Goals Distribution"]),
        #         "players": [{
        #             "name": ask[kk].replace("Ü", "U"), 
        #             "predtype": away_types[kk],
        #             "average": float(np.dot(np.arange(5), away_dists[kk])),
        #             "distribution": self.build_player_histogram(away_dists[kk])}
        #             for kk in np.arange(len(away_dists))]
        #     },
        #     "odds": {k: odd_res[k] for k in odd_res.keys() - ["Home Goals Distribution", "Away Goals Distribution"]}
        # })
        # self.reports.set_name(f"{date.today().year}-{'{:02d}'.format(date.today().month)}-{'{:02d}'.format(date.today().day)} Daily Report")
        # self.reports.generate(report_data)

    # # TODO
    # def get_last_update(self):
    #     if self.last_update:
    #         lu = datetime.strptime(self.last_update, "%Y-%m-%d").date()
    #         return lu
    #     else: return None

    # # TODO
    # def set_last_update(self, yyyy, mm, dd):
    #     dt = datetime(yyyy, mm, dd).strftime("%Y-%m-%d")
    #     self.last_update = dt

    # # Get Game Score and Kelly Criterion
    # def decide_game(self, home, away, odd, itr = 50_000_000):

    #     # Call Sim Function
    #     (home_goals, away_goals) = self.sim_goals(home, away, itr)

    #     # Collect totals
    #     totals = home_goals + away_goals
    #     home_wins = np.greater(home_goals, away_goals)
    #     away_wins = np.greater(away_goals, home_goals)
    #     overtime = np.equal(home_goals, away_goals)
    #     ou_goals = totals + overtime
    #     res_df = pd.DataFrame(
    #         index = np.arange(itr),
    #         data = np.array([home_goals.tolist(), away_goals.tolist(), totals.tolist(), home_wins.tolist(), away_wins.tolist(), overtime.tolist(), ou_goals.tolist()]).T,
    #         columns = [f"{odd['home']} Goals", f"{odd['away']} Goals", "Totals", f"{odd['home']} Win", f"{odd['away']} Win", "Overtime", "OU Totals"]
    #     )

    #     # Compute Statistics
    #     home_wins = res_df[res_df[f"{odd['home']} Win"]==1].shape[0]
    #     away_wins = res_df[res_df[f"{odd['away']} Win"]==1].shape[0]
    #     home_probs = home_wins / (home_wins + away_wins)
    #     away_probs = away_wins / (home_wins + away_wins)
    #     ot_potential = 1 - (home_wins + away_wins) / itr
    #     over_probs = res_df[res_df["OU Totals"]>odd['ou_points']].shape[0] / itr
    #     under_probs = res_df[res_df["OU Totals"]<odd['ou_points']].shape[0] / itr

    #     # KC Information
    #     kc_home = self.kelly_criterion(home_probs, odd['home_odds'])
    #     kc_away = self.kelly_criterion(away_probs, odd['away_odds'])
    #     kc_over = self.kelly_criterion(over_probs, odd['over_odds'])
    #     kc_under = self.kelly_criterion(under_probs, odd['under_odds'])

    #     return({
    #         f"Home Win Probability": home_probs,
    #         f"Away Win Probability": away_probs,
    #         f"Overtime Potential": ot_potential,
    #         f"Avg Home Goals": np.mean(home_goals),
    #         f"Avg Away Goals": np.mean(away_goals),
    #         f"Home Goals Distribution": home_goals.tolist(),
    #         f"Away Goals Distribution": away_goals.tolist(),
    #         f"Avg Total Goals": np.mean(totals),
    #         f"Avg OU Goals": np.mean(ou_goals),
    #         f"Over Probability": over_probs,
    #         f"Under Probability": under_probs,
    #         f"Home Win Kelly Criterion": kc_home,
    #         f"Away Win Kelly Criterion": kc_away,
    #         f"Over Kelly Criterion": kc_over,
    #         f"Under Kelly Criterion": kc_under,
    #         f"Sports Book Goals": odd['ou_points'],
    #         f"Sports Book Over": odd['over_odds'],
    #         f"Sports Book Under": odd['under_odds'],
    #         f"Sports Book Home Win": odd['home_odds'],
    #         f"Sports Book Away Win": odd['away_odds']
    #     })

    # def sim_goals(self, home, away, nsim):

    #     # Options
    #     numg = [0, 1, 2, 3, 4]

    #     # Home Team Simulation
    #     home_goals = np.zeros(nsim)
    #     for params in home:
    #         try: home_goals = home_goals + np.random.choice(numg, nsim, p=params)
    #         except: print(f"DISTRIBUTION ERROR: {params}")

    #     # Away Team Simulation
    #     away_goals = np.zeros(nsim)
    #     for params in away:
    #         try: away_goals = away_goals + np.random.choice(numg, nsim, p=params)
    #         except: print(f"DISTRIBUTION ERROR: {params}")

    #     return (home_goals, away_goals)

    # # Calculate proportion of bankroll to bet
    # def kelly_criterion(self, calc_p, ao):
    #     b = self.ao_to_earnings(ao)
    #     return calc_p - (1 - calc_p) / b

    # def zero_func(self, x):
    #     if x < 0: return 0
    #     else: return x

    # # Convert American Odds to Earnings
    # def ao_to_earnings(self, ao):
    #     if ao < 0:
    #         ao = abs(ao)
    #         Z = 100/ao
    #     else: Z = ao/100
    #     return Z

    # # Convert American Odds to Percentage
    # def ao_to_percentage(self, ao):
    #     if ao < 0:
    #         ao = abs(ao)
    #         p = ao/(ao+100)
    #     else: p = 100/(ao+100)
    #     return p
