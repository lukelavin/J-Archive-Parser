from bs4 import BeautifulSoup
from urllib import request
import psycopg2
from DatabaseConnection import DatabaseConnection

# dbcon = DatabaseConnection()
# dbcon.delete_database()
# dbcon.setup_database()

# Seasons page
print('Grabbing Seasons List')
with request.urlopen('https://j-archive.com/listseasons.php') as response:
    html = response.read()
soup = BeautifulSoup(html, 'html.parser')

rows = soup.find_all('tr')

print('Parsing Season Info')
for row in rows:
    info = row.find_all('td')
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
        end_date = 'Unknown'

    print('\t  From: ' + start_date)
    print('\t  To: ' + end_date)


    # Games Played
    games_played = info[2].get_text()
    games_played = games_played[1: games_played.find(' ')]
    print('\tNotes: ' + games_played)


# dbcon.close()
