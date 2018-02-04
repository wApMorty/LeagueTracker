# LeagueTracker
Tracker automatisé d'historique League of Legends pour stocker et analyser les données des parties d'un utilisateur

Le tracker se décompose en 2 parties:
* Un script de tracking qui tourne en background, qui va envoyer des request à l'API Riot pour récuperer les données et les stocker
* Un script d'exploitation des données qui permettra d'accéder aux données, en les visualisant sous forme de courbes, avec des parametres qu'on indiquera à chaque fois.
