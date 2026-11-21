from imports import *
from constants import *
from directories import *

# -----------------------
# AVITD Scraper Class
# -----------------------

class AVITDScraper:
    """
    Scraper for 'A View in the Dark' to update guilds and shops data in SQLite.
    """

    def __init__(self) -> None:
        """Initialize scraper with URL, headers, and database connection."""
        self.url = "https://aviewinthedark.net/"
        try:
            self.connection = sqlite3.connect(DB_PATH)
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            self.connection = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        logging.debug("AVITDScraper initialized")

    def scrape_guilds_and_shops(self) -> None:
        """Scrape guilds and shops data and update the database."""
        if not self.connection:
            logging.error("No database connection; aborting scrape")
            return

        logging.info("Starting guilds and shops scrape")
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logging.error(f"Failed to fetch {self.url}: {e}")
            return

        guilds = self.scrape_section(soup, "the guilds")
        shops = self.scrape_section(soup, "the shops")
        guilds_next = self.extract_next_update_time(soup, 'Guilds')
        shops_next = self.extract_next_update_time(soup, 'Shops')

        self.display_results(guilds, shops, guilds_next, shops_next)
        self.update_database(guilds, "guilds", guilds_next)
        self.update_database(shops, "shops", shops_next)
        logging.info("Scrape and database update completed")

    def scrape_section(self, soup: BeautifulSoup, section_alt: str) -> list[tuple[str, str, str]]:
        """
        Scrape a section (guilds or shops) from the parsed HTML.

        Args:
            soup: Parsed HTML content.
            section_alt: Alt text of the section image.

        Returns:
            List of (name, column, row) tuples.
        """
        data = []
        section_img = soup.find('img', alt=section_alt)
        if not section_img:
            logging.warning(f"Section '{section_alt}' not found")
            return data

        table = section_img.find_next('table')
        if not table:
            logging.warning(f"No table found for '{section_alt}'")
            return data

        for row in table.find_all('tr', class_=['odd', 'even']):
            cols = row.find_all('td')
            if len(cols) < 2:
                logging.debug(f"Skipping malformed row in '{section_alt}': {row.text}")
                continue

            name = cols[0].text.strip()
            location = cols[1].text.strip().replace("SE of ", "")
            try:
                col, row = location.split(" and ")
                data.append((name, col, row))
                logging.debug(f"Scraped {section_alt}: {name} at {col}, {row}")
            except ValueError:
                logging.warning(f"Invalid location format for '{name}': {location}")

        logging.debug(f"Scraped {len(data)} items from '{section_alt}'")
        return data

    def extract_next_update_time(self, soup: BeautifulSoup, section_name: str) -> str:
        """
        Extract the next update time for a section.

        Args:
            soup: Parsed HTML content.
            section_name: Section name ('Guilds' or 'Shops').

        Returns:
            Next update time in 'YYYY-MM-DD HH:MM:SS' or 'NA'.
        """
        for div in soup.find_all('div', class_='next_change'):
            if section_name in div.text:
                match = re.search(r'(\d+)\s+days?,\s+(\d+)h\s+(\d+)m\s+(\d+)s', div.text)
                if match:
                    days, hours, mins, secs = map(int, match.groups())
                    next_update = datetime.now() + timedelta(days=days, hours=hours, minutes=mins, seconds=secs)
                    return next_update.strftime('%Y-%m-%d %H:%M:%S')
        logging.debug(f"No update time found for '{section_name}'")
        return 'NA'

    def display_results(self, guilds: list, shops: list, guilds_next: str, shops_next: str) -> None:
        """
        Log scraped results for debugging.

        Args:
            guilds: List of guild data.
            shops: List of shop data.
            guilds_next: Guilds next update time.
            shops_next: Shops next update time.
        """
        logging.debug(f"Guilds Next Update: {guilds_next}")
        logging.debug(f"Shops Next Update: {shops_next}")
        logging.debug(f"Guilds ({len(guilds)}): {', '.join(g[0] for g in guilds)}")
        logging.debug(f"Shops ({len(shops)}): {', '.join(s[0] for s in shops)}")

    def update_database(self, data: list[tuple[str, str, str]], table: str, next_update: str) -> None:
        """
        Update the database with scraped data.

        Args:
            data: List of (name, column, row) tuples.
            table: Target table ('guilds' or 'shops').
            next_update: Next update time.
        """
        if not self.connection:
            return

        cursor = self.connection.cursor()
        try:
            # Reset all entries to 'NA' except Peacekeeper's Missions for guilds
            reset_query = f"UPDATE {table} SET `Column`='NA', `Row`='NA', `next_update`=? WHERE Name NOT LIKE 'Peacekkeepers Mission%' AND Name NOT IN ('Peacekeeper\\'s Mission 1', 'Peacekeeper\\'s Mission 2', 'Peacekeeper\\'s Mission 3')" if table == "guilds" else f"UPDATE {table} SET `Column`='NA', `Row`='NA', `next_update`=?"
            cursor.execute(reset_query, (next_update,))

            # Update or insert scraped data
            upsert_query = f"""
                INSERT INTO {table} (Name, `Column`, `Row`, `next_update`)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(Name) DO UPDATE SET `Column`=excluded.`Column`, `Row`=excluded.`Row`, `next_update`=excluded.`next_update`
            """
            filtered_data = [(n, c, r, next_update) for n, c, r in data if "Peacekkeepers Mission" not in n or table == "guilds"]
            cursor.executemany(upsert_query, filtered_data)

            # Ensure Peacekeeper’s Missions persist in guilds
            if table == "guilds":
                peacekeepers = [
                    ("Peacekkeepers Mission 1", "Emerald", "67th", next_update),
                    ("Peacekkeepers Mission 2", "Unicorn", "33rd", next_update),
                    ("Peacekkeepers Mission 3", "Emerald", "33rd", next_update),
                ]
                cursor.executemany(upsert_query, peacekeepers)

            self.connection.commit()
            logging.debug(f"Updated {table} with {len(filtered_data)} entries")
        except sqlite3.Error as e:
            logging.error(f"Failed to update {table}: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def close_connection(self) -> None:
        """Close the database connection."""
        if self.connection:
            try:
                self.connection.close()
                logging.debug("Database connection closed")
            except sqlite3.Error as e:
                logging.error(f"Failed to close connection: {e}")
            finally:
                self.connection = None
