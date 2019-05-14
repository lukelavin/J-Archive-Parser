from bs4 import BeautifulSoup
from urllib import request
from DatabaseConnection import DatabaseConnection
from time import sleep
from random import randrange

dbcon = DatabaseConnection()
dbcon.delete_database()
dbcon.setup_database()

# Seasons List
print('Grabbing Seasons List')
with request.urlopen('https://j-archive.com/listseasons.php') as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')
print(html)

rows = soup.find_all('tr')
season_links = []

print('Parsing Season Info')
for row in rows:
    info = row.find_all('td')
    season_links.append(info[0].find('a').get('href'))
    # print(info[2].prettify())

    # Season Name
    season_name = info[0].get_text()
    print('Title: ' + season_name)

    # Air Dates
    air_dates = info[1].get_text()
    print('\tAired: ' + air_dates)
    air_dates = air_dates.split(' to ')
    if len(air_dates) > 1:
        start_date = air_dates[0]
        end_date = air_dates[1]
    else:
        start_date = air_dates[0][0:air_dates[0].find(' ')]
        end_date = None

    print('\t  From: ' + start_date)
    print('\t  To: ' + str(end_date))

    # Games Played
    games_played = info[2].get_text()
    games_played = games_played[1: games_played.find(' ')]
    print('\tGames: ' + games_played)

    # Adding the season to the database
    dbcon.insert_season(season_name, start_date, end_date, games_played)

sleep(randrange(1, 5))
# Episode List for each season read off the Season List
for i in range(len(season_links)):
    season_link = season_links[i]
    sleep(randrange(5, 15))
    print(season_link)
    with request.urlopen('https://j-archive.com/' + season_link) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    rows = soup.find_all('tr')

    for row in rows:
        info = row.find_all('td')

        # Link to grab game's clue data next
        game_link = info[0].find('a').get('href')
        print('Game Link: ' + game_link)

        # Episode Number
        episode_number = info[0].get_text()[info[0].get_text().find('#') + 1: info[0].get_text().find(', ')].strip()
        print('Episode Number: ' + str(episode_number))

        # Air Date
        air_date = info[0].get_text()[info[0].get_text().find(', aired') + 7:].strip()
        print('\tAir Date: ' + air_date)

        # Contestants
        print('\nGrabbing Contestants')
        contestants = info[1].get_text().split(' vs. ')
        for i in range(3):
            contestants[i] = contestants[i].replace('\xf1', 'n').strip()
            print(contestants[i])
            if not dbcon.contestant_exists(contestants[i]):
                dbcon.insert_contestant(contestants[i], None, 0, 0)

        # Game Notes
        print('\nGrabbing game notes')
        game_notes = info[2].get_text().strip()
        print('Game notes: ' + game_notes)

        sleep(randrange(3, 8))
        # Read the Game Data (it has stuff we need before adding stuff to the database
        print('\n\nParsing game page')
        with request.urlopen(game_link) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'lxml')

        if len(soup.find_all('h3')) < 5:
            print('**********************')
            print('*** Game not ready ***')
            print('**********************')
            continue

        # More Contestant Info

        # Notes
        print('\nGrabbing contestant notes')
        contestant_notes = soup.find_all('p', class_='contestants')
        contestant_names = []
        for contestant in contestant_notes:
            print(contestant)
            contestant_name = contestant.find('a').get_text().replace('\xf1', 'n').strip()
            contestant_names.append(contestant_name)
            print('Name: ' + contestant_name)
            contestant_note = contestant.get_text()[contestant.get_text().find(', ') + 2:]
            print('Note: ' + contestant_note)
            if dbcon.contestant_exists(contestant_name):
                dbcon.update_contestant(contestant_name, contestant_note,
                                        (dbcon.get_contestant_games_played(contestant_name) + 1))
            else:
                dbcon.insert_contestant(contestant_name, contestant_note, 1, 0)
            print('Updated notes')
        contestant_names.reverse()

        # Grabbing contestant IDs from the names
        contestant_ids = []
        for c in contestant_names:
            contestant_ids.append(dbcon.get_contestant_id_from_name(c))

        # Winnings
        print('\nGrabbing contestant winnings')
        final_score_headers = soup.find_all('h3')
        header = final_score_headers[3]
        contestant_winnings_table = header.find_next_sibling()
        contestant_winnings_rows = contestant_winnings_table.find_all('tr')
        contestant_scores = contestant_winnings_rows[1].find_all('td')
        contestant_score_remarks = contestant_winnings_rows[2].find_all('td')

        scores = []

        for i in range(3):
            contestant_name = contestant_names[i]
            print('\nName: ' + contestant_name)

            score_text = contestant_scores[i].get_text()
            print(score_text)
            score = contestant_scores[i].get_text().strip()[contestant_scores[i].get_text().strip().find('$') + 1:].replace(',', '')
            print(score)
            scores.append(score)
            print('Score: ' + score)

            print(contestant_score_remarks[i])
            if contestant_score_remarks[i].get_text().find('2nd place') != -1:
                contestant_winnings = 2000
                winner = i
            elif contestant_score_remarks[i].get_text().find('3rd place') != -1:
                contestant_winnings = 1000
            else:
                contestant_winnings = int(score) + dbcon.get_contestant_winnings(contestant_name)
            print('Winnings:', contestant_winnings)

            dbcon.update_contestant(contestant_name, total_winnings=contestant_winnings)
            print('Updated')

        # Adding Game
        dbcon.insert_game(episode_number, i, air_date, game_notes, contestant_ids[0], contestant_ids[1],
                          contestant_ids[2], contestant_ids[winner], scores[0], scores[1], scores[2])

        # **********
        #    Clues
        # **********

        # Jeopardy Round
        soup.find_all('table')

        # Double Jeopardy Round
        soup.find_all('table')

        # Final Jeopardy

dbcon.close()
