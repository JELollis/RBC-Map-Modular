from imports import *
from constants import *
from directories import *
from database import *

# -----------------------
# AVITD Scraper Class
# -----------------------

class AVITDScraper:
    """
    A scraper class for 'A View in the Dark' to update guilds and shops data in the database.
    """

    def __init__(self):
        """
        Initialize the scraper with required headers.
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

    def scrape_guilds(self):
        """
        Scrape guilds data from 'A View in the Dark' and update the database.
        """
        url = 'https://quiz.ravenblack.net/guilds'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            guilds = []
            guild_rows = soup.find_all('tr', class_='guild')
            for row in guild_rows:
                columns = row.find_all('td')
                name = columns[0].text.strip()
                coordinates = re.search(r'\((\d+), (\d+)\)', columns[1].text.strip())
                if coordinates:
                    x = int(coordinates.group(1))
                    y = int(coordinates.group(2))
                    next_update = self.extract_next_update_time(columns[3].text.strip())

                    guilds.append((name, x, y, next_update))

            self.update_guilds(guilds)

        except requests.RequestException as e:
            logging.error(f"Failed to scrape guilds: {e}")

    def scrape_shops(self):
        """
        Scrape shops data from 'A View in the Dark' and update the database.
        """
        url = 'https://quiz.ravenblack.net/shops'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            shops = []
            shop_rows = soup.find_all('tr', class_='shop')
            for row in shop_rows:
                columns = row.find_all('td')
                name = columns[0].text.strip()
                coordinates = re.search(r'\((\d+), (\d+)\)', columns[1].text.strip())
                if coordinates:
                    x = int(coordinates.group(1))
                    y = int(coordinates.group(2))
                    next_update = self.extract_next_update_time(columns[3].text.strip())

                    shops.append((name, x, y, next_update))

            self.update_shops(shops)

        except requests.RequestException as e:
            logging.error(f"Failed to scrape shops: {e}")

    def extract_next_update_time(self, text):
        """
        Extract the next update time from the text.

        Args:
            text (str): Text containing the update time.

        Returns:
            str: Formatted next update time string.
        """
        match = re.search(r'(\d+)\s+days?\s+(\d+):(\d+)', text)
        if match:
            days = int(match.group(1))
            hours = int(match.group(2))
            minutes = int(match.group(3))
            next_update = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)
            return next_update.strftime('%Y-%m-%d %H:%M:%S')
        return 'NA'

    def update_guild(self, cursor, name, x, y, next_update):
        """
        Update a single guild in the database.

        Args:
            cursor (pymysql.cursors.Cursor): Database cursor.
            name (str): Guild name.
            x (int): X coordinate.
            y (int): Y coordinate.
            next_update (str): Next update time.
        """
        cursor.execute(
            """
            INSERT INTO guilds (`Name`, `Column`, `Row`, `Next_Update`)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE `Next_Update` = VALUES(`Next_Update`)
            """, (name, x, y, next_update)
        )

    def update_shop(self, cursor, name, x, y, next_update):
        """
        Update a single shop in the database.

        Args:
            cursor (pymysql.cursors.Cursor): Database cursor.
            name (str): Shop name.
            x (int): X coordinate.
            y (int): Y coordinate.
            next_update (str): Next update time.
        """
        cursor.execute(
            """
            INSERT INTO shops (`Name`, `Column`, `Row`, `Next_Update`)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE `Next_Update` = VALUES(`Next_Update`)
            """, (name, x, y, next_update)
        )

    def update_guilds(self, guilds):
        """
        Update the guilds data in the database.

        Args:
            guilds (list): List of guild data tuples (name, x, y, next_update).
        """
        connection = connect_to_database()
        if not connection:
            logging.error("Failed to connect to the database.")
            return

        try:
            cursor = connection.cursor()
            for guild in guilds:
                self.update_guild(cursor, guild[0], guild[1], guild[2], guild[3])
            connection.commit()
            logging.info("Guilds updated successfully.")
        except pymysql.MySQLError as e:
            logging.error(f"Failed to update guilds: {e}")
        finally:
            connection.close()

    def update_shops(self, shops):
        """
        Update the shops data in the database.

        Args:
            shops (list): List of shop data tuples (name, x, y, next_update).
        """
        connection = connect_to_database()
        if not connection:
            logging.error("Failed to connect to the database.")
            return

        try:
            cursor = connection.cursor()
            for shop in shops:
                self.update_shop(cursor, shop[0], shop[1], shop[2], shop[3])
            connection.commit()
            logging.info("Shops updated successfully.")
        except pymysql.MySQLError as e:
            logging.error(f"Failed to update shops: {e}")
        finally:
            connection.close()

    def get_next_update_times(self):
        """
        Retrieve the next update times for guilds and shops from the database.

        Returns:
            dict: Dictionary containing the next update times.
        """
        connection = connect_to_database()
        if not connection:
            logging.error("Failed to connect to the database.")
            return {}

        try:
            cursor = connection.cursor()

            cursor.execute("SELECT MIN(Next_Update) FROM guilds WHERE Next_Update != 'NA'")
            next_guild_update = cursor.fetchone()[0]

            cursor.execute("SELECT MIN(Next_Update) FROM shops WHERE Next_Update != 'NA'")
            next_shop_update = cursor.fetchone()[0]

            return {
                'guilds': next_guild_update,
                'shops': next_shop_update
            }
        except pymysql.MySQLError as e:
            logging.error(f"Failed to retrieve next update times: {e}")
            return {}
        finally:
            connection.close()

    def scrape_avitd_data(self):
        """
        Scrape data from 'A View in the Dark' and update the database.
        """
        self.scrape_guilds()
        self.scrape_shops()
