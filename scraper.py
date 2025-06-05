from imports import *
from constants import *

class Scraper:
    def __init__(self):
        self.avitd_url = "https://aviewinthedark.net/"
        self.terrible_url = "https://vampires.terrible.engineering/api/locations"
        self.discord_bot_url = "https://lollis-home.ddns.net/api/locations.json"
        self.connection = sqlite3.connect(DB_PATH)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        logging.info("Scraper initialized.")

    def scrape(self):
        avitd_data, guilds_next, shops_next = self.scrape_avitd()
        terrible_data = self.scrape_terrible()
        discord_data = self.scrape_discord_bot()

        # Chain merge Discord → Terrible → AVITD for both guilds and shops
        combined_guilds = self.merge_data(terrible_data["guilds"], discord_data["guilds"], source_a="Terrible", source_b="Discord")
        final_guilds = self.merge_data(avitd_data["guilds"], combined_guilds, source_a="AVITD", source_b="Terrible/Discord")

        combined_shops = self.merge_data(terrible_data["shops"], discord_data["shops"], source_a="Terrible", source_b="Discord")
        final_shops = self.merge_data(avitd_data["shops"], combined_shops, source_a="AVITD", source_b="Terrible/Discord")

        self.update_database(final_guilds, "guilds", guilds_next)
        self.update_database(final_shops, "shops", shops_next)

    def scrape_avitd(self):
        try:
            response = requests.get(self.avitd_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logging.error(f"AVITD fetch failed: {e}")
            return {'guilds': {}, 'shops': {}}, 'NA', 'NA'

        guilds = self.scrape_section(soup, "the guilds")
        shops = self.scrape_section(soup, "the shops")
        guilds_next = self.extract_next_update_time(soup, 'Guilds')
        shops_next = self.extract_next_update_time(soup, 'Shops')

        logging.info(f"AVITD provided {len(guilds)} guilds and {len(shops)} shops.")
        return {
            'guilds': {self.normalize_name(name): (col, row) for name, col, row in guilds},
            'shops': {self.normalize_name(name): (col, row) for name, col, row in shops}
        }, guilds_next, shops_next

    def scrape_section(self, soup, alt_text):
        section = soup.find('img', alt=alt_text)
        if not section:
            return []
        table = section.find_next('table')
        rows = table.find_all('tr', class_=['odd', 'even'])
        result = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
            name = cols[0].text.strip()
            try:
                col, row = cols[1].text.replace("SE of ", "").strip().split(" and ")
                result.append((name, col, row))
            except ValueError:
                continue
        return result

    def extract_next_update_time(self, soup, label):
        divs = soup.find_all('div', class_='next_change')
        for div in divs:
            if label in div.text:
                match = re.search(r'(\d+)\s+days?,\s+(\d+)h\s+(\d+)m\s+(\d+)s', div.text)
                if match:
                    delta = timedelta(days=int(match[1]), hours=int(match[2]), minutes=int(match[3]), seconds=int(match[4]))
                    return (datetime.now(timezone.utc) + delta).strftime('%Y-%m-%d %H:%M:%S')
        return 'NA'

    def scrape_terrible(self):
        try:
            response = requests.get(self.terrible_url, timeout=10)
            data = response.json()
        except Exception as e:
            logging.error(f"Terrible API fetch failed: {e}")
            return {'guilds': {}, 'shops': {}}

        guilds = {}
        shops = {}

        for loc in data:
            name = self.normalize_name(loc["building_name"])
            col = str(loc["coordinate_x"])
            row = str(loc["coordinate_y"])
            typ = loc["building_type"]
            if typ == "guild":
                guilds[name] = (col, row)
            elif typ == "shop":
                shops[name] = (col, row)

        logging.info(f"Terrible API provided {len(guilds)} guilds and {len(shops)} shops.")
        return {'guilds': guilds, 'shops': shops}

    def scrape_discord_bot(self):
        try:
            response = requests.get(self.discord_bot_url, timeout=10)
            data = response.json()
        except Exception as e:
            logging.error(f"Discord bot API fetch failed: {e}")
            return {'guilds': {}, 'shops': {}}

        guilds = {}
        shops = {}

        for name, coord in data.get("guilds", {}).items():
            norm_name = self.normalize_name(name)
            guilds[norm_name] = (coord["column"], coord["row"])
        for name, coord in data.get("shops", {}).items():
            norm_name = self.normalize_name(name)
            shops[norm_name] = (coord["column"], coord["row"])

        logging.info(f"Discord bot provided {len(guilds)} guilds and {len(shops)} shops.")
        return {'guilds': guilds, 'shops': shops}

    def normalize_name(self, name):
        """Standardizes building names by fixing known typos and stripping formatting."""
        name = name.strip()

        # Fix known typo in AVITD source
        if name.startswith("Peacekkeepers Mission"):
            name = name.replace("Peacekkeepers", "Peacekeepers", 1)

        # Remove Markdown-like decorations
        name = name.lstrip("*_~").rstrip("*_~")

        return name

    def merge_data(self, a_dict, b_dict, source_a="A", source_b="B"):
        merged = {}
        all_keys = set(a_dict.keys()) | set(b_dict.keys())
        for key in all_keys:
            if key in a_dict:
                merged[key] = a_dict[key]
                logging.debug(f"Using {source_a} data for {key}: {a_dict[key]}")
            else:
                merged[key] = b_dict[key]
                logging.debug(f"Using {source_b} data for {key}: {b_dict[key]}")
        return merged

    def update_database(self, merged_dict, table, next_update):
        scrape_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                # Reset existing entries
                if table == "guilds":
                    cursor.execute(f"""
                        UPDATE {table}
                        SET `Column`='NA', `Row`='NA', `next_update`=?, `last_scraped`=?
                        WHERE Name NOT LIKE 'Peacekeepers Mission%'
                    """, (next_update, scrape_time))
                else:
                    cursor.execute(f"""
                        UPDATE {table}
                        SET `Column`='NA', `Row`='NA', `next_update`=?, `last_scraped`=?
                    """, (next_update, scrape_time))

                # Insert or update entries in sorted order
                for name in sorted(merged_dict):
                    if table == "shops" and "Peacekeepers Mission" in name:
                        logging.warning(f"Skipping {name} as it belongs in guilds, not shops.")
                        continue

                    col, row = merged_dict[name]
                    norm_name = self.normalize_name(name)
                    cursor.execute(f"""
                        INSERT INTO {table} (Name, `Column`, `Row`, `next_update`, `last_scraped`)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(Name) DO UPDATE SET
                            `Column`=excluded.`Column`,
                            `Row`=excluded.`Row`,
                            `next_update`=excluded.`next_update`,
                            `last_scraped`=excluded.`last_scraped`
                    """, (norm_name, col, row, next_update, scrape_time))

                # Manually insert Peacekeepers if in guilds
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
                        ("Peacekeepers Mission 1", "Emerald", "67th", next_update, scrape_time),
                        ("Peacekeepers Mission 2", "Unicorn", "33rd", next_update, scrape_time),
                        ("Peacekeepers Mission 3", "Emerald", "33rd", next_update, scrape_time),
                    ])

                conn.commit()
                logging.info(f"{table.capitalize()} table updated with {len(merged_dict)} entries.")

        except sqlite3.Error as e:
            logging.error(f"Failed to update database: {e}")

    def close_connection(self):
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")