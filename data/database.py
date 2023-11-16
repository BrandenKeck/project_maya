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
class BetData(Base):

    __tablename__ = "bets"
    idx: Mapped[int] = mapped_column(primary_key=True)
    
    def __repr__(self):
        return f"BetData({self.idx})"

# Team Class
class TeamData(Base):

    __tablename__ = "teams"
    idx: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[str] = mapped_column(String())
    team_name: Mapped[str] = mapped_column(String())
    game_id: Mapped[str] = mapped_column(String())
    date: Mapped[str] = mapped_column(String())
    is_home: Mapped[int] = mapped_column(Numeric())
    skater_goals_toi: Mapped[float] = mapped_column(Numeric())
    skater_assists_toi: Mapped[float] = mapped_column(Numeric())
    skater_shots_toi: Mapped[float] = mapped_column(Numeric())
    skater_blocks_toi: Mapped[float] = mapped_column(Numeric())
    skater_hits_toi: Mapped[float] = mapped_column(Numeric())
    skater_takeaways_toi: Mapped[float] = mapped_column(Numeric())
    skater_giveaways_toi: Mapped[float] = mapped_column(Numeric())
    defenseman_blocks_toi: Mapped[float] = mapped_column(Numeric())
    defenseman_hits_toi: Mapped[float] = mapped_column(Numeric())
    goaltender_shots_against_toi: Mapped[float] = mapped_column(Numeric())
    goaltender_goals_against_toi: Mapped[float] = mapped_column(Numeric())
    goaltender_save_percentage_toi: Mapped[float] = mapped_column(Numeric())
    record_id: Mapped[str] = mapped_column(String())

    def __repr__(self):
        return f"TeamData(team={self.team_name}, game={self.game_id})"

# Skater Class
class SkaterData(Base):

    __tablename__ = "skaters"
    idx: Mapped[int] = mapped_column(primary_key=True)
    skater_id: Mapped[str] = mapped_column(String())
    skater_name: Mapped[str] = mapped_column(String())
    team_id: Mapped[str] = mapped_column(String())
    opp_id: Mapped[str] = mapped_column(String())
    game_id: Mapped[str] = mapped_column(String())
    date: Mapped[str] = mapped_column(String())
    is_home: Mapped[int] = mapped_column(Numeric())
    toi: Mapped[float] = mapped_column(Numeric())
    goals: Mapped[int] = mapped_column(Numeric())
    assists: Mapped[int] = mapped_column(Numeric())
    shots: Mapped[int] = mapped_column(Numeric())
    blocks: Mapped[int] = mapped_column(Numeric())
    hits: Mapped[int] = mapped_column(Numeric())
    takeaways: Mapped[int] = mapped_column(Numeric())
    giveaways: Mapped[int] = mapped_column(Numeric())
    goals_toi: Mapped[float] = mapped_column(Numeric())
    assists_toi: Mapped[float] = mapped_column(Numeric())
    shots_toi: Mapped[float] = mapped_column(Numeric())
    blocks_toi: Mapped[float] = mapped_column(Numeric())
    hits_toi: Mapped[float] = mapped_column(Numeric())
    takeaways_toi: Mapped[float] = mapped_column(Numeric())
    giveaways_toi: Mapped[float] = mapped_column(Numeric())
    record_id: Mapped[str] = mapped_column(String())

    def __repr__(self):
        return f"SkaterData(skater={self.skater_name}, game={self.game_id})"


# Goaltender Class
class GoaltenderData(Base):

    __tablename__ = "goaltenders"
    idx: Mapped[int] = mapped_column(primary_key=True)
    goaltender_id: Mapped[str] = mapped_column(String())
    goaltender_name: Mapped[str] = mapped_column(String())
    team_id: Mapped[str] = mapped_column(String())
    opp_id: Mapped[str] = mapped_column(String())
    game_id: Mapped[str] = mapped_column(String())
    date: Mapped[str] = mapped_column(String())
    is_home: Mapped[int] = mapped_column(Numeric())
    toi: Mapped[float] = mapped_column(Numeric())
    saves: Mapped[int] = mapped_column(Numeric())
    shots_against: Mapped[int] = mapped_column(Numeric())
    goals_against: Mapped[int] = mapped_column(Numeric())
    save_percentage: Mapped[float] = mapped_column(Numeric())
    shots_against_toi: Mapped[float] = mapped_column(Numeric())
    goals_against_toi: Mapped[float] = mapped_column(Numeric())
    save_percentage_toi: Mapped[float] = mapped_column(Numeric())
    record_id: Mapped[str] = mapped_column(String())

    def __repr__(self):
        return f"GoaltenderData(skater={self.goaltender_name}, game={self.game_id})"

class LakshmiDatabase():

    def __init__(self):
        self.ppq = Query()
        self.ppdb = TinyDB("data/preprocessed.json")
        self.engine = create_engine("sqlite:///data/data.db")
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
    
    def add_team_data(self, data):
        exists = bool(self.session.query(TeamData).filter_by(record_id=data["record_id"]).first())
        if not exists:
            team = TeamData(
                team_id=data["team_id"],
                team_name=data["team_name"],
                game_id=data["game_id"],
                date=data["date"],
                is_home=data["is_home"],
                skater_goals_toi=data["skater_goals_toi"],
                skater_assists_toi=data["skater_assists_toi"],
                skater_shots_toi=data["skater_shots_toi"],
                skater_blocks_toi=data["skater_blocks_toi"],
                skater_hits_toi=data["skater_hits_toi"],
                skater_takeaways_toi=data["skater_takeaways_toi"],
                skater_giveaways_toi=data["skater_giveaways_toi"],
                defenseman_blocks_toi=data["defenseman_blocks_toi"],
                defenseman_hits_toi=data["defenseman_hits_toi"],
                goaltender_shots_against_toi=data["goaltender_shots_against_toi"],
                goaltender_goals_against_toi=data["goaltender_goals_against_toi"],
                goaltender_save_percentage_toi=data["goaltender_save_percentage_toi"],
                record_id=data["record_id"]
            )
            self.session.add(team)

    def add_skater_data(self, data):
        exists = bool(self.session.query(SkaterData).filter_by(record_id=data["record_id"]).first())
        if not exists:
            sk8r = SkaterData(
                skater_id=data["skater_id"],
                skater_name=data["skater_name"],
                team_id=data["team_id"],
                opp_id=data["opp_id"],
                game_id=data["game_id"],
                date=data["date"],
                is_home=data["is_home"],
                toi=data["toi"],
                goals=data["goals"],
                assists=data["assists"],
                shots=data["shots"],
                blocks=data["blocks"],
                hits=data["hits"],
                takeaways=data["takeaways"],
                giveaways=data["giveaways"],
                goals_toi=data["goals_toi"],
                assists_toi=data["assists_toi"],
                shots_toi=data["shots_toi"],
                blocks_toi=data["blocks_toi"],
                hits_toi=data["hits_toi"],
                takeaways_toi=data["takeaways_toi"],
                giveaways_toi=data["giveaways_toi"],
                record_id=data["record_id"]
            )
            self.session.add(sk8r)

    def add_goaltender_data(self, data):
        exists = bool(self.session.query(GoaltenderData).filter_by(record_id=data["record_id"]).first())
        if not exists:
            gt = GoaltenderData(
                goaltender_id=data["goaltender_id"],
                goaltender_name=data["goaltender_name"],
                team_id=data["team_id"],
                opp_id=data["opp_id"],
                game_id=data["game_id"],
                date=data["date"],
                is_home=data["is_home"],
                toi=data["toi"],
                saves=data["saves"],
                shots_against=data["shots_against"],
                goals_against=data["goals_against"],
                save_percentage=data["save_percentage"],
                shots_against_toi=data["shots_against_toi"],
                goals_against_toi=data["goals_against_toi"],
                save_percentage_toi=data["save_percentage_toi"],
                record_id=data["record_id"]
            )
            self.session.add(gt)

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