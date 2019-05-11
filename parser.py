from bs4 import BeautifulSoup
from urllib import request
import psycopg2
from DatabaseConnection import DatabaseConnection

dbcon = DatabaseConnection()
print(dbcon.connection)

# dbcon.insert_season('Season Luke', '2000-04-21', '2019-05-10', 150)
dbcon.print_seasons()

dbcon.close()

'''
with request.urlopen('http://j-archive.com') as response:
    html = response.read()

soup = BeautifulSoup(html, 'html.parser')
print(soup.prettify())
'''