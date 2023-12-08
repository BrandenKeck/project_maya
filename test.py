import pandas as pd
from data.datafetch import DataManagement
dm = DataManagement()

players = dm.fetch_roster("Carolina Hurricanes")
ptable = pd.DataFrame()
for position in players:
    for player in players[position]:
        try:
            newtable = dm.fetch_data(player, position)
            ptable = pd.concat([ptable, newtable])
        except:
            print(f"Error on {player.title()}")


# dm.fetch_data("Michael Bunting", "Carolina Hurricanes", "F")