import unittest
import psycopg2
from contextlib import redirect_stdout
from io import StringIO
from DatabaseConnection import DatabaseConnection


class DBConnectionTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('password.txt') as f:
            password = f.readline()

        cls.dbcon = DatabaseConnection('dbname=test user=postgres password=' + password)
        try:
            cls.dbcon.delete_database()
        except psycopg2.errors.UndefinedTable as e:
            pass
        cls.dbcon.setup_database()

        cls.dbcon.cursor.execute('''
            INSERT INTO seasons (season_name, start_date, end_date, total_games)
            VALUES (%s, %s, %s, %s);
            ''', ('Test Season', '2013-05-30', '2014-04-23', 43))

        cls.dbcon.cursor.execute('''
            INSERT INTO contestants (name, notes, games_played, total_winnings)
            VALUES (%s, %s, %s, %s);
            ''', ('John Smith', 'A teacher from Akron, Ohio', 2, 19400))

        cls.dbcon.cursor.execute('''
            INSERT INTO contestants (name, notes, games_played, total_winnings)
            VALUES (%s, %s, %s, %s);
            ''', ('Jane Doe', 'A software engineer from Atlanta, Georgia', 1, 2000))

        cls.dbcon.cursor.execute('''
            INSERT INTO contestants (name, notes, games_played, total_winnings)
            VALUES (%s, %s, %s, %s);
            ''', ('Joe Schmo', 'An accountant from San Diego, California', 1, 1000))

        cls.dbcon.cursor.execute('''
            INSERT INTO games (season_id, air_date, notes, contestant1, contestant2, contestant3, winner, score1, score2, score3)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            ''', (1, '2013-08-24', 'Tournament of Champions Game 1', 1, 2, 3, 1, 3400, 1400, 1200))

        cls.dbcon.cursor.execute('''
            INSERT INTO questions (game_id, value, daily_double, round, category, clue, response, correct_contestant)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            ''', (1, 400, 'No', 'Jeopardy', 'State Capitals', 'The capital of Indiana', 'Indianapolis', 1))

        print('Connected:', cls.dbcon, "\n")

    @classmethod
    def tearDownClass(cls):
        cls.dbcon.delete_database()
        cls.dbcon.close()

    def test_insert_season(self):
        self.dbcon.insert_season('Season Luke', '2000-04-21', '2019-05-10', 150)

        captured_output = StringIO()
        with redirect_stdout(captured_output):
            self.dbcon.print_seasons()

        self.assertEqual(captured_output.getvalue(),
                         "(1, 'Test Season', datetime.date(2013, 5, 30), datetime.date(2014, 4, 23), 43)\n" +
                         "(2, 'Season Luke', datetime.date(2000, 4, 21), datetime.date(2019, 5, 10), 150)\n")

        self.dbcon.cursor.execute('''
        DELETE FROM seasons
        WHERE id = 2;
        ''')

    def test_insert_contestant(self):
        self.dbcon.insert_contestant('Test Man', 'A fake person made to mock data', 1, 1000)

        captured_output = StringIO()
        with redirect_stdout(captured_output):
            self.dbcon.print_contestants()

        self.assertEqual(captured_output.getvalue(),
                         "(1, 'John Smith', 'A teacher from Akron, Ohio', 2, 19400)\n" +
                         "(2, 'Jane Doe', 'A software engineer from Atlanta, Georgia', 1, 2000)\n" +
                         "(3, 'Joe Schmo', 'An accountant from San Diego, California', 1, 1000)\n" +
                         "(4, 'Test Man', 'A fake person made to mock data', 1, 1000)\n")

        self.dbcon.cursor.execute('''
                DELETE FROM contestants
                WHERE id = 4;
                ''')

    def test_insert_game(self):
        self.dbcon.insert_game(1, '2014-01-01', 'New Year Special', 1, 2, 3, 3, 9400, 400, 14200)

        captured_output = StringIO()
        with redirect_stdout(captured_output):
            self.dbcon.print_games()

        self.assertEqual(captured_output.getvalue(),
                         "(1, 1, datetime.date(2013, 8, 24), 'Tournament of Champions Game 1', " +
                         "1, 2, 3, 1, 3400, 1400, 1200)\n" +
                         "(2, 1, datetime.date(2014, 1, 1), 'New Year Special', " +
                         "1, 2, 3, 3, 9400, 400, 14200)\n"
                         )

        self.dbcon.cursor.execute('''
                        DELETE FROM games
                        WHERE id = 2;
                        ''')

    def test_insert_question(self):
        self.dbcon.insert_question(1, 2000, 'No', 'Double Jeopardy', 'Poetry', 'The man we always ask questions about',
                                   'Henry David Thoreau', 3)

        captured_output = StringIO()
        with redirect_stdout(captured_output):
            self.dbcon.print_questions()

        self.assertEqual(captured_output.getvalue(),
                         "(1, 1, 400, False, 'Jeopardy', 'State Capitals', 'The capital of Indiana', 'Indianapolis', 1)\n" +
                         "(2, 1, 2000, False, 'Double Jeopardy', 'Poetry', 'The man we always ask questions about', " +
                         "'Henry David Thoreau', 3)\n")

        self.dbcon.cursor.execute('''
                                DELETE FROM questions
                                WHERE id = 2;
                                ''')

    def test_print_seasons(self):
        captured_output = StringIO()
        with redirect_stdout(captured_output):
            self.dbcon.print_seasons()

        self.assertEqual(captured_output.getvalue(),
                         "(1, 'Test Season', datetime.date(2013, 5, 30), datetime.date(2014, 4, 23), 43)\n")

    def test_print_contestants(self):
        captured_output = StringIO()
        with redirect_stdout(captured_output):
            self.dbcon.print_contestants()

        self.assertEqual(captured_output.getvalue(),
                         "(1, 'John Smith', 'A teacher from Akron, Ohio', 2, 19400)\n" +
                         "(2, 'Jane Doe', 'A software engineer from Atlanta, Georgia', 1, 2000)\n" +
                         "(3, 'Joe Schmo', 'An accountant from San Diego, California', 1, 1000)\n")

    def test_print_games(self):
        captured_output = StringIO()
        with redirect_stdout(captured_output):
            self.dbcon.print_games()

        self.assertEqual(captured_output.getvalue(),
                         "(1, 1, datetime.date(2013, 8, 24), 'Tournament of Champions Game 1', " +
                         "1, 2, 3, 1, 3400, 1400, 1200)\n")

    def test_print_questions(self):
        captured_output = StringIO()
        with redirect_stdout(captured_output):
            self.dbcon.print_questions()

        self.assertEqual(captured_output.getvalue(),
                         "(1, 1, 400, False, 'Jeopardy', 'State Capitals', 'The capital of Indiana', 'Indianapolis', 1)\n")


if __name__ == '__main__':
    unittest.main()
