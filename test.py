import pandas as pd
from data.datafetch import DataManagement
dm = DataManagement()

players = dm.fetch_roster("Pittsburgh Penguins")
ptable = pd.DataFrame()
for position in players:
    for player in players[position]:
        newtable = dm.fetch_data(player, position)
        pd.concat([ptable, newtable])