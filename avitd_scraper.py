from imports import *
from constants import *

class AVITDScraper:
    """
    A scraper class for 'A View in the Dark' to update guilds and shops data in the SQLite database.
    """

    def __init__(self):
        self.url = "https://aviewinthedark.net/"
        self.connection = sqlite3.connect(DB_PATH)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("AVITDScraper initialized.")

    def scrape_guilds_and_shops(self):
        logging.info("Starting to scrape guilds and shops.")
        response = requests.get(self.url, headers=self.headers)
        logging.debug(f"Received response: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        guilds = self.scrape_section(soup, "the guilds")
        shops = self.scrape_section(soup, "the shops")
        guilds_next_update = self.extract_next_update_time(soup, 'Guilds')
        shops_next_update = self.extract_next_update_time(soup, 'Shops')

        self.display_results(guilds, shops, guilds_next_update, shops_next_update)

        self.update_database(guilds, "guilds", guilds_next_update)
        self.update_database(shops, "shops", shops_next_update)
        logging.info("Finished scraping and updating the database.")

    def scrape_section(self, soup, section_image_alt):
        logging.debug(f"Scraping section: {section_image_alt}")
        data = []
        section_image = soup.find('img', alt=section_image_alt)
        if not section_image:
            logging.warning(f"No data found for {section_image_alt}.")
            return data

        table = section_image.find_next('table')
        rows = table.find_all('tr', class_=['odd', 'even'])

        for row in rows:
            columns = row.find_all('td')
            if len(columns) < 2:
                logging.debug(f"Skipping row due to insufficient columns: {row}")
                continue

            name = columns[0].text.strip()
            location = columns[1].text.strip().replace("SE of ", "").strip()

            try:
                column, row = location.split(" and ")
                data.append((name, column, row))
                logging.debug(f"Extracted data - Name: {name}, Column: {column}, Row: {row}")
            except ValueError:
                logging.warning(f"Location format unexpected for {name}: {location}")

        logging.info(f"Scraped {len(data)} entries from {section_image_alt}.")
        return data

    def extract_next_update_time(self, soup, section_name):
        logging.debug(f"Extracting next update time for section: {section_name}")
        section_divs = soup.find_all('div', class_='next_change')

        for div in section_divs:
            if section_name in div.text:
                match = re.search(r'(\d+)\s+days?,\s+(\d+)h\s+(\d+)m\s+(\d+)s', div.text)
                if match:
                    days = int(match.group(1))
                    hours = int(match.group(2))
                    minutes = int(match.group(3))
                    seconds = int(match.group(4))

                    next_update = datetime.now(timezone.utc) + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
                    logging.debug(f"Next update time for {section_name}: {next_update}")
                    return next_update.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        logging.warning(f"No next update time found for {section_name}.")
        return 'NA'

    def display_results(self, guilds, shops, guilds_next_update, shops_next_update):
        logging.info(f"Guilds Next Update: {guilds_next_update}")
        logging.info(f"Shops Next Update: {shops_next_update}")

        logging.info("Guilds Data:")
        for guild in guilds:
            logging.info(f"Name: {guild[0]}, Column: {guild[1]}, Row: {guild[2]}")

        logging.info("Shops Data:")
        for shop in shops:
            logging.info(f"Name: {shop[0]}, Column: {shop[1]}, Row: {shop[2]}")

    def update_database(self, data, table, next_update):
        scrape_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                if table == "guilds":
                    cursor.execute(f"""
                        UPDATE {table}
                        SET `Column`='NA', `Row`='NA', `next_update`=?, `last_scraped`=?
                        WHERE Name NOT LIKE 'Peacekeepers Mission%'
                    """, (next_update, scrape_timestamp))
                else:
                    cursor.execute(f"""
                        UPDATE {table}
                        SET `Column`='NA', `Row`='NA', `next_update`=?, `last_scraped`=?
                    """, (next_update, scrape_timestamp))

                for name, column, row in data:
                    if table == "shops" and "Peacekeepers Mission" in name:
                        logging.warning(f"Skipping {name} as it belongs in guilds, not shops.")
                        continue

                    try:
                        cursor.execute(f"""
                            INSERT INTO {table} (Name, `Column`, `Row`, `next_update`, `last_scraped`)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(Name) DO UPDATE SET
                                `Column`=excluded.`Column`,
                                `Row`=excluded.`Row`,
                                `next_update`=excluded.`next_update`,
                                `last_scraped`=excluded.`last_scraped`
                        """, (name, column, row, next_update, scrape_timestamp))
                    except sqlite3.Error as e:
                        logging.error(f"Failed to update {table} entry '{name}': {e}")

                if table == "guilds":
                    cursor.executemany(f"""
                        INSERT INTO {table} (Name, `Column`, `Row`, `next_update`, `last_scraped`)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(Name) DO UPDATE SET
                            `Column`=excluded.`Column`,
                            `Row`=excluded.`Row`,
                            `next_update`=excluded.`next_update`,
                            `last_scraped`=excluded.`last_scraped`
                    """, [
                        ("Peacekeepers Mission 1", "Emerald", "67th", next_update, scrape_timestamp),
                        ("Peacekeepers Mission 2", "Unicorn", "33rd", next_update, scrape_timestamp),
                        ("Peacekeepers Mission 3", "Emerald", "33rd", next_update, scrape_timestamp),
                    ])

                conn.commit()
                logging.info(f"Database updated for {table}.")

        except sqlite3.Error as e:
            logging.error(f"Database operation for {table} failed: {e}")

    def close_connection(self):
        """Close the SQLite connection if it's open."""
        if self.connection:
            self.connection.close()
            logging.debug("AVITDScraper database connection closed.")