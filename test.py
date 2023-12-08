import pandas as pd
from data.datafetch import DataManagement
dm = DataManagement()

team = "Carolina Hurricanes"
players = dm.fetch_roster(team)
# players = {'F': ['Teuvo Teravainen', 'Sebastian Aho', 'Martin Necas']}
ptable = pd.DataFrame()
for position in players:
    for player in players[position]:
        error = True
        while error:
            try:
                newtable = dm.fetch_data(player, team, position)
                ptable = pd.concat([ptable, newtable])
                error = False
            except:
                print(f"Error on {player.title()}")
                error = True


# dm.fetch_data("Sebastian Aho", "Carolina Hurricanes", "F")
# dm.fetch_data("Martin Necas", "Carolina Hurricanes", "F")