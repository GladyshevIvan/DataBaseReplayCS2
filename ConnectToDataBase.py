import mysql.connector
from ParseDemo import StatsFromDemo
from create_hash import set_game_id, make_hash


class CS2DataBase:
    def __init__(self, database_name="CS2_Tournament"):
        self.database_name = database_name
        self.mydb = self.connect_to_database()
        if self.mydb:
            self.create_tables()

    def connect_to_database(self):
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="user",
                password="password"
            )

            mycursor = mydb.cursor()

            mycursor.execute(
                f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{self.database_name}'")
            exists = mycursor.fetchone()

            if not exists:
                mycursor.execute(f"CREATE DATABASE {self.database_name}")
                mydb.commit()

            mydb = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="user",
                password="password",
                database=self.database_name

            )

            return mydb

        except mysql.connector.Error as err:
            print(f"Ошибка при подключении к базе данных: {err}")
            return None


    def create_tables(self):
        mycursor = self.mydb.cursor()

        mycursor.execute("""
      CREATE TABLE IF NOT EXISTS Teams (
      team_id BIGINT PRIMARY KEY, 
      team_name VARCHAR(255)
      );
       """)

        mycursor.execute("""
      CREATE TABLE IF NOT EXISTS Players (
      steamid BIGINT PRIMARY KEY,
      name VARCHAR(255),
      team_id BIGINT,
      FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE SET NULL
      );
        """)

        mycursor.execute("""
      CREATE TABLE IF NOT EXISTS Games (
      game_id BIGINT PRIMARY KEY,
      map VARCHAR(255),
      date VARCHAR(255)
      );
       """)

        mycursor.execute("""
      CREATE TABLE IF NOT EXISTS Scores (
       sсore_id INT PRIMARY KEY AUTO_INCREMENT,
       game_id BIGINT,
       team1_id BIGINT,
       team2_id BIGINT,
       score1 INT,
       score2 INT,
       FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE SET NULL,
       FOREIGN KEY (team1_id) REFERENCES Teams(team_id) ON DELETE SET NULL,
       FOREIGN KEY (team2_id) REFERENCES Teams(team_id) ON DELETE SET NULL
       );
       """)

        mycursor.execute("""
      CREATE TABLE IF NOT EXISTS Stats (
       stats_id INT PRIMARY KEY AUTO_INCREMENT,
       steamid BIGINT,
       game_id BIGINT,
       kills INT,
       deaths INT,
       assists INT,
       FOREIGN KEY (steamid) REFERENCES Players(steamid) ON DELETE SET NULL,
       FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE SET NULL
       );
       """)

        self.mydb.commit()


    def insert_cs2_stats_to_db(self, raw_dem, date_and_time):
        cs2_stats = StatsFromDemo(raw_dem, date_and_time)
        players_stats = cs2_stats.players_stats
        total_score = cs2_stats.total_score
        map = cs2_stats.map
        date_and_time = cs2_stats.date_and_time
        new_id = cs2_stats.game_id

        team_hash_names = {}

        mycursor = self.mydb.cursor()

        mycursor.execute("INSERT INTO Games (game_id, map, date) VALUES (%s, %s, %s)",
                         (new_id, map, date_and_time))  # Добавление игры

        for team_bio in total_score.values():  # Добавление команд
            team_full_name = team_bio['team']
            team_hash_name = make_hash(team_full_name)
            team_hash_names[team_full_name] = team_hash_name

            mycursor.execute("SELECT COUNT(*) FROM Teams WHERE team_id = %s", (team_hash_name,)) #Проверка есть ли уже команда в Базе Данных
            if mycursor.fetchone()[0] == 0:
                mycursor.execute("INSERT INTO Teams (team_id, team_name) VALUES (%s, %s)", (team_hash_name, team_full_name))

        team1, team2 = total_score.values()  # Добавление счёта
        mycursor.execute("INSERT INTO Scores (game_id, team1_id, team2_id, score1, score2) VALUES (%s, %s, %s, %s, %s)",
                         (new_id, team_hash_names[team1['team']], team_hash_names[team2['team']], team1['score'],
                          team2['score']))

        for player in players_stats:
            player_name = players_stats[player]['name']
            player_team_id = team_hash_names[players_stats[player]['team']]
            player_kills = players_stats[player]['kills']
            player_deaths = players_stats[player]['deaths']
            player_assists = players_stats[player]['assists']

            mycursor.execute("SELECT COUNT(*) FROM Players WHERE steamid = %s",
                             (player,))  # Проверка есть ли уже команда в Базе Данных
            if mycursor.fetchone()[0] == 0:
                mycursor.execute("INSERT INTO Players (steamid, name, team_id) VALUES (%s, %s, %s)",
                             (player, player_name, player_team_id))
            mycursor.execute("INSERT INTO Stats (steamid, game_id, kills, deaths, assists) VALUES (%s, %s, %s, %s, %s)",
                             (player, new_id, player_kills, player_deaths, player_assists))

        self.mydb.commit()


    def extract_player_stats(self, demo_id):
        mycursor = self.mydb.cursor()

        mycursor.execute('''
          SELECT Players.steamid, Players.name, Teams.team_name, Stats.kills, Stats.deaths, Stats.assists
          FROM Players JOIN Teams ON Players.team_id = Teams.team_id
          JOIN Stats ON Players.steamid = Stats.steamid
          WHERE Stats.game_id = %s
          ORDER BY Teams.team_name DESC, Stats.kills DESC;
          ''', (demo_id,))

        extracted_player_stats = {}
        for steamid, name, team, kills, deaths, assists in mycursor.fetchall():
            extracted_player_stats[steamid] = {'name': name, 'team': team, 'kills': kills, 'deaths': deaths,
                                               'assists': assists}

        return extracted_player_stats

    def extract_total_score(self, demo_id):
        mycursor = self.mydb.cursor()

        mycursor.execute('''
            SELECT 
                Teams.team_id, Teams.team_name,
                CASE
                    WHEN Scores.team1_id = Teams.team_id THEN Scores.score1
                    ELSE Scores.score2
                END AS score
            FROM Scores
            JOIN Teams ON Scores.team1_id = Teams.team_id OR Scores.team2_id = Teams.team_id
            WHERE Scores.game_id = %s;
        ''', (demo_id,))

        extracted_total_score = {}
        for team_id, team, score in mycursor.fetchall():
            extracted_total_score[team_id] = {'team': team, 'score': score}

        return extracted_total_score


    def extract_one_game_from_database(self, raw_name, date_and_time):
        demo_id = set_game_id(raw_name, date_and_time)

        player_stats = self.extract_player_stats(demo_id)
        total_score = self.extract_total_score(demo_id)

        return total_score, player_stats