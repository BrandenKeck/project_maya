# Database Imports
import json
import numpy as np
import pandas as pd
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, String, Numeric
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column

# Helper Functions
from data.datafetch import fetch_roster, fetch_odds, fetch_games

# Establish an empty Base class
class Base(DeclarativeBase):
    pass

# Bets Class - TODO
class Bets(Base):

    __tablename__ = "bets"
    idx: Mapped[int] = mapped_column(primary_key=True)
    
    def __repr__(self):
        return f"BetData({self.idx})"

class LakshmiDatabase():

    def __init__(self):
        self.ppq = Query()
        self.ppdb = TinyDB("data/preproc_data.json")
        self.engine = create_engine("sqlite:///data/bets.db")
        self.session = Session(self.engine)
        self.connection = self.engine.raw_connection()
        
    def create(self):
        Base.metadata.create_all(self.engine)
    
    def get_roster(self, team):
        return fetch_roster(team)
    
    def get_data(self, query="SELECT * FROM skaters"):
        with self.engine.begin() as conn:
            query = text(query)
            return pd.read_sql_query(query, conn)

    def update_odds(self):
        with open('data/keys.json') as f:
            api_key = json.load(f)["odds_key"]
        games = fetch_odds(api_key)
        return games
    
    def update_games(self, start="2015-10-01", end="2023-10-01"):    
        teams, skaters, goaltenders = fetch_games(start, end)
        for team in teams: self.add_team_data(team)
        for skater in skaters: self.add_skater_data(skater)
        for goaltender in goaltenders: self.add_goaltender_data(goaltender)
        self.session.commit()
    
    def preprocess_data(self, skater_id=8471675):

        # Skater Games List:
        q = f"""SELECT 
                goals as lab,
                date as dt,
                game_id as gid,
                team_id as tid,
                opp_id as oid
                FROM skaters 
                WHERE skater_id={skater_id}
                ORDER BY date"""
        games = self.get_data(q)

        # Data Loop
        dates = list(games["dt"])
        labels = list(games["lab"])
        gids = list(games["gid"])
        tids = list(games["tid"])
        oids = list(games["oid"])
        if len(dates)>20:
            for idx in np.arange(10, len(dates)):

                # Skip existing records
                is_record = self.ppdb.search(self.ppq.record_id==int(f"{skater_id}{gids[idx]}"))
                if len(is_record)>0: continue

                # Player Stats Block
                first = dates[idx-10]
                last = dates[idx]
                q = f"""SELECT 
                    goals_toi as gtoi,
                    assists_toi as atoi,
                    blocks_toi as btoi,
                    shots_toi as stoi
                    FROM skaters
                    WHERE skater_id={skater_id}
                        AND date>='{first}' 
                        AND date<'{last}'"""
                skdata = self.get_data(q)
                if len(skdata) < 10: continue

                # Team Games Block
                team = tids[idx]
                q = f"""SELECT date as tdt FROM teams 
                        WHERE team_id={team}
                        ORDER BY date"""
                tgames = list(self.get_data(q)["tdt"])
                tidx = tgames.index(last)
                tfirst = tgames[tidx-10]
                tprev = tgames[tidx-1]
                tlast = tgames[tidx]

                # Team Stats Block
                q = f"""SELECT 
                    skater_assists_toi as tatoi,
                    skater_shots_toi as tstoi
                    FROM teams
                    WHERE team_id={team}
                        AND date>='{tfirst}' 
                        AND date<'{tlast}'"""
                tmdata = self.get_data(q)
                if len(tmdata) < 10: continue

                # Opp Games Block
                opp = oids[idx]
                q = f"""SELECT date as odt FROM teams 
                        WHERE team_id={opp}
                        ORDER BY date"""
                ogames = list(self.get_data(q)["odt"])
                oidx = ogames.index(last)
                ofirst = ogames[oidx-10]
                oprev = ogames[oidx-1]
                olast = ogames[oidx]

                # Opp Stats Block
                q = f"""SELECT 
                    skater_blocks_toi as obtoi,
                    skater_hits_toi as ohtoi,
                    defenseman_blocks_toi as odhtoi,
                    defenseman_hits_toi as odbtoi,
                    goaltender_shots_against_toi as osatoi,
                    goaltender_goals_against_toi as ogatoi,
                    goaltender_save_percentage_toi as osvptoi
                    FROM teams
                    WHERE team_id={opp}
                        AND date>='{ofirst}' 
                        AND date<'{olast}'"""
                opdata = self.get_data(q)
                if len(opdata) < 10: continue

                # Team Flat Data Block
                q = f"""SELECT is_home FROM teams WHERE date='{tlast}'"""
                tishome  = self.get_data(q)
                tprevdate = datetime.strptime(tprev, "%Y-%m-%d %H:%M:%S")
                tlastdate = datetime.strptime(tlast, "%Y-%m-%d %H:%M:%S")
                tdelta = tlastdate - tprevdate
                tdelta = tdelta.days if tdelta.days < 4 else 4
                ha = self.to_onehot(tishome["is_home"][0], 2)
                tdr = self.to_onehot(tdelta-1, 4)

                # Opp Flat Data Block
                oprevdate = datetime.strptime(oprev, "%Y-%m-%d %H:%M:%S")
                olastdate = datetime.strptime(olast, "%Y-%m-%d %H:%M:%S")
                odelta = olastdate - oprevdate
                odelta = odelta.days if odelta.days < 4 else 4
                odr = self.to_onehot(odelta-1, 4)

                # Create Label
                lab = labels[idx]
                lab = lab if lab < 4 else 4
                labvec = self.to_labelhot(lab, 5)

                # Compilation
                seq = np.hstack((
                    skdata.to_numpy(),
                    tmdata.to_numpy(),
                    opdata.to_numpy()
                ))
                flat = np.hstack((ha, tdr, odr))
        
                self.ppdb.insert({'skater_id': int(skater_id),
                                     'game_id': int(gids[idx]),
                                     'record_id': int(f'{skater_id}{gids[idx]}'),
                                     'seq': seq.tolist(), 
                                     'flat': flat.tolist(),
                                     'label': labvec.tolist()})
                
    def to_onehot(self, idx, max):
        vec = np.zeros(max)
        vec[idx] = 1
        return vec
    
    def to_labelhot(self, idx, max):
        vec = np.zeros(max)
        vec[:idx+1] = 1
        return vec