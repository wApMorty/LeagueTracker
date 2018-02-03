"""
Created on 03/02/2018 

@author: Paul JANSEN
"""

"""
Objectif : Mettre en place un tracker qui s'execute à chaque fin de game, va interroger l'API Riot pour avoir les infos
du match, et les stock dans un fichier texte/CSV

PART 1 : Comprendre comment fonctionne les API, request toutes les infos necessaires aux stats
PART 2 : Stocker les infos dans un fichier texte/CSV
PART 2 : Automatiser l'execution du script avec detection de fin de game. (impose de faire tourner le script en
         background en permanence => Need quelque chose de leger pour ne pas impacter les performances du PC)
"""

"""
Probleme 1: 'Rate limit exceeded' : Pas possible de s'en debarasser ? Request op.gg au lieu de Riot ?
Probleme 2: Key Error : 0, probablement lie au probleme 1
Probleme 3: L'API Riot est protegee par un systeme de cle dynamique qu'il faut recuperer toutes les 24h. Pas contournable ?
"""
#----------------------------------------------------#
#                                                    #
#                       IMPORTS                      #
#                                                    #
#----------------------------------------------------#

import requests

#----------------------------------------------------#
#                                                    # 
#                      CONSTANTES                    #
#                                                    #
#----------------------------------------------------#

summonerName = "MVP%20Morty"
region = "euw1"
APIKey = "RGAPI-0b343d23-0774-4f42-b007-fbe647fbd74d"

#----------------------------------------------------#
#                                                    #
#                     FONCTIONS                      #
#                                                    #
#----------------------------------------------------#

#Entree : String summonerName
#Sortie : json summonerData
def requestSummonerData(summonerName):
    #Creation de l'URL pour aller recuperer le fichier json
    URL = "https://"+region+".api.riotgames.com/lol/summoner/v3/summoners/by-name/"+summonerName+"?api_key="+APIKey
    #Request the URL
    response = requests.get(URL)
    return response.json()

#Entree : int accountID
#Sortie : json liste des 20 derniers matchs
def requestRecentMatchList(accountID):
    #Creation de l'URL pour aller recuperer le fichier json
    URL = "https://"+region+".api.riotgames.com/lol/match/v3/matchlists/by-account/"+str(accountID)+"/recent?api_key="+APIKey
    #Request the URL
    response = requests.get(URL)
    return response.json()

#Entree : int ID Match
#Sortie : json infos match
def requestMatch(matchID) :
    #Creation de l'URL pour aller recuperer le fichier json
    URL = "https://"+region+".api.riotgames.com/lol/match/v3/matches/"+str(matchID)+"?api_key="+APIKey
    #Request the URL
    response = requests.get(URL)
    return response.json()

#Entree : None
#Sortie : Patch le plus recent
def requestPatch() :
    #Creation de l'URL pour aller recuperer le fichier json
    URL = "https://"+region+".api.riotgames.com/lol/static-data/v3/versions?api_key="+APIKey
    #Request the URL
    response = requests.get(URL)
    return response.json()[0]

#Entree : int summonerId, lastMatchInfo car pas encore declare et pas envie de def la fonction plus tard.
#Sortie : int participantId obtenu dans le lastMatchInfo
def getParticipantId(summonerId, lastMatchInfo):
    participantId = None
    for i in range (0, 10):
        if lastMatchInfo["participantIdentities"][i]["player"]["currentAccountId"] == summonerId :
            participantId = i+1
    return participantId

#Entree : int participantID, lastMatchInfo car pas encore declare et pas envie de def la fonction plus tard
#Sortie : Le role joue pendant la game.
def getMyRole(participantID,lastMatchInfo):
    role = None
    for i in range (0, 10):
        if lastMatchInfo['participants'][i]["participantId"] == participantID :
            role = lastMatchInfo['participants'][i]["timeline"]["lane"]
    return role

#Entree : lastMatchInfo car pas encore declare, int myParticipantId pour eviter de s'auto selectionner, myRole pour chercher l'autre joueur avec le meme role
#Sortie : le participantId du laner adverse
def getEnemy(lastMatchInfo, myParticipantId, myRole):
    enemyId = None
    for i in range(0, 10):
        if (lastMatchInfo['participants'][i]["timeline"]["lane"]==myRole and lastMatchInfo['participants'][i]["participantId"]!=myParticipantId) :
            enemyId = lastMatchInfo['participants'][i]["participantId"]
    return enemyId

#Entree : lastMatchInfo car pas encore declare, int myParticipantId pour me retrouver dans la liste
#Sortie : l'id du champion joue pendant la game
def getChampionId(lastMatchInfo, myParticipantId):
    championId = None
    for i in range(0,10):
        if lastMatchInfo['participants'][i]["participantId"] == myParticipantId:
            championId = lastMatchInfo['participants'][i]["championId"]
    return championId

#Entree : int championId pour chercher le champion dans la database, String patch, necessaire pour la request
#Sortie : String champion joue
def getChampion(championId, patch):
    champion = None
    URL = "https://"+region+".api.riotgames.com/lol/static-data/v3/champions?locale=fr_FR&version="+patch[0]+"&champListData=skins&dataById=false&api_key="+APIKey
    response = requests.get(URL).json()
    championList = response["data"]
    print(championList)
    for i in range (0, 200):
        print(championList[i]['id'])
        if championList[i]['id'] == championId:
            champion = championList[i]['name']
    return champion


#----------------------------------------------------#
#                                                    #
#                PROGRAMME PRINCIPAL                 #
#                                                    #
#----------------------------------------------------#

#Need to find summoner id
#Request summoner data, get ID
summonerData = requestSummonerData(summonerName)
id = summonerData['id'] #OK
accountId = summonerData['accountId']#OK

#Potential need to draw a winrate by patch graph. Need to find the patch
patch = requestPatch()
print(patch)#OK

#Need to find information about last match
#Request recent match list, get the last one and store its ID. Then search by game ID to find more inforamtion
recentMatchList = requestRecentMatchList(accountId) #OK
lastMatchID = recentMatchList['matches'][0]['gameId'] #OK

lastMatchInfo = requestMatch(lastMatchID) #WIP : Extraction des infos pertinentes pour analyse statistique

#Besoin de parcourir les joueurs pour trouver le participantId, ainsi que celui du laner adverse
myParticipantId = getParticipantId(accountId,lastMatchInfo)
myRole = getMyRole(myParticipantId, lastMatchInfo)
enemyParticipantId = getEnemy(lastMatchInfo, myParticipantId, myRole)

#Recuperation des infos sur le matchup (champion joue, champion en face)
myChampionId = getChampionId(lastMatchInfo, myParticipantId)
myChampion = getChampion(myChampionId, patch) # <= Key Error : 0

print(myChampion)