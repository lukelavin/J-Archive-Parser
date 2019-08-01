import psycopg2


class DatabaseConnection:

    def __init__(self, connect_args=None):
        with open('password.txt') as f:
            password = f.readline()

        try:
            if connect_args is None:
                self.connection = psycopg2.connect('dbname=jeopardy user=luke password=' + password)
            else:
                self.connection = psycopg2.connect(connect_args)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
        except psycopg2.Error as e:
            print("Error connecting to database" + '\n' + e.pgcode + '\n' + e.pgerror)

    def close(self):
        try:
            self.cursor.close()
            self.connection.close()
        except psycopg2.Error as e:
            print("Error closing the connection." + '\n' + e.pgcode + '\n' + e.pgerror)

    def insert_parsed_game(self, episode_num, game_link):
        print('Inserting game into parsed list')
        self.cursor.execute('''
        INSERT INTO parsed_games(episode_num, game_link)
        VALUES (%s, %s);
        ''', (episode_num, game_link))

    def insert_season(self, name, start_date, end_date, total_games):
        print('Inserting season')
        self.cursor.execute('''
        INSERT INTO seasons (season_name, start_date, end_date, total_games)
        VALUES (%s, %s, %s, %s);
        ''', (name, start_date, end_date, total_games))

    def insert_contestant(self, name, notes, games_played, total_winnings):
        print('Inserting contestant')
        self.cursor.execute('''
        INSERT INTO contestants (name, notes, games_played, total_winnings)
        VALUES (%s, %s, %s, %s);
        ''', (name, notes, games_played, total_winnings))

    def insert_game(self, episode_num, season_id, air_date, notes, contestant1, contestant2, contestant3,
                    winner, score1, score2, score3):
        print(f'Inserting game {episode_num}')
        self.cursor.execute('''
        INSERT INTO
        games (episode_num, season_id, air_date, notes, contestant1, contestant2, contestant3, winner, score1, score2, score3)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        ''', (episode_num, season_id, air_date, notes, contestant1, contestant2, contestant3, winner,
              score1, score2, score3))

    def insert_question(self, game_id, value, daily_double, round, category, clue, response):
        # print('Inserting clue')
        self.cursor.execute('''
        INSERT INTO clues (game_id, value, daily_double, round, category, clue, response)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        ''', (game_id, value, daily_double, round, category, clue, response))

    def print_seasons(self):
        self.cursor.execute('SELECT * FROM seasons ORDER BY id;')
        seasons = self.cursor.fetchall()
        for season in seasons:
            print(season)

    def print_contestants(self):
        self.cursor.execute('SELECT * FROM contestants ORDER BY id;')
        contestants = self.cursor.fetchall()
        for contestant in contestants:
            print(contestant)

    def print_games(self):
        self.cursor.execute('SELECT * FROM games ORDER BY id;')
        games = self.cursor.fetchall()
        for game in games:
            print(game)

    def print_questions(self):
        self.cursor.execute('SELECT * FROM clues ORDER BY id;')
        questions = self.cursor.fetchall()
        for question in questions:
            print(question)

    def game_parsed(self, episode_num):
        self.cursor.execute('SELECT * FROM parsed_games WHERE episode_num=(%s)', (episode_num, ))
        episode_num_found = len(self.cursor.fetchall()) > 0
        return episode_num_found

    def update_contestant(self, name, notes=None,  games_played=None, total_winnings=None):
        if games_played is not None:
            self.cursor.execute('''
            UPDATE contestants
            SET games_played = (%s)
            WHERE name = (%s);''', (games_played, name))

        if notes is not None:
            self.cursor.execute('''
            UPDATE contestants
            SET notes = (%s)
            WHERE name = (%s);''', (notes, name))

        if total_winnings is not None:
            self.cursor.execute('''
            UPDATE contestants
            SET total_winnings = (%s)
            WHERE name = (%s);''', (total_winnings, name))

    def contestant_exists(self, name):
        self.cursor.execute('''SELECT * FROM contestants WHERE name = (%s);''', (name,))
        contestant = self.cursor.fetchone()
        return contestant is not None

    def get_contestant_games_played(self, name):
        self.cursor.execute('''SELECT games_played FROM contestants WHERE name = (%s);''', (name,))
        total_winnings = self.cursor.fetchone()
        return total_winnings[0]

    def get_contestant_winnings(self, name):
        self.cursor.execute('''SELECT total_winnings FROM contestants WHERE name = (%s);''', (name,))
        total_winnings = self.cursor.fetchone()
        return total_winnings[0]

    def get_contestant_id_from_name(self, name):
        self.cursor.execute('''SELECT id FROM contestants WHERE name = (%s);''', (name,))
        total_winnings = self.cursor.fetchone()
        return total_winnings[0]

    def get_game_from_episode_number(self, episode_number):
        self.cursor.execute('''SELECT id FROM games WHERE episode_num = (%s);''', (episode_number,))
        game_id = self.cursor.fetchone()
        return game_id[0]

    def setup_database(self):
        # Parsed Games Table
        self.cursor.execute('''
        CREATE TABLE parsed_games (
        id serial PRIMARY KEY,
        episode_num integer,
        game_link VARCHAR
        );
        ''')

        # Seasons Table
        self.cursor.execute('''
        CREATE TABLE seasons (
          id serial PRIMARY KEY,
          season_name VARCHAR(16),
          start_date DATE,
          end_date DATE,
          total_games integer
        );
        ''')

        # Contestants Table
        self.cursor.execute('''
        CREATE TABLE contestants (
          id serial PRIMARY KEY,
          name VARCHAR NOT NULL,
          notes VARCHAR,
          games_played integer NOT NULL,
          total_winnings integer
        );
        ''')

        # Games Table
        self.cursor.execute('''
        CREATE TABLE games (
          id serial PRIMARY KEY,
          episode_num INT UNIQUE,
          season_id INT,
          air_date DATE NOT NULL,
          notes VARCHAR,
          contestant1 INT,
          contestant2 INT,
          contestant3 INT,
          winner INT,
          score1 INT,
          score2 INT,
          score3 INT,
          FOREIGN KEY (season_id) REFERENCES seasons (id),
          FOREIGN KEY (contestant1) REFERENCES contestants (id),
          FOREIGN KEY (contestant2) REFERENCES contestants (id),
          FOREIGN KEY (contestant3) REFERENCES contestants (id),
          FOREIGN KEY (winner) REFERENCES contestants (id)
        );
        ''')

        # Questions Table
        self.cursor.execute('''
        CREATE TABLE clues (
          id serial PRIMARY KEY,
          game_id INT,
          value INT NOT NULL,
          daily_double BOOLEAN NOT NULL,
          round VARCHAR NOT NULL,
          category VARCHAR NOT NULL,
          clue VARCHAR NOT NULL,
          response VARCHAR NOT NULL,
          FOREIGN KEY (game_id) REFERENCES games (id)
        );
        ''')

    def delete_database(self):
        self.cursor.execute('DROP TABLE games CASCADE')
        self.cursor.execute('DROP TABLE seasons CASCADE')
        self.cursor.execute('DROP TABLE contestants CASCADE')
        self.cursor.execute('DROP TABLE clues CASCADE')
        self.cursor.execute('DROP TABLE parsed_games')
