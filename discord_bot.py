from imports import *
from constants import *

class DiscordReportBot(discord.Client):
    def __init__(self, token: str, channel_id: int):
        intents = discord.Intents.default()
        intents.messages = True
        super().__init__(intents=intents)

        self.token = token
        self.channel_id = channel_id

    async def on_ready(self):
        logging.info(f"[DiscordBot] Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message):
        if message.author.bot or message.channel.id != self.channel_id:
            return

        new_entries = 0
        for line in message.content.splitlines():
            if match := re.match(r"^(.*?),\s*right by\s*(\w+)\s+and\s+(\d+\w*)", line, re.IGNORECASE):
                # Format: Shop
                name, col, row = match.groups()
                added = self.store(name.strip(), col, row, "shops")
                if added:
                    logging.info(f"[DiscordBot] Added shop: {name} at {col} & {row}")
                    new_entries += 1
            elif match := re.match(r"^(.*?Guild\s*\d?)\s*[-–]\s*(\w+)\s*&\s*(\d+\w*)", line, re.IGNORECASE):
                # Format: Guild
                name, col, row = match.groups()
                added = self.store(name.strip(), col, row, "guilds")
                if added:
                    logging.info(f"[DiscordBot] Added guild: {name} at {col} & {row}")
                    new_entries += 1

        if new_entries:
            logging.info(f"[DiscordBot] Total new entries from message: {new_entries}")

    def store(self, name: str, col: str, row: str, table: str) -> bool:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT 1 FROM {table} WHERE Name=? AND `Column`=? AND `Row`=?", (name, col, row))
                if cursor.fetchone():
                    return False  # Already exists

                cursor.execute(f"""
                    INSERT INTO {table} (Name, `Column`, `Row`, `next_update`, `last_scraped`)
                    VALUES (?, ?, ?, 'NA', datetime('now'))
                """, (name, col, row))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"[DiscordBot] DB error inserting {name} into {table}: {e}")
            return False

    def start_bot(self):
        self.run(self.token)