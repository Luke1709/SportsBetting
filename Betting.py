import pandas as pd
import numpy as np
import bs4 as bs
import urllib.request
from bs4 import BeautifulSoup
import requests
import json
from scipy.stats import poisson

def getOdds(Home, Away, Matchweek):

    Gameweek = 20   # Needs to be altered on a game by game basis

    # Teams in each league
    data = {'Name':['Arsenal','Aston Villa','Brentford','Brighton','Burnley','Chelsea','Crystal Palace','Everton','Leeds','Leicester','Liverpool','Manchester City','Manchester United','Newcastle United','Norwich City','Southampton','Tottenham','Watford','West Ham','Wolves'],'Stats Name':['Arsenal','Aston Villa','Brentford','Brighton','Burnley','Chelsea','Crystal Palace','Everton','Leeds','Leicester','Liverpool','Manchester City','Manchester United','Newcastle United','Norwich','Southampton','Tottenham','Watford','West Ham','Wolverhampton Wanderers']}
    PremierLeague = pd.DataFrame(data)

    data = {'Name':['Alaves','Athletic Club','Atletico Madrid','Barcelona','Cadiz','Celta Vigo','Elche','Espanyol','Getafe','Granada','Levante','Mallorca','Osasuna','Rayo Vallecano','Real Betis','Real Madrid','Real Sociedad','Sevilla','Valencia','Villarreal'],'Stats Name':['Alaves','Athletic Club','Atletico Madrid','Barcelona','Cadiz','Celta Vigo','Elche','Espanyol','Getafe','Granada','Levante','Mallorca','Osasuna','Rayo Vallecano','Real Betis','Real Madrid','Real Sociedad','Sevilla','Valencia','Villarreal']}
    LaLiga = pd.DataFrame(data)

    data = {'Name': ['Arminia Bielefel','Augsburg','Bayer Leverkusen','Bayern Munich','Bochum','Borussia Dortmund','Borussia M.Gladback', 'Eintracht Frankfurt','FC Cologne','Freiburg','Greuther Fuerth','Hertha Berlin','Hoffenheim','Mainz 05','RB Leipzig','Union Berlin','Vfb Stuttgart','Wolfsburg'], 'Stats Name': ['Arminia Bielefel','Augsburg','Bayer Leverkusen','Bayern Munich','Bochum','Borussia Dortmund','Borussia M.Gladback', 'Eintracht Frankfurt','FC Cologne','Freiburg','Greuther Fuerth','Hertha Berlin','Hoffenheim','Mainz 05','RasenBallsport Leipzig','Union Berlin','Vfb Stuttgart','Wolfsburg']}
    Bundesliga = pd.DataFrame(data)

    data = {'Name': ['AC Milan','Atalanta','Bologna','Cagliari','Empoli','Fiorentina','Genoa','Inter','Juventus','Lazio','Napoli','Roma','Salernitana','Sampdoria','Sassuolo','Spezia','Torino','Udinese','Venezia','Verona'], 'Stats Name': ['AC Milan','Atalanta','Bologna','Cagliari','Empoli','Fiorentina','Genoa','Inter','Juventus','Lazio','Napoli','Roma','Salernitana','Sampdoria','Sassuolo','Spezia','Torino','Udinese','Venezia','Verona']}
    SerieA = pd.DataFrame(data)

    data = {'Name': ['Angers','Bordeaux','Brest','Clermont Foot','Lens','Lille','Lorient','Lyon','Marseille','Metz','Monaco','Montpellier','Nantes','Nice','PSG','Reims','Rennes','Saint-Ettiene','Strasbourg','Troyes'], 'Stats Name': ['Angers','Bordeaux','Brest','Clermont Foot','Lens','Lille','Lorient','Lyon','Marseille','Metz','Monaco','Montpellier','Nantes','Nice','Paris Saint Germain','Reims','Rennes','Saint-Ettiene','Strasbourg','Troyes']}
    League1 = pd.DataFrame(data)

    def lineuplink(team):
        if team in PremierLeague.values:
            index = PremierLeague.index
            condition = PremierLeague['Name'] == team
            team_indices = index[condition]
            team_indices_list = team_indices.tolist()
            team_link = PremierLeague['Stats Name'][team_indices_list]
        elif team in SerieA.values:
            index = SerieA.index
            condition = SerieA['Name'] == team
            team_indices = index[condition]
            team_indices_list = team_indices.tolist()
            team_link = SerieA['Stats Name'][team_indices_list]
        elif team in Bundesliga.values:
            index = Bundesliga.index
            condition = Bundesliga['Name'] == team
            team_indices = index[condition]
            team_indices_list = team_indices.tolist()
            team_link = Bundesliga['Stats Name'][team_indices_list]
        elif team in League1.values:
            index = League1.index
            condition = League1['Name'] == team
            team_indices = index[condition]
            team_indices_list = team_indices.tolist()
            team_link = League1['Stats Name'][team_indices_list]
        else:
            index = LaLiga.index
            condition = LaLiga['Name'] == team
            team_indices = index[condition]
            team_indices_list = team_indices.tolist()
            team_link = LaLiga['Stats Name'][team_indices_list]
        team_link = str(team_link.tolist())
        team_link = team_link[2:len(team_link)-2]
        link = 'https://understat.com/team/' + team_link + '/2021'
        return link
    
    # Web scrape for predicted lineups for a specific game:

    def get_lineups(Home, Away):

        #ensure that the home/away team is inputted as a string
        #using https://www.sportsgambler.com/lineups/football/ to find teams

        def get_link(): # only one team is needed to find league
            if Home in League1.values:
                link = 'https://www.rotowire.com/soccer/lineups.php?league=FRAN'
            elif Home in PremierLeague.values:
                link = 'https://www.rotowire.com/soccer/lineups.php'
            elif Home in Bundesliga.values:
                link = 'https://www.rotowire.com/soccer/lineups.php?league=BUND'
                return link
            elif Home in SerieA.values:
                link = 'https://www.rotowire.com/soccer/lineups.php?league=SERI'
                return link
            elif Home in LaLiga.values:
                link = 'https://www.rotowire.com/soccer/lineups.php?league=LIGA'
            else:
                print("Team name is incorrect or does not play in these divisions")
            return link

        link = get_link()
        url = link
        site = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(site, 'lxml')


        League_Lineups = soup.find_all(class_="lineup is-soccer") # shows all games

        # loop to select games that have not been played
        i = 0
        Home_Teams = []
        while i < len(League_Lineups):
            dummy_var = League_Lineups[i].find_all(class_="lineup__mteam is-home")
            Home_Teams.append(dummy_var)
            i += 1
        # search for all the games lineup boxes 
        # in each lineup box find lineup__matchup
        i = 0
        #print(len(League_Lineups))  #prints the number of games
        while i < len(League_Lineups):
            #Home_Teams = League_Lineups[i].find_all(class_="lineup__mteam is-home")
            html = Home_Teams[i]
            html = str(html)
            parser = BeautifulSoup(html)
            home = parser.text.strip()
            #print(home)
            if Home in home: #if string contains home???
                break
            else:
                i += 1
                continue
            break
        #print(i)
        #print(League_Lineups[0])
        
        #CODE WORKS TIL HERE
        Lineups_class = League_Lineups[i].find_all(class_='lineup__main')
        #print(len(Lineups_class))
        Home_Lineup = Lineups_class[0].find_all(class_='lineup__list is-home')  
        Away_Lineup = Lineups_class[0].find_all(class_='lineup__list is-visit')
        #print(len(Home_Lineup))
        h = Home_Lineup[0].find_all(class_='lineup__player')
        a = Away_Lineup[0].find_all(class_='lineup__player')
        global Home_team_lineup
        global Away_team_Lineup
        Home_team_lineup = []
        Away_team_Lineup = []
        for j in range(0,11):
            html = h[j]
            html2 = a[j]
            html = str(html)
            html2 = str(html2)
            parser = BeautifulSoup(html)
            parser2 = BeautifulSoup(html2)
            player_home = parser.text.strip()
            player_away = parser2.text.strip()
            player_home = player_home[2:] # remove the players positions
            player_away = player_away[2:]
            Home_team_lineup.append(player_home)
            Away_team_Lineup.append(player_away)

        return Home_team_lineup, Away_team_Lineup

    def get_xG(Home, Away):

        Home_link = lineuplink(Home)
        Away_link = lineuplink(Away)

        # Home xG first
        global HomexG 
        global home_player_ids
        global AwayxG
        global away_player_ids
        HomexG = []
        home_player_ids = []
        AwayxG = []
        away_player_ids = []

        res = requests.get(Home_link)
        soup = BeautifulSoup(res.content,'lxml')
        scripts = soup.find_all('script')

        strings = scripts[3].string
        ind_start = strings.index("('")+2
        ind_end = strings.index("')")

        json_data = strings[ind_start:ind_end]
        json_data = json_data.encode('utf8').decode('unicode_escape')

        data = json.loads(json_data)

        # extract the last word from expected lineups
        Home_names = []
        for i in Home_team_lineup:
            a = i.split()
            Home_names.append(a[-1])

        for i in Home_names:
            for index in range(len(data)):
                for key in data[index]:
                    if key == 'player_name':
                        if i in data[index][key]:
                            player_id = data[index]['id']
                            dummy = np.divide(float(data[index]['xG']),float(data[index]['time']))
                            HomexG.append(dummy*90)
                            home_player_ids.append(player_id)
                        else:
                            continue

        
        res = requests.get(Away_link)
        soup = BeautifulSoup(res.content,'lxml')
        scripts = soup.find_all('script')

        strings = scripts[3].string
        ind_start = strings.index("('")+2
        ind_end = strings.index("')")

        json_data = strings[ind_start:ind_end]
        json_data = json_data.encode('utf8').decode('unicode_escape')

        data = json.loads(json_data)

        # extract the last word from expected lineups
        Away_names = []
        for i in Away_team_Lineup:
            a = i.split()
            Away_names.append(a[-1])

        for i in Away_names:
            for index in range(len(data)):
                for key in data[index]:
                    if key == 'player_name':
                        if i in data[index][key]:
                            player_id = data[index]['id']
                            dummy = np.divide(float(data[index]['xG']),float(data[index]['time']))
                            AwayxG.append(dummy*90)
                            away_player_ids.append(player_id)
                        else:
                            continue

        HomexG = np.sum(HomexG)
        AwayxG = np.sum(AwayxG)
        return HomexG, AwayxG

    def xGAdj(Home, Away, HomexG, AwayxG):
        
        # Adjust the xG values based upon opponents defence strength, whether they are home/away

        # Home/Away adjustment
        HomexG = HomexG * 1.1 # home teams score 5% more goals  THEORETICAL
        AwayxG = AwayxG * 0.95 # away teams score 5% less goals  THEORETICAL

        def oppStrength(team):

            url = lineuplink(team)
            res = requests.get(url) 
            soup = BeautifulSoup(res.content,'lxml')
            scripts = soup.find_all('script')
            strings = scripts[1].string
            ind_start = strings.index("('")+2
            ind_end = strings.index("')")

            json_data = strings[ind_start:ind_end]
            json_data = json_data.encode('utf8').decode('unicode_escape')

            data = json.loads(json_data)
            # using last 5 games, calculate the average of actual goals / xG against 
            # using last 5 games, calculate goal form, see if they are scoring more than their xG
            n = 5 # number of games
            global defence
            global attack
            defence = []
            attack = []
            for i in range(Gameweek-n,Gameweek-1):
                side = data[i]['side']
                xG_ingame = data[i]['xG'][side]
                actual_goals = data[i]['goals'][side]
                if xG_ingame is None:
                    continue
                else:
                    attack.append(float(actual_goals)/float(xG_ingame))
                if side == 'h':
                    side = 'a'
                else:
                    side = 'h'
                xG_ingame = data[i]['xG'][side]
                actual_goals = data[i]['goals'][side]
                if xG_ingame is None:
                    defence
                else:
                    defence.append(float(actual_goals)/float(xG_ingame))
            defence = np.mean(defence)    
            attack = np.mean(attack)
            return defence, attack
        global Home_attack
        global Home_defence
        global Away_attack
        global Away_defence
        oppStrength(Home)
        Home_attack = attack
        Home_defence = defence
        oppStrength(Away)
        Away_attack = attack
        Away_defence = defence


        HomexG = HomexG * Home_attack * Away_defence
        AwayxG = AwayxG * Away_attack * Home_defence

        return HomexG, AwayxG

    get_lineups(Home, Away)
    get_xG(Home, Away)
    xGAdj(Home, Away, HomexG, AwayxG)

    global Teams_xG
    Teams_xG = [[0,poisson.pmf(k=0,mu=HomexG),poisson.pmf(k=0,mu=AwayxG)],[1,poisson.pmf(k=1,mu=HomexG),poisson.pmf(k=1,mu=AwayxG)],[2,poisson.pmf(k=2,mu=HomexG),poisson.pmf(k=2,mu=AwayxG)],[3,poisson.pmf(k=3,mu=HomexG),poisson.pmf(k=3,mu=AwayxG)],[4,poisson.pmf(k=4,mu=HomexG),poisson.pmf(k=4,mu=AwayxG)]]

    # need to calculate all the ways to see over x goals
    no_goals = Teams_xG[0][1]*Teams_xG[0][2]    # under 0.5 goals    # 0-0
    two_goals = no_goals + (Teams_xG[0][1]*Teams_xG[1][2]) + (Teams_xG[0][2]*Teams_xG[1][1])    # under 1.5 goals    # 1-0 / 0-1
    three_goals = two_goals + (Teams_xG[2][1]*Teams_xG[0][2]) + (Teams_xG[0][1]*Teams_xG[2][2]) + (Teams_xG[1][1]*Teams_xG[1][2])  # under 2.5 goals   # 2-0 / 0-2 / 1-1
    #four_goals = three_goals + 

    over_no_goals = 1 - no_goals
    over_one_goals = 1 - two_goals
    over_two_goals = 1 - three_goals


    over_no_goals_odds = 1/over_no_goals
    over_one_goals_odds = 1/over_one_goals
    over_two_goals_odds = 1/over_two_goals

    data = {'Probability' : [over_no_goals, over_one_goals, over_two_goals], 'Odds' : [over_no_goals_odds, over_one_goals_odds, over_two_goals_odds]}
    Summary = pd.DataFrame(data)
    Summary.index = ['Over 0.5 goals', 'Over 1.5 goals', 'Over 2.5 goals']


    print('Game : ' + Home + ' vs ' + Away)
    print(Home + ' xG : ' + str(HomexG))
    print(Away + ' xG : ' + str(AwayxG))


    return Summary


getOdds('Southampton','Brentford',20)

# This script works better as a python notebook.

