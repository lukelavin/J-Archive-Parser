import unittest
from DatabaseConnection import DatabaseConnection


class DBConnectionTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbcon = DatabaseConnection('dbname=test user=postgres password=*********')
        cls.dbcon.setup_database()
        print(cls.dbcon)

    @classmethod
    def tearDownClass(cls):
        cls.dbcon.delete_database()
        cls.dbcon.close()

    def test_insert_season(self):
        pass

    def test_insert_contestant(self):
        pass

    def test_insert_game(self):
        pass

    def test_insert_question(self):
        pass

    def test_print_seasons(self):
        pass

    def test_print_contestants(self):
        pass

    def test_print_games(self):
        pass

    def test_print_questions(self):
        pass


if __name__ == '__main__':
    unittest.main()