from bs4 import BeautifulSoup
import re, urllib
from urllib import urlopen


def getTeams():   #returns team codes for all 30 teams 
    url = 'http://www.basketball-reference.com/leagues/NBA_2015_standings.html'
    f = urllib.urlopen(url)
    words = f.read().decode('utf-8')
    team_links = re.findall('<a href="/teams/(.+)/2015.html">', words)
    adj_team_links = []
    for i in team_links:  
        if i not in adj_team_links:
            adj_team_links.append(i)
    return adj_team_links

    
def getRatings(team_links):   #scrapes offensive, defensive ratings for each team  
    base_url = 'http://www.basketball-reference.com/teams/'
    end_url = '/2015.html'
    all_oRtg = {}
    all_dRtg = {}
    for i in team_links:
        full_url = base_url + i + end_url
        f = urllib.urlopen(full_url)
        words = f.read().decode('utf-8')
        rating_arr = re.findall('Off Rtg</span></a>: (.+) \(', words) #this scrapes a lot, must be cleaned
        oRtg = ''
        back_dRtg = ''
        dRtg = ''
        j = 0 #character indice
        rating_info = rating_arr[0]
        good_chars = ['0','1','2','3','4','5','6','7','8','9','.'] #characters we're looking for
        while rating_info[j] in good_chars:
            oRtg += rating_info[j]
            j = j+1   
        j = 1
        while rating_info[len(rating_info)-j] in good_chars:
            back_dRtg += rating_info[len(rating_info)-j] #working backwards, getting defensive rating
            j = j+1
        for k in range(0,len(back_dRtg)): #flipping the backwards value to normal
            dRtg += back_dRtg[len(back_dRtg)-k-1]  
        all_dRtg[i] = dRtg
        all_oRtg[i] = oRtg
    return all_oRtg, all_dRtg  

    
def getSchedule(team_links): #returns schedules for each team
    base_url = 'http://www.basketball-reference.com/teams/'
    end_url = '/2015_games.html'
    all_schedules = {}
    for i in team_links:
        all_opponents = []
        full_url = base_url + i + end_url
        f = urllib.urlopen(full_url)
        soup = BeautifulSoup(f.read())
        all_rows = soup.findAll('tr')
        for j in all_rows:
            row = str(j)
            if 'Box Score' in row:
                opponent = re.findall('<a href="/teams/(.+)/2015.html">', row)
                all_opponents.append(opponent)
        all_schedules[i] = all_opponents
    return all_schedules                           
    

def findAvg(schedule, off_, def_): #gets league averages of efficiency
    sum_off = 0
    sum_def = 0
    games = 0
    for key in off_:
        team_sched = schedule[key]
        num_gms = float(len(team_sched))
        games = games + num_gms
    for key in off_:
        team_sched = schedule[key]
        num_gms = float(len(team_sched))
        team_weight = num_gms/games
        sum_off = sum_off + team_weight * float(off_[key])
        sum_def = sum_def + team_weight * float(def_[key])
    return sum_off, sum_def    
        
        
def adjustRtg(off_, def_, oAvg, dAvg): #adjusts teams' efficiencies compared to league average
    adjO = {}
    adjD = {}
    for key in off_:
        adjO[key] = float(off_[key]) - oAvg
        adjD[key] = float(def_[key]) - dAvg        
    return adjO, adjD
    
def perfectRtg(schedule, adjO, adjD): #Modifies teams' ratings based off ratings of opponents
    newO = adjO
    newD = adjD
    for n in range(0, 100000):    
        placeholderO = {}
        placeholderD = {}
        for key in schedule:
            team_sched = schedule[key]
            num_gms = float(len(team_sched))
            sumD = 0
            sumO = 0
            for i in team_sched:
                opp = i[0]
                sumD = sumD + newD[opp]
                sumO = sumO + newO[opp]
            placeholderO[key] = adjO[key] + ((1 / num_gms) * sumD)  
            placeholderD[key] = adjD[key] + ((1 / num_gms) * sumO)
        newO = placeholderO
        newD = placeholderD
    for team in newD:
        newD[team] = abs(newD[team])
    return newO, newD          
        

def rateTeams(off_, def_): #this method not currently in use
    teamNames = []
    spreadValues = []
    for key in off_:
        spread = off_[key] + def_[key]
        if len(spreadValues) == 0:
            teamNames.append(key)
            spreadValues.append(spread)
        else:
            for i in range(0, len(spreadValues)):
                if spread >= spreadValues[i]:
                    spreadValues.insert(i, spread)
                    teamNames.insert(i, key)
                    break
            if key not in teamNames:
                spreadValues.append(spread)
                teamNames.append(key)
    for n in range(0, len(spreadValues)):
        print teamNames[n], spreadValues[n]                           


def readjustRtg(off_, def_, oAvg, dAvg): #Converts ratings from +/- to actual numbers
    finalO = {}
    finalD = {}
    for key in off_:
        finalO[key] = off_[key] + oAvg
        finalD[key] = dAvg - def_[key]
    return finalO, finalD     


def getDaysGames(): #gets list of games for a given day
    daily_sched = {}
    weekday = 'Wed'
    month = 'Nov'
    day = '12'
    year = '2014'
    full_date = weekday + ', ' + month + ' ' + day + ', ' + year
    
    url = 'http://www.basketball-reference.com/leagues/NBA_2015_games.html'
    f = urllib.urlopen(url)
    soup = BeautifulSoup(f.read())
    all_rows = soup.findAll('tr')
    for i in all_rows:
        row = str(i)
        if full_date in row:
            teams = re.findall('<a href="/teams/(.+)/2015.html">', row)
            daily_sched[teams[0]] = teams[1]      
    return daily_sched        
    

def getPace(team_links): #finds the pace of play for every team, and league average
    base_url = 'http://www.basketball-reference.com/teams/'
    end_url = '/2015.html'
    all_pace = {}
    sum_pace = 0
    for i in team_links:
        full_url = base_url + i + end_url
        f = urllib.urlopen(full_url)
        words = f.read().decode('utf-8')
        pace_data = re.findall('Pace</span></a>: (.+) \(', words)
        pace_info = pace_data[0]
        pace = ''
        j = 0
        good_chars = ['0','1','2','3','4','5','6','7','8','9','.'] #characters we're looking for
        while pace_info[j] in good_chars:
            pace += pace_info[j]
            j = j+1
        all_pace[i] = float(pace)
        sum_pace = sum_pace + float(pace)       
    return (sum_pace / 30), all_pace


def calculateTempo(teamA, teamB, league_pace, all_pace): #predicts number of possessions for a matchup
    teamA_pace = all_pace[teamA]
    teamB_pace = all_pace[teamB]
    tempo = (teamA_pace / league_pace) * (teamB_pace / league_pace) * league_pace
    return tempo


def predictGames(daily_sched, league_pace, all_pace, offAvg, defAvg, finalO, finalD): #predicts scores of games
    for key in daily_sched:
        teamA = key
        teamB = daily_sched[key]
        tempo = calculateTempo(teamA, teamB, league_pace, all_pace)
        teamA_output = int((tempo / 100.00) * (finalO[teamA] / offAvg) * (finalD[teamB] / defAvg) * offAvg)
        teamB_output = int((tempo / 100.00) * (finalO[teamB] / offAvg) * (finalD[teamA] / defAvg) * offAvg)
        print '======================'   
        print teamA, teamA_output, teamB, teamB_output


all_teams = getTeams()
print 'Gathered Teams'     
all_oRtg, all_dRtg = getRatings(all_teams)
print 'Gathered Ratings'
schedule = getSchedule(all_teams)
print 'Gathered Completed Schedules'
offAvg, defAvg = findAvg(schedule, all_oRtg, all_dRtg)
print 'Gathered League Averages'
adjO, adjD = adjustRtg(all_oRtg, all_dRtg, offAvg, defAvg)
print 'Adjusted Ratings'
newO, newD = perfectRtg(schedule, adjO, adjD)
print 'Perfected Ratings'
finalO, finalD = readjustRtg(newO, newD, offAvg, defAvg)
print 'Performed Final Adjustments on Ratings'
daily_sched = getDaysGames()
print 'Gathered Games for the Day'
league_pace, all_pace = getPace(all_teams) 
print 'Gathered Pace Data'
predictGames(daily_sched, league_pace, all_pace, offAvg, defAvg, finalO, finalD)
