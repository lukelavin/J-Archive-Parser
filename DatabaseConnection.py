import psycopg2


class DatabaseConnection:

    def __init__(self, connect_args=None):
        try:
            if connect_args is None:
                self.connection = psycopg2.connect('dbname=jeopardy user=postgres password=*************')
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

    def insert_season(self, name, start_date, end_date, total_games):
        self.cursor.execute('''
        INSERT INTO seasons (season_name, start_date, end_date, total_games)
        VALUES (%s, %s, %s, %s);
        ''', (name, start_date, end_date, total_games))

    def insert_contestant(self, name, notes, games_played, total_winnings):
        self.cursor.execute('''
        INSERT INTO contestants (name, notes, games_played, total_winnings)
        VALUES (%s, %s, %s, %s);
        ''', (name, notes, games_played, total_winnings))

    def insert_game(self, season_id, air_date, notes, contestant1, contestant2, contestant3,
                    winner, score1, score2, score3):
        self.cursor.execute('''
        INSERT INTO 
        games (season_id, air_date, notes, contestant1, contestant2, contestant3, winner, score1, score2, score3)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        ''', (season_id, air_date, notes, contestant1, contestant2, contestant3, winner, score1, score2, score3))

    def insert_question(self, game_id, value, round, category, clue, response, correct_contestant):
        self.cursor.execute('''
        INSERT INTO questions (game_id, value, round, category, clue, response, correct_contestant)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (game_id, value, round, category, clue, response, correct_contestant))

    def print_seasons(self):
        self.cursor.execute('SELECT * FROM seasons')
        seasons = self.cursor.fetchall()
        for season in seasons:
            print(season)

    def print_contestants(self):
        self.cursor.execute('SELECT * FROM contestants')
        contestants = self.cursor.fetchall()
        for contestant in contestants:
            print(contestant)

    def print_games(self):
        self.cursor.execute('SELECT * FROM games')
        games = self.cursor.fetchall()
        for game in games:
            print(game)

    def print_questions(self):
        self.cursor.execute('SELECT * FROM questions')
        questions = self.cursor.fetchall()
        for question in questions:
            print(question)

    def setup_database(self):
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
          notes VARCHAR NOT NULL,
          games_played integer NOT NULL,
          total_winnings integer
        );
        ''')

        # Games Table
        self.cursor.execute('''
        CREATE TABLE games (
          id serial PRIMARY KEY,
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
        CREATE TABLE questions (
          id serial PRIMARY KEY,
          game_id INT,
          value INT NOT NULL,
          round VARCHAR NOT NULL,
          category VARCHAR NOT NULL,
          clue VARCHAR NOT NULL,
          response VARCHAR NOT NULL,
          correct_contestant INT,
          FOREIGN KEY (game_id) REFERENCES games (id),
          FOREIGN KEY (correct_contestant) REFERENCES contestants (id)
        );
        ''')

    def delete_database(self):
        self.cursor.execute('DROP TABLE games CASCADE')
        self.cursor.execute('DROP TABLE seasons CASCADE')
        self.cursor.execute('DROP TABLE contestants CASCADE')
        self.cursor.execute('DROP TABLE questions CASCADE')

        self.cursor.close()
        self.connection.close()
