from imports import *
from constants import *
from directories import *


def create_tables(conn: sqlite3.Connection) -> None:
    """Create database tables if they don’t exist."""
    cursor = conn.cursor()
    tables = [
        """CREATE TABLE IF NOT EXISTS banks (
            ID INTEGER PRIMARY KEY,
            `Column` TEXT NOT NULL,
            Row TEXT NOT NULL,
            Name TEXT DEFAULT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT,
            active_cookie INTEGER DEFAULT NULL
        )
        """,
        """CREATE TABLE IF NOT EXISTS coins (
            character_id INTEGER,
            pocket INTEGER DEFAULT 0,
            bank INTEGER DEFAULT 0,
            FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS color_mappings (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            color TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS `columns` (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Coordinate INTEGER NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS cookies (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value TEXT,
            domain TEXT,
            path TEXT,
            expiration TEXT,
            secure INTEGER,
            httponly INTEGER
        )""",
        """CREATE TABLE IF NOT EXISTS css_profiles (
                    profile_name TEXT PRIMARY KEY
                )""",
        """CREATE TABLE IF NOT EXISTS custom_css (
            profile_name TEXT NOT NULL,
            element TEXT NOT NULL,
            value TEXT NOT NULL,
            PRIMARY KEY (profile_name, element),
            FOREIGN KEY (profile_name) REFERENCES css_profiles(profile_name) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER,
            col INTEGER,
            row INTEGER,
            timestamp TEXT,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS guilds (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE,
            `Column` TEXT NOT NULL,
            Row TEXT NOT NULL,
            next_update TIMESTAMP DEFAULT NULL,
            last_scraped TIMESTAMP DEFAULT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS last_active_character (
            character_id INTEGER,
            FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS placesofinterest (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            `Column` TEXT NOT NULL,
            Row TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS powers (
            power_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            guild TEXT NOT NULL,
            cost INTEGER DEFAULT NULL,
            quest_info TEXT,
            skill_info TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS recent_destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER,
            col INTEGER,
            row INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
        )""",
        """CREATE TABLE IF NOT EXISTS `rows` (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Coordinate INTEGER NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS settings (
            setting_name TEXT PRIMARY KEY,
            setting_value BLOB
        )""",
        """CREATE TABLE IF NOT EXISTS shop_items (
            id INTEGER PRIMARY KEY,
            shop_name TEXT DEFAULT NULL,
            item_name TEXT DEFAULT NULL,
            base_price INTEGER DEFAULT NULL,
            charisma_level_1 INTEGER DEFAULT NULL,
            charisma_level_2 INTEGER DEFAULT NULL,
            charisma_level_3 INTEGER DEFAULT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS shops (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE,
            `Column` TEXT NOT NULL,
            Row TEXT NOT NULL,
            next_update TIMESTAMP DEFAULT NULL,
            last_scraped TIMESTAMP DEFAULT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS taverns (
            ID INTEGER PRIMARY KEY,
            `Column` TEXT NOT NULL,
            Row TEXT NOT NULL,
            Name TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS transits (
            ID INTEGER PRIMARY KEY,
            `Column` TEXT NOT NULL,
            Row TEXT NOT NULL,
            Name TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS userbuildings (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            `Column` TEXT NOT NULL,
            Row TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS discord_servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            invite_link TEXT NOT NULL
        );"""
    ]
    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            logging.debug(f"Created table: {table_sql.split('(')[0].strip()}")
        except sqlite3.Error as e:
            logging.error(f"Failed to create table: {e}")
            raise
    conn.commit()

def insert_initial_data(conn: sqlite3.Connection) -> None:
    """Insert initial data into the database."""
    cursor = conn.cursor()
    initial_data = [
        ("INSERT OR IGNORE INTO settings (setting_name, setting_value) VALUES (?, ?)", [
            ('keybind_config', 1),
            ('css_profile', 'Default'),
            ('log_level', str(DEFAULT_LOG_LEVEL))
        ]),
        # INSERT OR IGNORE (not REPLACE): user theme edits are upserted into this
        # table by save_theme_settings, and this seed runs on every startup, so
        # REPLACE would reset the user's colors to defaults each launch. Seed only
        # the rows a fresh DB is missing.
        ("INSERT OR IGNORE INTO color_mappings (id, type, color) VALUES (?, ?, ?)", [
            (1, 'bank', '#0000ff'),
            (2, 'tavern', '#887700'),
            (3, 'transit', '#880000'),
            (4, 'user_building', '#660022'),
            (5, 'alley', '#000000'),
            (6, 'default', '#888888'),
            (7, 'border', 'white'),
            (8, 'edge', '#0000ff'),
            (9, 'shop', '#004488'),
            (10, 'guild', '#ff0000'),
            (11, 'placesofinterest', '#660022'),
            (12, 'background', '#3b3b3b'),
            (13, 'text_color', '#dddddd'),
            (14, 'button_color', '#55557f'),
            (15, 'cityblock', '#0000dd'),
            (16, 'intersect', '#008800'),
            (17, 'street', '#444444'),
            (18, 'button_hover_color', '#666699'),
            (19, 'button_pressed_color', '#444466'),
            (20, 'button_border_color', '#222244'),
            (21, 'graveyard', '#888888')
        ]),
        ("REPLACE INTO `columns` (ID, Name, Coordinate) VALUES (?, ?, ?)", [
            ('1', 'WCL', '0'),
            ('2', 'Western City Limits', '0'),
            ('3', 'Aardvark', '2'),
            ('4', 'Alder', '4'),
            ('5', 'Buzzard', '6'),
            ('6', 'Beech', '8'),
            ('7', 'Cormorant', '10'),
            ('8', 'Cedar', '12'),
            ('9', 'Duck', '14'),
            ('10', 'Dogwood', '16'),
            ('11', 'Eagle', '18'),
            ('12', 'Elm', '20'),
            ('13', 'Ferret', '22'),
            ('14', 'Fir', '24'),
            ('15', 'Gibbon', '26'),
            ('16', 'Gum', '28'),
            ('17', 'Haddock', '30'),
            ('18', 'Holly', '32'),
            ('19', 'Iguana', '34'),
            ('20', 'Ivy', '36'),
            ('21', 'Jackal', '38'),
            ('22', 'Juniper', '40'),
            ('23', 'Kraken', '42'),
            ('24', 'Knotweed', '44'),
            ('25', 'Lion', '46'),
            ('26', 'Larch', '48'),
            ('27', 'Mongoose', '50'),
            ('28', 'Maple', '52'),
            ('29', 'Nightingale', '54'),
            ('30', 'Nettle', '56'),
            ('31', 'Octopus', '58'),
            ('32', 'Olive', '60'),
            ('33', 'Pilchard', '62'),
            ('34', 'Pine', '64'),
            ('35', 'Quail', '66'),
            ('36', 'Quince', '68'),
            ('37', 'Raven', '70'),
            ('38', 'Ragweed', '72'),
            ('39', 'Squid', '74'),
            ('40', 'Sycamore', '76'),
            ('41', 'Tapir', '78'),
            ('42', 'Teasel', '80'),
            ('43', 'Unicorn', '82'),
            ('44', 'Umbrella', '84'),
            ('45', 'Vulture', '86'),
            ('46', 'Vervain', '88'),
            ('47', 'Walrus', '90'),
            ('48', 'Willow', '92'),
            ('49', 'Yak', '94'),
            ('50', 'Yew', '96'),
            ('51', 'Zebra', '98'),
            ('52', 'Zelkova', '100'),
            ('53', 'Amethyst', '102'),
            ('54', 'Anguish', '104'),
            ('55', 'Beryl', '106'),
            ('56', 'Bleak', '108'),
            ('57', 'Cobalt', '110'),
            ('58', 'Chagrin', '112'),
            ('59', 'Diamond', '114'),
            ('60', 'Despair', '116'),
            ('61', 'Emerald', '118'),
            ('62', 'Ennui', '120'),
            ('63', 'Flint', '122'),
            ('64', 'Fear', '124'),
            ('65', 'Gypsum', '126'),
            ('66', 'Gloom', '128'),
            ('67', 'Hessite', '130'),
            ('68', 'Horror', '132'),
            ('69', 'Ivory', '134'),
            ('70', 'Ire', '136'),
            ('71', 'Jet', '138'),
            ('72', 'Jaded', '140'),
            ('73', 'Kyanite', '142'),
            ('74', 'Killjoy', '144'),
            ('75', 'Lead', '146'),
            ('76', 'Lonely', '148'),
            ('77', 'Malachite', '150'),
            ('78', 'Malaise', '152'),
            ('79', 'Nickel', '154'),
            ('80', 'Nervous', '156'),
            ('81', 'Obsidian', '158'),
            ('82', 'Oppression', '160'),
            ('83', 'Pyrites', '162'),
            ('84', 'Pessimism', '164'),
            ('85', 'Quartz', '166'),
            ('86', 'Qualms', '168'),
            ('87', 'Ruby', '170'),
            ('88', 'Regret', '172'),
            ('89', 'Steel', '174'),
            ('90', 'Sorrow', '176'),
            ('91', 'Turquoise', '178'),
            ('92', 'Torment', '180'),
            ('93', 'Uranium', '182'),
            ('94', 'Unctuous', '184'),
            ('95', 'Vauxite', '186'),
            ('96', 'Vexation', '188'),
            ('97', 'Wulfenite', '190'),
            ('98', 'Woe', '192'),
            ('99', 'Yuksporite', '194'),
            ('100', 'Yearning', '196'),
            ('101', 'Zinc', '198'),
            ('102', 'Zestless', '200')
        ]),
        ("REPLACE INTO css_profiles (profile_name) VALUES (?)", [("Default",)]),
        ("REPLACE INTO custom_css (profile_name, element, value) VALUES (?, ?, ?)", [
            ("Default", "BODY", "background-color:#000000;"),
            ("Default", "H1,DIV,BODY,P,A", "font-family:Verdana,Arial,sans-serif;"),
            ("Default", "BODY,H1", "text-align:center;"),
            ("Default", "P,A,TD,DIV,BODY", "color:#dddddd;"),
            ("Default", "P,TD,DIV", "text-align:left;"),
            ("Default", "TD", "vertical-align:top;"),
            ("Default", "TD,DIV,BODY,P", "font-size:small;"),
            ("Default", "FORM", "padding:0px; margin:0px; text-align:center;"),
            ("Default", "H1", "font-size:x-large; color:#ff0000; padding:0 0 0 0;"),
            ("Default", "A", "text-decoration:underline;"),
            ("Default", "UL", "text-align:left; font-size:smaller; padding-left:38px; margin-top:3px;"),
            ("Default", "P", "padding:5px 10px 0px 10px; margin:0px; font-weight:bold;"),
            ("Default", "P.ans", "font-style:italic; font-weight:normal; padding:5px 10px 0px 15px; margin:0px;"),
            ("Default", "DIV.spacey", "text-align:center; width:450px; padding-top:10px;"),
            ("Default", ".head", "text-align:center; font-weight:bold;"),
            ("Default", "TD.cityblock", "text-align:center; background-color:#0000dd;"),
            ("Default", "TD.intersect","text-align:center; background-color:#444444; width:150px; height:100px; position:relative;"),
            ("Default", "TD.street","text-align:center; background-color:#444444; width:150px; height:100px; position:relative;"),
            ("Default", "TD.city","text-align:center; border:solid white 1px; width:150px; height:100px; position:relative;"),
            ("Default", "SPAN.intersect", "background-color:#008800; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.transit", "background-color:#880000; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.arena","background-color:#ff0000; border:solid white 1px; padding:2px; font-weight:bold; color:white;"),
            ("Default", "SPAN.pub", "background-color:#887700; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.bank", "background-color:#0000ff; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.shop", "background-color:#004488; border:solid white 1px; padding:2px;"),
            ("Default", "SPAN.grave", "background-color:#888888; border:solid white 1px; color:#222222; padding:2px;"),
            ("Default", "SPAN.pk", "background-color:#000066; border:solid white 1px; color:#ffff00; padding:2px;"),
            ("Default", "SPAN.lair,SPAN.alchemy","background-color:#660022; border:solid white 1px; color:#cccccc; padding:2px;"),
            ("Default", "SPAN.sever,SPAN.bind", "border:solid red 1px; color:red; padding:2px;"),
            ("Default", "SPAN.vhuman", "color:green; background-color:black;"),
            ("Default", "SPAN.phuman", "color:cyan; background-color:black; font-weight:bold;"),
            ("Default", "SPAN.whuman", "color:brown; background-color:black; font-weight:bold;"),
            ("Default", "SPAN.object", "color:yellow;"),
            ("Default", "UL.possessions", "margin-top:0px; margin-bottom:3px; font-size:small;"),
            ("Default", "#mo","display:none; position:absolute; left:0; top:0; width:300; padding:2px; font:x-small Verdana,Sans-serif; color:black; background-color:yellow; border: solid black 1px;"),
            ("Default", "TABLE.textad", "background-color:#002211; border:solid #668877 1px;"),
            ("Default", "TABLE.hiscore", "border:solid #668877 1px;"),
            ("Default", "TABLE.hiscore tr:first-child", "background-color: #004400;"),
            ("Default", "TABLE.hiscore tr:not(:first-child) td", "border-right: solid #668877 1px;"),
            ("Default", "TD.headline", "font-size:8pt; text-align:center; padding:0px 8px 0px 8px;"),
            ("Default", "TD.text", "font-size:7pt; text-align:center; padding:0px 8px 0px 8px;"),
            ("Default", "TD.link", "font-size:6pt; text-align:right; color:#999999; padding:0px 2px 0px 1px;"),
            ("Default", "TABLE.at", "padding:5px; width:100%;"),
            ("Default", "TABLE.at TD","background-color:#333333; border:solid white 1px; padding:3px; padding-left:5px;"),
            ("Default", "TABLE.at TD.ahead", "font-weight:bold; padding-left:2px;"),
            ("Default", "DIV.asubhead", "font-weight:normal; font-size:80%;"),
            ("Default", "DIV.sb", "overflow:auto; height:80px; border:solid #bbbbbb 1px; background-color:#555533;"),
            ("Default", "TABLE.battle", "padding:0px; margin:0px;"),
            ("Default", "TABLE.battle TD", "border:none; padding:0px; margin:0px; text-align:center;"),
            ("Default", "TABLE.battle TD.n,TD.f,TD.e", "width:10px;"),
            ("Default", "TABLE.battle TD.f", "background:white;"),
            ("Default", "FORM.bq", "display:inline;"),
            ("Default", ".pansy", "color:#ff8888;"),
            ("Default", ".cloak", "color:#00ffff;"),
            ("Default", ".rich", "color:#ffff44;"),
            ("Default", ".mh","border:none; background-color:transparent; text-decoration:underline; color:white; padding:0px; cursor:hand;")
        ]),
        ("REPLACE INTO powers (power_id, name, guild, cost, quest_info, skill_info) VALUES (?, ?, ?, ?, ?, ?)", [
            (1,'Battle Cloak','Any Peacekeeper''s Mission',2000,'None','Buying a cloak from one of the peace missions will prevent you from attacking or being attacked by non-cloaked vampires. The cloak enforces a resting rule which limits you to bite only humans after being zeroed until you reach 250 BP. Vampires cannot bite or attack you during this time. You may still bite and rob non-cloaked vampires, as they can do the same to you. Cloaked vampires appear blue, and if zeroed, they turn pink.'),
            (2,'Celerity 1','Travellers Guild 1',4000,'Bring items to 3 pubs, no transits but you can teleport.','AP regeneration time reduced by 5 minutes per AP (25 minutes/AP).'),
            (3,'Celerity 2','Travellers Guild 2',8000,'Bring items to 6 pubs, no transits but you can teleport.','AP regeneration time reduced by 5 minutes per AP (20 minutes/AP).'),
            (4,'Celerity 3','Travellers Guild 3',17500,'Bring items to 12 pubs, no transits but you can teleport.','AP regeneration time reduced by 5 minutes per AP (15 minutes/AP).'),
            (5,'Charisma 1','Allurists Guild 1',1000,'Convince 3 vampires to visit a specific pub and say "VampName sent me".','Shop prices reduced by 3%.'),
            (6,'Charisma 2','Allurists Guild 2',3000,'Convince 6 vampires to visit a specific pub and say "VampName sent me".','Shop prices reduced by 7%.'),
            (7,'Charisma 3','Allurists Guild 3',5000,'Convince 9 vampires to visit a specific pub and say "VampName sent me".','Shop prices reduced by 10%, with an additional coin discount on each item.'),
            (8,'Locate 1','Empaths Guild 1',1500,'Visit specific locations, say "Check-Point", and drain 10 BP per location.','You can now determine the distance to a specific vampire.'),
            (9,'Locate 2','Empaths Guild 2',4000,'Visit specific locations, say "Check-Point", and drain 15 BP per location.','Locate 2 adds directional tracking and some advantages for locating close vampires in the shadows.'),
            (10,'Locate 3','Empaths Guild 3',15000,'Visit specific locations, say "Check-Point", and drain 25 BP per location.','Locate 3 reveals the exact street intersection of the vampire.'),
            (11,'Neutrality 1','Peacekeeper''s Mission 1',10000,'None','Neutrality designates a vampire as "non-violent", restricting weapon use but granting Peacekeeper protection. Can be removed at the same place and cost.'),
            (12,'Neutrality 2','Peacekeeper''s Mission 2',10000,'Additional 500 BP cost at this level.','Continues non-violent status with Peacekeeper protection.'),
            (13,'Neutrality 3','Peacekeeper''s Mission 3',10000,'Additional 1000 BP cost at this level.','Non-violent status continues, and Vial of Holy Water causes only 1 BP of damage.'),
            (14,'Perception 1','Allurists Guild',7500,'Hunt and kill 1 Vampire Hunter within 10 days.','Allows detection of hunters and potentially coin sounds in vampire pockets.'),
            (15,'Perception 2','Allurists Guild',15000,'Hunt and kill 3 Vampire Hunters within 10 days.','Detects Paladins and nearby hunters with concentration.'),
            (16,'Second Sight','Donation Required','$5','Visit donation page for $5 or find a sponsor.','Grants a bonus power of choice from a list, including Celerity-1, Stamina-1, Thievery-1, Shadows-1, Telepathy-1, Charisma-1, or Locate-1.'),
            (17,'Shadows 1','Thieves Guild 1',1000,'None','Allows you to fall into shadows after 3 days of inactivity.'),
            (18,'Shadows 2','Thieves Guild 2',2000,'None','Allows you to fall into shadows after 2 days of inactivity.'),
            (19,'Shadows 3','Thieves Guild 3',4000,'None','Allows you to fall into shadows after 1 day of inactivity.'),
            (20,'Stamina 1','Immolators Guild 1',1000,'Walk to a specified location, say code word, lose 500 BP.','Increases max AP by 10 and adds resistance to scrolls of turning (25% chance).'),
            (21,'Stamina 2','Immolators Guild 2',2500,'Walk to a specified location, say code word, lose 1000 BP.','Increases max AP by 10 and adds resistance to scrolls of turning (50% chance).'),
            (22,'Stamina 3','Immolators Guild 3',5000,'Walk to a specified location, say code word, lose 1500 BP.','Increases max AP by 10 and adds resistance to scrolls of turning (75% chance).'),
            (23,'Suction 1','Immolators Guild (ALL)',7500,'Bite 20 vampires with higher BP, spit blood into wineskin.','Gain ability to drink 2 pints from vampires and up to 4 from humans.'),
            (24,'Suction 2','Immolators Guild (ALL)',15000,'Bite 20 vampires with higher BP, spit blood into wineskin.','Gain ability to drink 4 pints from vampires and up to 10 from humans.'),
            (25,'Surprise','Empaths Guild (ALL)',20000,'None','Allows access to overcrowded squares (blue squares), but entry may still be limited if it''s too full.'),
            (26,'Telepathy 1','Travellers Guild 1',2500,'None','Allows sending messages to vampires from a distance with an AP cost of 10 for unrelated vampires and 5 for sire or childer.'),
            (27,'Telepathy 2','Travellers Guild 2',5000,'None','Allows sending messages to vampires from a distance with an AP cost of 6 for unrelated vampires and 3 for sire or childer.'),
            (28,'Telepathy 3','Travellers Guild 3',10000,'None','Allows sending messages to vampires from a distance with an AP cost of 2 for unrelated vampires and 1 for sire or childer.'),
            (29,'Thievery 1','Thievery Guild 1',2000,'None','Adds a (rob) option to vampires, allowing you to rob up to 25% of their coins.'),
            (30,'Thievery 2','Thievery Guild 2',5000,'None','Improves the (rob) option, allowing you to rob up to 50% of a vampire''s coins.'),
            (31,'Thievery 3','Thievery Guild 3',10000,'None','Improves the (rob) option further, allowing you to rob up to 75% of a vampire''s coins.'),
            (32,'Thrift 1','Allurists Guild 1',1000,'Buy 1 Perfect Red Rose from a specified shop.','5% chance to keep a used item/scroll instead of it burning up.'),
            (33,'Thrift 2','Allurists Guild 2',3000,'Buy 1 Perfect Red Rose from 3 specified shops.','10% chance to keep a used item/scroll instead of it burning up.'),
            (34,'Thrift 3','Allurists Guild 3',10000,'Buy 1 Perfect Red Rose from 6 specified shops.','15% chance to keep a used item/scroll instead of it burning up.')
        ]),
        ("REPLACE INTO `rows` (ID, Name, Coordinate) VALUES (?, ?, ?)", [
            ('1', 'NCL', '0'),
            ('2', 'Northern City Limits', '0'),
            ('3', '1st', '2'),
            ('4', '2nd', '4'),
            ('5', '3rd', '6'),
            ('6', '4th', '8'),
            ('7', '5th', '10'),
            ('8', '6th', '12'),
            ('9', '7th', '14'),
            ('10', '8th', '16'),
            ('11', '9th', '18'),
            ('12', '10th', '20'),
            ('13', '11th', '22'),
            ('14', '12th', '24'),
            ('15', '13th', '26'),
            ('16', '14th', '28'),
            ('17', '15th', '30'),
            ('18', '16th', '32'),
            ('19', '17th', '34'),
            ('20', '18th', '36'),
            ('21', '19th', '38'),
            ('22', '20th', '40'),
            ('23', '21st', '42'),
            ('24', '22nd', '44'),
            ('25', '23rd', '46'),
            ('26', '24th', '48'),
            ('27', '25th', '50'),
            ('28', '26th', '52'),
            ('29', '27th', '54'),
            ('30', '28th', '56'),
            ('31', '29th', '58'),
            ('32', '30th', '60'),
            ('33', '31st', '62'),
            ('34', '32nd', '64'),
            ('35', '33rd', '66'),
            ('36', '34th', '68'),
            ('37', '35th', '70'),
            ('38', '36th', '72'),
            ('39', '37th', '74'),
            ('40', '38th', '76'),
            ('41', '39th', '78'),
            ('42', '40th', '80'),
            ('43', '41st', '82'),
            ('44', '42nd', '84'),
            ('45', '43rd', '86'),
            ('46', '44th', '88'),
            ('47', '45th', '90'),
            ('48', '46th', '92'),
            ('49', '47th', '94'),
            ('50', '48th', '96'),
            ('51', '49th', '98'),
            ('52', '50th', '100'),
            ('53', '51st', '102'),
            ('54', '52nd', '104'),
            ('55', '53rd', '106'),
            ('56', '54th', '108'),
            ('57', '55th', '110'),
            ('58', '56th', '112'),
            ('59', '57th', '114'),
            ('60', '58th', '116'),
            ('61', '59th', '118'),
            ('62', '60th', '120'),
            ('63', '61st', '122'),
            ('64', '62nd', '124'),
            ('65', '63rd', '126'),
            ('66', '64th', '128'),
            ('67', '65th', '130'),
            ('68', '66th', '132'),
            ('69', '67th', '134'),
            ('70', '68th', '136'),
            ('71', '69th', '138'),
            ('72', '70th', '140'),
            ('73', '71st', '142'),
            ('74', '72nd', '144'),
            ('75', '73rd', '146'),
            ('76', '74th', '148'),
            ('77', '75th', '150'),
            ('78', '76th', '152'),
            ('79', '77th', '154'),
            ('80', '78th', '156'),
            ('81', '79th', '158'),
            ('82', '80th', '160'),
            ('83', '81st', '162'),
            ('84', '82nd', '164'),
            ('85', '83rd', '166'),
            ('86', '84th', '168'),
            ('87', '85th', '170'),
            ('88', '86th', '172'),
            ('89', '87th', '174'),
            ('90', '88th', '176'),
            ('91', '89th', '178'),
            ('92', '90th', '180'),
            ('93', '91st', '182'),
            ('94', '92nd', '184'),
            ('95', '93rd', '186'),
            ('96', '94th', '188'),
            ('97', '95th', '190'),
            ('98', '96th', '192'),
            ('99', '97th', '194'),
            ('100', '98th', '196'),
            ('101', '99th', '198'),
            ('102', '100th', '200')
        ]),
        ("REPLACE INTO shop_items (id, shop_name, item_name, base_price, charisma_level_1, charisma_level_2, charisma_level_3) VALUES (?, ?, ?, ?, ?, ?, ?)", [
            (1,'Discount Magic','Perfect Dandelion',35,33,32,31),
            (2,'Discount Magic','Sprint Potion',105,101,97,94),
            (3,'Discount Magic','Perfect Red Rose',350,339,325,315),
            (4,'Discount Magic','Scroll of Turning',350,339,325,315),
            (5,'Discount Magic','Scroll of Succour',525,509,488,472),
            (6,'Discount Magic','Scroll of Bondage',637,617,592,573),
            (7,'Discount Magic','Garlic Spray',700,678,651,630),
            (8,'Discount Magic','Scroll of Displacement',700,678,651,630),
            (9,'Discount Magic','Perfect Black Orchid',795,772,740,716),
            (10,'Discount Magic','Scroll of Summoning',1050,1018,976,945),
            (11,'Discount Magic','Vial of Holy Water',1400,1357,1302,1260),
            (12,'Discount Magic','Wooden Stake',2800,2715,2604,2520),
            (13,'Discount Magic','Scroll of Accounting',3500,3394,3255,3150),
            (14,'Discount Magic','Scroll of Teleportation',3500,3394,3255,3150),
            (15,'Discount Magic','UV Grenade',3500,3394,3255,3150),
            (16,'Discount Magic','Ring of Resistance',14000,13579,13020,12600),
            (17,'Discount Magic','Diamond Ring',70000,67900,65100,63000),
            (18,'Discount Potions','Sprint Potion',105,101,97,94),
            (19,'Discount Potions','Garlic Spray',700,678,651,630),
            (20,'Discount Potions','Vial of Holy Water',1400,1357,1302,1260),
            (21,'Discount Potions','Blood Potion',30000,30000,30000,30000),
            (22,'Discount Potions','Necromancer',25,25,25,25),
            (23,'Discount Scrolls','Scroll of Turning',350,339,325,315),
            (24,'Discount Scrolls','Scroll of Succour',525,509,488,472),
            (25,'Discount Scrolls','Scroll of Displacement',700,678,651,630),
            (26,'Discount Scrolls','Scroll of Summoning',1050,1018,976,945),
            (27,'Discount Scrolls','Scroll of Accounting',3500,3394,3255,3150),
            (28,'Discount Scrolls','Scroll of Teleportation',3500,3394,3255,3150),
            (29,'Dark Desires','Perfect Dandelion',50,48,46,45),
            (30,'Dark Desires','Sprint Potion',150,145,139,135),
            (31,'Dark Desires','Perfect Red Rose',500,485,465,450),
            (32,'Dark Desires','Scroll of Turning',500,485,465,450),
            (33,'Dark Desires','Scroll of Succour',750,727,697,675),
            (34,'Dark Desires','Scroll of Bondage',910,882,846,819),
            (35,'Dark Desires','Garlic Spray',1000,970,930,900),
            (36,'Dark Desires','Scroll of Displacement',1000,970,930,900),
            (37,'Dark Desires','Perfect Black Orchid',1137,1102,1057,1023),
            (38,'Dark Desires','Scroll of Summoning',1500,1455,1395,1350),
            (39,'Dark Desires','Vial of Holy Water',2000,1940,1860,1800),
            (40,'Dark Desires','Wooden Stake',4000,3880,3720,3600),
            (41,'Dark Desires','Scroll of Accounting',5000,4850,4650,4500),
            (42,'Dark Desires','Scroll of Teleportation',5000,4850,4650,4500),
            (43,'Dark Desires','UV Grenade',5000,4850,4650,4500),
            (44,'Dark Desires','Ring of Resistance',20000,19400,18600,18000),
            (45,'Dark Desires','Diamond Ring',100000,97000,93000,90000),
            (46,'Interesting Times','Perfect Dandelion',50,48,46,45),
            (47,'Interesting Times','Sprint Potion',150,145,139,135),
            (48,'Interesting Times','Perfect Red Rose',500,485,465,450),
            (49,'Interesting Times','Scroll of Turning',500,485,465,450),
            (50,'Interesting Times','Scroll of Succour',750,727,697,675),
            (51,'Interesting Times','Scroll of Bondage',910,882,846,819),
            (52,'Interesting Times','Garlic Spray',1000,970,930,900),
            (53,'Interesting Times','Scroll of Displacement',1000,970,930,900),
            (54,'Interesting Times','Perfect Black Orchid',1137,1102,1057,1023),
            (55,'Interesting Times','Scroll of Summoning',1500,1455,1395,1350),
            (56,'Interesting Times','Vial of Holy Water',2000,1940,1860,1800),
            (57,'Interesting Times','Wooden Stake',4000,3880,3720,3600),
            (58,'Interesting Times','Scroll of Accounting',5000,4850,4650,4500),
            (59,'Interesting Times','Scroll of Teleportation',5000,4850,4650,4500),
            (60,'Interesting Times','UV Grenade',5000,4850,4650,4500),
            (61,'Interesting Times','Ring of Resistance',20000,19400,18600,18000),
            (62,'Interesting Times','Diamond Ring',100000,97000,93000,90000),
            (63,'Sparks','Perfect Dandelion',50,48,46,45),
            (64,'Sparks','Sprint Potion',150,145,139,135),
            (65,'Sparks','Perfect Red Rose',500,485,465,450),
            (66,'Sparks','Scroll of Turning',500,485,465,450),
            (67,'Sparks','Scroll of Succour',750,727,697,675),
            (68,'Sparks','Scroll of Bondage',910,882,846,819),
            (69,'Sparks','Garlic Spray',1000,970,930,900),
            (70,'Sparks','Scroll of Displacement',1000,970,930,900),
            (71,'Sparks','Perfect Black Orchid',1137,1102,1057,1023),
            (72,'Sparks','Scroll of Summoning',1500,1455,1395,1350),
            (73,'Sparks','Vial of Holy Water',2000,1940,1860,1800),
            (74,'Sparks','Wooden Stake',4000,3880,3720,3600),
            (75,'Sparks','Scroll of Accounting',5000,4850,4650,4500),
            (76,'Sparks','Scroll of Teleportation',5000,4850,4650,4500),
            (77,'Sparks','UV Grenade',5000,4850,4650,4500),
            (78,'Sparks','Ring of Resistance',20000,19400,18600,18000),
            (79,'Sparks','Diamond Ring',100000,97000,93000,90000),
            (80,'The Magic Box','Perfect Dandelion',50,48,46,45),
            (81,'The Magic Box','Sprint Potion',150,145,139,135),
            (82,'The Magic Box','Perfect Red Rose',500,485,465,450),
            (83,'The Magic Box','Scroll of Turning',500,485,465,450),
            (84,'The Magic Box','Scroll of Succour',750,727,697,675),
            (85,'The Magic Box','Scroll of Bondage',910,882,846,819),
            (86,'The Magic Box','Garlic Spray',1000,970,930,900),
            (87,'The Magic Box','Scroll of Displacement',1000,970,930,900),
            (88,'The Magic Box','Perfect Black Orchid',1137,1102,1057,1023),
            (89,'The Magic Box','Scroll of Summoning',1500,1455,1395,1350),
            (90,'The Magic Box','Vial of Holy Water',2000,1940,1860,1800),
            (91,'The Magic Box','Wooden Stake',4000,3880,3720,3600),
            (92,'The Magic Box','Scroll of Accounting',5000,4850,4650,4500),
            (93,'The Magic Box','Scroll of Teleportation',5000,4850,4650,4500),
            (94,'The Magic Box','UV Grenade',5000,4850,4650,4500),
            (95,'The Magic Box','Ring of Resistance',20000,19400,18600,18000),
            (96,'The Magic Box','Diamond Ring',100000,97000,93000,90000),
            (97,'White Light','Perfect Dandelion',50,48,46,45),
            (98,'White Light','Sprint Potion',150,145,139,135),
            (99,'White Light','Perfect Red Rose',500,485,465,450),
            (100,'White Light','Scroll of Turning',500,485,465,450),
            (101,'White Light','Scroll of Succour',750,727,697,675),
            (102,'White Light','Scroll of Bondage',910,882,846,819),
            (103,'White Light','Garlic Spray',1000,970,930,900),
            (104,'White Light','Scroll of Displacement',1000,970,930,900),
            (105,'White Light','Perfect Black Orchid',1137,1102,1057,1023),
            (106,'White Light','Scroll of Summoning',1500,1455,1395,1350),
            (107,'White Light','Vial of Holy Water',2000,1940,1860,1800),
            (108,'White Light','Wooden Stake',4000,3880,3720,3600),
            (109,'White Light','Scroll of Accounting',5000,4850,4650,4500),
            (110,'White Light','Scroll of Teleportation',5000,4850,4650,4500),
            (111,'White Light','UV Grenade',5000,4850,4650,4500),
            (112,'White Light','Ring of Resistance',20000,19400,18600,18000),
            (113,'White Light','Diamond Ring',100000,97000,93000,90000),
            (114,'McPotions','Sprint Potion',150,145,139,135),
            (115,'McPotions','Garlic Spray',1000,970,930,900),
            (116,'McPotions','Vial of Holy Water',2000,1940,1860,1800),
            (117,'McPotions','Blood Potion',30000,30000,30000,30000),
            (118,'McPotions','Necromancer',25,25,25,25),
            (119,'Potable Potions','Sprint Potion',150,145,139,135),
            (120,'Potable Potions','Garlic Spray',1000,970,930,900),
            (121,'Potable Potions','Vial of Holy Water',2000,1940,1860,1800),
            (122,'Potable Potions','Blood Potion',30000,30000,30000,30000),
            (123,'Potable Potions','Necromancer',25,25,25,25),
            (124,'Potion Distillery','Sprint Potion',150,145,139,135),
            (125,'Potion Distillery','Garlic Spray',1000,970,930,900),
            (126,'Potion Distillery','Vial of Holy Water',2000,1940,1860,1800),
            (127,'Potion Distillery','Blood Potion',30000,30000,30000,30000),
            (128,'Potion Distillery','Necromancer',25,25,25,25),
            (129,'Potionworks','Sprint Potion',150,145,139,135),
            (130,'Potionworks','Garlic Spray',1000,970,930,900),
            (131,'Potionworks','Vial of Holy Water',2000,1940,1860,1800),
            (132,'Potionworks','Blood Potion',30000,30000,30000,30000),
            (133,'Potionworks','Necromancer',25,25,25,25),
            (134,'Silver Apothecary','Sprint Potion',150,145,139,135),
            (135,'Silver Apothecary','Garlic Spray',1000,970,930,900),
            (136,'Silver Apothecary','Vial of Holy Water',2000,1940,1860,1800),
            (137,'Silver Apothecary','Blood Potion',30000,30000,30000,30000),
            (138,'Silver Apothecary','Perfect Dandelion',50,48,46,45),
            (139,'Silver Apothecary','Perfect Red Rose',500,485,465,450),
            (140,'Silver Apothecary','Perfect Black Orchid',1137,1102,1057,1023),
            (141,'Silver Apothecary','Diamond Ring',100000,97000,93000,90000),
            (142,'Silver Apothecary','Necromancer',25,25,25,25),
            (143,'The Potion Shoppe','Sprint Potion',150,145,139,135),
            (144,'The Potion Shoppe','Garlic Spray',1000,970,930,900),
            (145,'The Potion Shoppe','Vial of Holy Water',2000,1940,1860,1800),
            (146,'The Potion Shoppe','Blood Potion',30000,30000,30000,30000),
            (147,'The Potion Shoppe','Necromancer',25,25,25,25),
            (148,'Herman''s Scrolls','Scroll of Turning',500,485,465,450),
            (149,'Herman''s Scrolls','Scroll of Succour',750,727,697,675),
            (150,'Herman''s Scrolls','Scroll of Displacement',1000,970,930,900),
            (151,'Herman''s Scrolls','Scroll of Summoning',1500,1455,1395,1350),
            (152,'Herman''s Scrolls','Scroll of Accounting',5000,4850,4650,4500),
            (153,'Herman''s Scrolls','Scroll of Teleportation',5000,4850,4650,4500),
            (154,'Paper and Scrolls','Scroll of Turning',500,485,465,450),
            (155,'Paper and Scrolls','Scroll of Succour',750,727,697,675),
            (156,'Paper and Scrolls','Scroll of Displacement',1000,970,930,900),
            (157,'Paper and Scrolls','Scroll of Summoning',1500,1455,1395,1350),
            (158,'Paper and Scrolls','Scroll of Accounting',5000,4850,4650,4500),
            (159,'Paper and Scrolls','Scroll of Teleportation',5000,4850,4650,4500),
            (160,'Scrollmania','Scroll of Turning',500,485,465,450),
            (161,'Scrollmania','Scroll of Succour',750,727,697,675),
            (162,'Scrollmania','Scroll of Displacement',1000,970,930,900),
            (163,'Scrollmania','Scroll of Summoning',1500,1455,1395,1350),
            (164,'Scrollmania','Scroll of Accounting',5000,4850,4650,4500),
            (165,'Scrollmania','Scroll of Teleportation',5000,4850,4650,4500),
            (166,'Scrolls ''n'' Stuff','Scroll of Turning',500,485,465,450),
            (167,'Scrolls ''n'' Stuff','Scroll of Succour',750,727,697,675),
            (168,'Scrolls ''n'' Stuff','Scroll of Displacement',1000,970,930,900),
            (169,'Scrolls ''n'' Stuff','Scroll of Summoning',1500,1455,1395,1350),
            (170,'Scrolls ''n'' Stuff','Scroll of Accounting',5000,4850,4650,4500),
            (171,'Scrolls ''n'' Stuff','Scroll of Teleportation',5000,4850,4650,4500),
            (172,'Scrolls R Us','Scroll of Turning',500,485,465,450),
            (173,'Scrolls R Us','Scroll of Succour',750,727,697,675),
            (174,'Scrolls R Us','Scroll of Displacement',1000,970,930,900),
            (175,'Scrolls R Us','Scroll of Summoning',1500,1455,1395,1350),
            (176,'Scrolls R Us','Scroll of Accounting',5000,4850,4650,4500),
            (177,'Scrolls R Us','Scroll of Teleportation',5000,4850,4650,4500),
            (178,'Scrollworks','Scroll of Turning',500,485,465,450),
            (179,'Scrollworks','Scroll of Succour',750,727,697,675),
            (180,'Scrollworks','Scroll of Displacement',1000,970,930,900),
            (181,'Scrollworks','Scroll of Summoning',1500,1455,1395,1350),
            (182,'Scrollworks','Scroll of Accounting',5000,4850,4650,4500),
            (183,'Scrollworks','Scroll of Teleportation',5000,4850,4650,4500),
            (184,'Ye Olde Scrolles','Scroll of Turning',500,485,465,450),
            (185,'Ye Olde Scrolles','Scroll of Succour',750,727,697,675),
            (186,'Ye Olde Scrolles','Scroll of Displacement',1000,970,930,900),
            (187,'Ye Olde Scrolles','Scroll of Summoning',1500,1455,1395,1350),
            (188,'Ye Olde Scrolles','Scroll of Accounting',5000,4850,4650,4500),
            (189,'Ye Olde Scrolles','Scroll of Teleportation',5000,4850,4650,4500),
            (190,'Eternal Aubade of Mystical Treasures','Perfect Dandelion',55,55,55,55),
            (191,'Eternal Aubade of Mystical Treasures','Sprint Potion',165,165,165,165),
            (192,'Eternal Aubade of Mystical Treasures','Perfect Red Rose',550,550,550,550),
            (193,'Eternal Aubade of Mystical Treasures','Scroll of Succour',825,25,25,25),
            (194,'Eternal Aubade of Mystical Treasures','Scroll of Bondage',1001,1001,1001,1001),
            (195,'Eternal Aubade of Mystical Treasures','Perfect Black Orchid',1250,1250,1250,1250),
            (196,'Eternal Aubade of Mystical Treasures','Gold Dawn to Dusk Tulip',1500,1500,1500,1500),
            (197,'Eternal Aubade of Mystical Treasures','Wooden Stake',4400,4400,4400,4400),
            (198,'Eternal Aubade of Mystical Treasures','Kitten',10000,10000,10000,10000),
            (199,'Eternal Aubade of Mystical Treasures','Wolf Pup',12500,12500,12500,12500),
            (200,'Eternal Aubade of Mystical Treasures','Dragon''s Egg',17499,17499,17499,17499),
            (201,'Eternal Aubade of Mystical Treasures','Silver Pocket Watch',20000,20000,20000,20000),
            (202,'Eternal Aubade of Mystical Treasures','Crystal Music Box',25000,25000,25000,25000),
            (203,'Eternal Aubade of Mystical Treasures','Blood Potion',33000,33000,33000,33000),
            (204,'Eternal Aubade of Mystical Treasures','Hand Mirror of Truth',35000,35000,35000,35000),
            (205,'Eternal Aubade of Mystical Treasures','Book of Spells',44999,44999,44999,44999),
            (206,'Eternal Aubade of Mystical Treasures','Ritual Gown',55000,55000,55000,55000),
            (207,'Eternal Aubade of Mystical Treasures','Silver Ruby Dagger',65000,65000,65000,65000),
            (208,'Eternal Aubade of Mystical Treasures','Onyx Coffin',75000,75000,75000,75000),
            (209,'Eternal Aubade of Mystical Treasures','Platinum Puzzle Rings',115000,115000,115000,115000),
            (210,'Eternal Aubade of Mystical Treasures','Diamond Succubus Earrings',125000,125000,125000,125000),
            (211,'The Cloister of Secrets','Perfect Dandelion',55,55,55,55),
            (212,'The Cloister of Secrets','Perfect Red Rose',550,550,550,550),
            (213,'The Cloister of Secrets','Perfect Black Orchid',1250,1250,1250,1250),
            (214,'The Cloister of Secrets','Safety Deposit Box Key',11000,11000,11000,11000),
            (215,'The Cloister of Secrets','Necklace with Locket',55000,55000,55000,55000),
            (216,'The Cloister of Secrets','Flask of Heinous Deceptions',77000,77000,77000,77000),
            (217,'The Cloister of Secrets','Amulet of Insidious Illusions',88000,88000,88000,88000),
            (218,'The Cloister of Secrets','Golden Ring',99000,99000,99000,99000),
            (219,'The Cloister of Secrets','Diamond Ring',110000,110000,110000,110000),
            (220,'The Cloister of Secrets','Titanium-Platinum Ring',110000,110000,110000,110000),
            (221,'Grotto of Deceptions','Scroll of Turning',550,550,550,550),
            (222,'Grotto of Deceptions','Scroll of Teleportation',5500,5500,5500,5500),
            (223,'Grotto of Deceptions','Scroll of Displacement',1100,1100,1100,1100),
            (224,'Grotto of Deceptions','Scroll of Succour',825,825,825,825),
            (225,'Grotto of Deceptions','Vial of Holy Water',2200,2200,2200,2200),
            (226,'Grotto of Deceptions','Garlic Spray',1100,1100,1100,1100),
            (227,'Grotto of Deceptions','Sprint Potion',165,165,165,165),
            (228,'Grotto of Deceptions','Perfect Dandelion',55,55,55,55),
            (229,'Grotto of Deceptions','Perfect Red Rose',550,550,550,550),
            (230,'Grotto of Deceptions','Perfect Black Orchid',1100,1100,1100,1100),
            (231,'NightWatch Headquarters','Memorial Candle',200,200,200,200),
            (232,'NightWatch Headquarters','Perfect Red Rose',550,550,550,550),
            (233,'The Ixora Estate','Perfect Ixora Cluster',550,550,550,550),
            (234,'The Ixora Estate','Perfect Dandelion',55,55,55,55),
            (235,'The Ixora Estate','Perfect Black Orchid',1100,1100,1100,1100),
            (236,'The Ixora Estate','Perfect Red Rose',550,550,550,550),
            (237,'The White House','Perfect Red Rose',550,550,550,550),
            (238,'The White House','Perfect Black Orchid',1250,1250,1250,1250),
            (239,'The White House','Pewter Celtic Cross',10000,10000,10000,10000),
            (240,'The White House','Compass',11999,11999,11999,11999),
            (241,'The White House','Pewter Tankard',15000,15000,15000,15000)
        ]),
        ("REPLACE INTO discord_servers (id, name, invite_link) VALUES (?, ?, ?)", [
            (1, "RBC Community Map Hub", "https://discord.gg/rKamEZvK6X"),
            (2, "Ab Antiquo Headquarters", "https://discord.gg/AhPEzkJyA4"),
            (3, "Hellfire Club", "https://discord.gg/qZCbbKEt3z"),
            (4, "RB Improvement Group", "https://discord.gg/8ent8jn54u"),
            (5, "RBCH", "https://discord.gg/ktdG9FZ"),
            (6, "Raven Black: Boroughs and Barrios", "https://discord.gg/RTSXJ5tC4d"),
            (7, "RavenBlack Community Center", "https://discord.gg/SVMmGcvNCV"),
            (8, "The Moon over Orion", "https://discord.gg/EArPr7vqHC"),
            (9, "The Ravenblack Historical Society", "https://discord.gg/zqPXpw8sMw"),
            (10, "rêverie", "https://discord.gg/jAVHpGvgCf")
        ])
    ]
    for query, data in initial_data:
        try:
            cursor.executemany(query, data)
            logging.debug(f"Inserted initial data into: {query.split('INTO ')[1].split(' ')[0]}")
        except sqlite3.Error as e:
            logging.error(f"Failed to insert data into {query.split('INTO ')[1].split(' ')[0]}: {e}")
            raise
    conn.commit()

def migrate_schema(conn: sqlite3.Connection) -> None:
    """
    Migrate the database schema to the latest version.

    Handles sequential migrations:
    - v1 -> v2: Fixes custom_css, guilds, and shops tables.
    - v2 -> v3: Adds active_cookie column to characters table.
    - v3 -> v4: Adds last_scraped column to guilds and shops tables.
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA user_version")
    version = cursor.fetchone()[0]

    if version < 2:
        logging.info("Applying schema migration: v1 → v2 (fixing custom_css, guilds, and shops)")

        try:
            # --- Step 1: Fix custom_css table ---
            cursor.execute("PRAGMA table_info(custom_css)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'profile_name' not in columns:
                logging.info("custom_css missing profile_name column. Rebuilding custom_css table.")
                cursor.execute("ALTER TABLE custom_css RENAME TO custom_css_old")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_css (
                        profile_name TEXT NOT NULL,
                        element TEXT NOT NULL,
                        value TEXT NOT NULL,
                        PRIMARY KEY (profile_name, element),
                        FOREIGN KEY (profile_name) REFERENCES css_profiles(profile_name) ON DELETE CASCADE
                    )
                """)
                try:
                    # noinspection SqlResolve
                    cursor.execute("""
                        INSERT INTO custom_css (element, value, profile_name)
                        SELECT element, value, 'Default' FROM custom_css_old
                    """)
                    logging.info("Migrated old custom_css data successfully.")
                except sqlite3.Error as e:
                    logging.warning(f"Failed to migrate custom_css data: {e}")
                cursor.execute("DROP TABLE IF EXISTS custom_css_old")

            # --- Step 2: Fix guilds table ---
            cursor.execute("PRAGMA index_list(guilds)")
            indexes = cursor.fetchall()
            unique_names = [index[1] for index in indexes if index[2]]  # index[2] == 1 means UNIQUE
            if not any('Name' in idx for idx in unique_names):
                logging.info("guilds table missing UNIQUE constraint on Name. Rebuilding guilds table.")
                cursor.execute("ALTER TABLE guilds RENAME TO guilds_old")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS guilds (
                        ID INTEGER PRIMARY KEY,
                        Name TEXT NOT NULL UNIQUE,
                        Column TEXT NOT NULL,
                        Row TEXT NOT NULL,
                        next_update TIMESTAMP DEFAULT NULL
                    )
                """)
                try:
                    # noinspection SqlResolve
                    cursor.execute("""
                        INSERT INTO guilds (ID, Name, `Column`, Row, next_update)
                        SELECT ID, Name, `Column`, `Row`, next_update FROM guilds_old
                    """)
                    logging.info("Migrated old guilds data successfully.")
                except sqlite3.Error as e:
                    logging.warning(f"Failed to migrate guilds data: {e}")
                cursor.execute("DROP TABLE IF EXISTS guilds_old")

            # --- Step 3: Fix shops table ---
            cursor.execute("PRAGMA index_list(shops)")
            shops_indexes = cursor.fetchall()
            shops_has_unique_name = any('Name' in idx for idx in shops_indexes if idx[2])

            if not shops_has_unique_name:
                logging.info("shops table missing UNIQUE constraint on Name. Rebuilding shops table.")
                cursor.execute("ALTER TABLE shops RENAME TO shops_old")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shops (
                        ID INTEGER PRIMARY KEY,
                        Name TEXT NOT NULL UNIQUE,
                        Column TEXT NOT NULL,
                        Row TEXT NOT NULL,
                        next_update TIMESTAMP DEFAULT NULL
                    )
                """)
                try:
                    # noinspection SqlResolve
                    cursor.execute("""
                        INSERT INTO shops (ID, Name, `Column`, Row, next_update)
                        SELECT ID, Name, `Column`, `Row`, next_update FROM shops_old
                    """)
                    logging.info("Migrated old shops data successfully.")
                except sqlite3.Error as e:
                    logging.warning(f"Failed to migrate shops data: {e}")
                cursor.execute("DROP TABLE IF EXISTS shops_old")

            # --- Finish migration ---
            conn.execute("PRAGMA user_version = 2")
            conn.commit()
            logging.info("Migration to v2 complete.")

        except sqlite3.Error as e:
            logging.error(f"Migration v2 failed: {e}")
            conn.rollback()
            raise

    if version < 3:
        logging.info("Applying schema migration: v2 → v3 (add active_cookie to characters)")

        try:
            cursor.execute("PRAGMA table_info(characters)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'active_cookie' not in columns:
                logging.info("characters table missing active_cookie column. Adding column.")
                cursor.execute("ALTER TABLE characters ADD COLUMN active_cookie INTEGER DEFAULT NULL")
            else:
                logging.info("characters table already has active_cookie column. Skipping.")

            conn.execute("PRAGMA user_version = 3")
            conn.commit()
            logging.info("Migration to v3 complete.")

        except sqlite3.Error as e:
            logging.error(f"Migration v3 failed: {e}")
            conn.rollback()
            raise

    if version < 4:
        logging.info("Applying schema migration: v3 → v4 (add last_scraped to guilds and shops)")

        try:
            # --- Add last_scraped to guilds ---
            cursor.execute("PRAGMA table_info(guilds)")
            guilds_columns = [col[1] for col in cursor.fetchall()]
            if 'last_scraped' not in guilds_columns:
                logging.info("guilds table missing last_scraped column. Adding column.")
                cursor.execute("ALTER TABLE guilds ADD COLUMN last_scraped TEXT DEFAULT NULL")
            else:
                logging.info("guilds table already has last_scraped column. Skipping.")

            # --- Add last_scraped to shops ---
            cursor.execute("PRAGMA table_info(shops)")
            shops_columns = [col[1] for col in cursor.fetchall()]
            if 'last_scraped' not in shops_columns:
                logging.info("shops table missing last_scraped column. Adding column.")
                cursor.execute("ALTER TABLE shops ADD COLUMN last_scraped TEXT DEFAULT NULL")
            else:
                logging.info("shops table already has last_scraped column. Skipping.")

            conn.execute("PRAGMA user_version = 4")
            conn.commit()
            logging.info("Migration to v4 complete.")

        except sqlite3.Error as e:
            logging.error(f"Migration v4 failed: {e}")
            conn.rollback()
            raise

def initialize_database(db_path: str = DB_PATH) -> bool:
    """
    Initialize the SQLite database with the required schema and data.

    Args:
        db_path (str, optional): Path to the SQLite database file. Defaults to DB_PATH.

    Returns:
        bool: True if initialization succeeds, False if an error occurs.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
            create_tables(conn)                       # Fist create missing tables
            migrate_schema(conn)                      # Then migrate schema
            insert_initial_data(conn)                 # THEN populate defaults
            logging.info(f"Database initialized successfully at {db_path}")
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to initialize database at {db_path}: {e}")
        return False

# Call database initialization
if not ensure_directories_exist():  # Ensure directories exist first
    logging.error("Required directories could not be created. Aborting database initialization.")
elif not initialize_database(DB_PATH):
    logging.warning("Database initialization failed. Application may encounter issues.")

# -----------------------
# Load Data from Database
# -----------------------

def load_data() -> tuple:
    """
    Load map-related data from the SQLite database.

    Also loads:
    - keybind configuration
    - active CSS profile
    - last active character
    - most recent destination
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # -----------------------
            # Coordinate Mappings
            # -----------------------

            cursor.execute("SELECT Name, Coordinate FROM columns")
            columns = {name: coord for name, coord in cursor.fetchall()}

            cursor.execute("SELECT Name, Coordinate FROM rows")
            rows = {name: coord for name, coord in cursor.fetchall()}

            def to_coords(col_name: str, row_name: str) -> tuple[int | None, int | None]:
                if col_name not in columns or row_name not in rows:
                    logging.warning(
                        "Could not resolve coordinates for %s & %s",
                        col_name,
                        row_name,
                    )
                    return None, None
                return columns[col_name] + 1, rows[row_name] + 1

            # -----------------------
            # Banks (string-based)
            # -----------------------

            banks_coordinates: dict[str, tuple[str, str]] = {}
            cursor.execute("SELECT Column, Row FROM banks")
            for col_name, row_name in cursor.fetchall():
                banks_coordinates[f"{col_name} & {row_name}"] = (col_name, row_name)

            # -----------------------
            # Coordinate-Based Entities
            # -----------------------

            taverns_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute(
                    "SELECT Name, Column, Row FROM taverns"
                )
            }

            transits_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute(
                    "SELECT Name, Column, Row FROM transits"
                )
            }

            user_buildings_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute(
                    "SELECT Name, Column, Row FROM userbuildings"
                )
            }

            # -----------------------
            # Color Mappings
            # -----------------------

            color_mappings: dict[str, PySide6.QtGui.QColor] = {}
            for type_, color in cursor.execute(
                    "SELECT type, color FROM color_mappings"
            ):
                qcolor = PySide6.QtGui.QColor(color)
                if not qcolor.isValid():
                    logging.warning(
                        "Invalid color value for '%s': %s",
                        type_,
                        color,
                    )
                    qcolor = PySide6.QtGui.QColor("#000000")
                color_mappings[type_] = qcolor

            # -----------------------
            # Shops & Guilds
            # -----------------------

            shops_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute(
                    "SELECT Name, Column, Row FROM shops"
                )
                if col != "NA" and row != "NA"
            }

            guilds_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute(
                    "SELECT Name, Column, Row FROM guilds"
                )
                if col != "NA" and row != "NA"
            }

            # -----------------------
            # Points of Interest
            # -----------------------

            places_of_interest_coordinates: dict[str, tuple[int, int]] = {}
            cursor.execute("SELECT Name, Column, Row FROM placesofinterest")

            for name, col, row in cursor.fetchall():
                coords = to_coords(col, row)
                if coords == (None, None):
                    logging.warning(
                        "Skipping POI '%s' due to unresolved coordinates (%s, %s)",
                        name,
                        col,
                        row,
                    )
                else:
                    places_of_interest_coordinates[name] = coords

            # -----------------------
            # Settings
            # -----------------------

            cursor.execute(
                "SELECT setting_value FROM settings WHERE setting_name = 'keybind_config'"
            )
            row = cursor.fetchone()
            keybind_config = int(row[0]) if row else 1

            cursor.execute(
                "SELECT setting_value FROM settings WHERE setting_name = 'css_profile'"
            )
            row = cursor.fetchone()
            current_css_profile = row[0] if row else "Default"

            # -----------------------
            # Last Active Character
            # -----------------------

            selected_character = None
            last_destination = None

            cursor.execute(
                "SELECT character_id FROM last_active_character LIMIT 1"
            )
            row = cursor.fetchone()

            if row:
                character_id = row[0]
                cursor.execute(
                    "SELECT id, name, password FROM characters WHERE id = ?",
                    (character_id,),
                )
                char = cursor.fetchone()

                if char:
                    selected_character = {
                        "id": char[0],
                        "name": char[1],
                        "password": char[2],
                    }

                    cursor.execute(
                        """
                        SELECT col, row
                        FROM destinations
                        WHERE character_id = ?
                        ORDER BY timestamp DESC
                        LIMIT 1
                        """,
                        (character_id,),
                    )
                    dest = cursor.fetchone()
                    if dest:
                        last_destination = (dest[0], dest[1])

            logging.debug("Database data loaded successfully")

            return (
                columns,
                rows,
                banks_coordinates,
                taverns_coordinates,
                transits_coordinates,
                user_buildings_coordinates,
                color_mappings,
                shops_coordinates,
                guilds_coordinates,
                places_of_interest_coordinates,
                keybind_config,
                current_css_profile,
                selected_character,
                last_destination,
            )

    except sqlite3.Error as exc:
        logging.error(
            "Failed to load data from database %s: %s",
            DB_PATH,
            exc,
        )
        raise

# -----------------------
# Load Data at Startup
# -----------------------

try:
    (
        columns,
        rows,
        banks_coordinates,
        taverns_coordinates,
        transits_coordinates,
        user_buildings_coordinates,
        color_mappings,
        shops_coordinates,
        guilds_coordinates,
        places_of_interest_coordinates,
        keybind_config,
        current_css_profile,
        selected_character,
        last_destination,
    ) = load_data()

except sqlite3.Error:
    logging.critical(
        "Database load failed. Falling back to empty runtime data."
    )

    columns = rows = {}
    banks_coordinates = {}
    taverns_coordinates = {}
    transits_coordinates = {}
    user_buildings_coordinates = {}
    shops_coordinates = {}
    guilds_coordinates = {}
    places_of_interest_coordinates = {}

    color_mappings = {
        "default": PySide6.QtGui.QColor("#000000")
    }

    keybind_config = 1
    current_css_profile = "Default"
    selected_character = None
    last_destination = None
