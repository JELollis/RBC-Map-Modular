from directories import *

def create_tables(conn: sqlite3.Connection) -> None:
    """Create database tables if they don’t exist."""
    cursor = conn.cursor()
    tables = [
        """CREATE TABLE IF NOT EXISTS banks (
            ID INTEGER PRIMARY KEY,
            Column TEXT NOT NULL,
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
            Column TEXT NOT NULL,
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
            Column TEXT NOT NULL,
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
            Column TEXT NOT NULL,
            Row TEXT NOT NULL,
            next_update TIMESTAMP DEFAULT NULL,
            last_scraped TIMESTAMP DEFAULT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS taverns (
            ID INTEGER PRIMARY KEY,
            Column TEXT NOT NULL,
            Row TEXT NOT NULL,
            Name TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS transits (
            ID INTEGER PRIMARY KEY,
            Column TEXT NOT NULL,
            Row TEXT NOT NULL,
            Name TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS userbuildings (
            ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Column TEXT NOT NULL,
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

        ("INSERT OR IGNORE INTO banks (ID, Column, Row, Name) VALUES (?, ?, ?, ?)", [
            (1,'Aardvark','82nd','OmniBank'),
            (2,'Alder','40th','OmniBank'),
             (3,'Alder','80th','OmniBank'),
             (4,'Amethyst','16th','OmniBank'),
             (5,'Amethyst','37th','OmniBank'),
             (6,'Amethyst','99th','OmniBank'),
             (7,'Anguish','30th','OmniBank'),
             (8,'Anguish','73rd','OmniBank'),
             (9,'Anguish','91st','OmniBank'),
             (10,'Beech','26th','OmniBank'),
             (11,'Beech','39th','OmniBank'),
             (12,'Beryl','28th','OmniBank'),
             (13,'Beryl','40th','OmniBank'),
             (14,'Beryl','65th','OmniBank'),
             (15,'Beryl','72nd','OmniBank'),
             (16,'Bleak','14th','OmniBank'),
             (17,'Buzzard','13th','OmniBank'),
             (18,'Cedar','1st','OmniBank'),
             (19,'Cedar','52nd','OmniBank'),
             (20,'Cedar','80th','OmniBank'),
             (21,'Chagrin','23rd','OmniBank'),
             (22,'Chagrin','39th','OmniBank'),
             (23,'Cobalt','46th','OmniBank'),
             (24,'Cobalt','81st','OmniBank'),
             (25,'Cobalt','88th','OmniBank'),
             (26,'Cormorant','93rd','OmniBank'),
             (27,'Despair','1st','OmniBank'),
             (28,'Despair','75th','OmniBank'),
             (29,'Dogwood','4th','OmniBank'),
             (30,'Duck','37th','OmniBank'),
             (31,'Duck','77th','OmniBank'),
             (32,'Eagle','64th','OmniBank'),
             (33,'Eagle','89th','OmniBank'),
             (34,'Elm','98th','OmniBank'),
             (35,'Emerald','19th','OmniBank'),
             (36,'Emerald','90th','OmniBank'),
             (37,'Emerald','99th','OmniBank'),
             (38,'Ennui','20th','OmniBank'),
             (39,'Ennui','78th','OmniBank'),
             (40,'Fear','15th','OmniBank'),
             (41,'Ferret','32nd','OmniBank'),
             (42,'Ferret','90th','OmniBank'),
             (43,'Fir','2nd','OmniBank'),
             (44,'Flint','37th','OmniBank'),
             (45,'Flint','45th','OmniBank'),
             (46,'Flint','47th','OmniBank'),
             (47,'Flint','5th','OmniBank'),
             (48,'Gloom','34th','OmniBank'),
             (49,'Gloom','71st','OmniBank'),
             (50,'Gloom','89th','OmniBank'),
             (51,'Gloom','90th','OmniBank'),
             (52,'Haddock','46th','OmniBank'),
             (53,'Haddock','52nd','OmniBank'),
             (54,'Haddock','67th','OmniBank'),
             (55,'Haddock','74th','OmniBank'),
             (56,'Haddock','88th','OmniBank'),
             (57,'Hessite','39th','OmniBank'),
             (58,'Hessite','76th','OmniBank'),
             (59,'Holly','96th','OmniBank'),
             (60,'Horror','49th','OmniBank'),
             (61,'Horror','59th','OmniBank'),
             (62,'Ire','31st','OmniBank'),
             (63,'Ire','42nd','OmniBank'),
             (64,'Ire','53rd','OmniBank'),
             (65,'Ire','97th','OmniBank'),
             (66,'Ivory','5th','OmniBank'),
             (67,'Ivory','71st','OmniBank'),
             (68,'Ivy','70th','OmniBank'),
             (69,'Ivy','79th','OmniBank'),
             (70,'Ivy','NCL','OmniBank'),
             (71,'Jackal','43rd','OmniBank'),
             (72,'Jaded','25th','OmniBank'),
             (73,'Jaded','48th','OmniBank'),
             (74,'Jaded','71st','OmniBank'),
             (75,'Juniper','16th','OmniBank'),
             (76,'Juniper','20th','OmniBank'),
             (77,'Juniper','98th','OmniBank'),
             (78,'Knotweed','15th','OmniBank'),
             (79,'Knotweed','29th','OmniBank'),
             (80,'Kraken','13th','OmniBank'),
             (81,'Kraken','18th','OmniBank'),
             (82,'Kraken','34th','OmniBank'),
             (83,'Kraken','3rd','OmniBank'),
             (84,'Kraken','45th','OmniBank'),
             (85,'Kraken','48th','OmniBank'),
             (86,'Kraken','7th','OmniBank'),
             (87,'Kyanite','40th','OmniBank'),
             (88,'Kyanite','6th','OmniBank'),
             (89,'Larch','33rd','OmniBank'),
             (90,'Larch','7th','OmniBank'),
             (91,'Larch','91st','OmniBank'),
             (92,'Lead','11th','OmniBank'),
             (93,'Lead','21st','OmniBank'),
             (94,'Lead','88th','OmniBank'),
             (95,'Lion','80th','OmniBank'),
             (96,'Lonely','93rd','OmniBank'),
             (97,'Malachite','11th','OmniBank'),
             (98,'Malachite','32nd','OmniBank'),
             (99,'Malachite','87th','OmniBank'),
             (100,'Malaise','36th','OmniBank'),
             (101,'Malaise','4th','OmniBank'),
             (102,'Malaise','50th','OmniBank'),
             (103,'Maple','34th','OmniBank'),
             (104,'Maple','84th','OmniBank'),
             (105,'Maple','85th','OmniBank'),
             (106,'Mongoose','78th','OmniBank'),
             (107,'Mongoose','79th','OmniBank'),
             (108,'Mongoose','91st','OmniBank'),
             (109,'Nervous','10th','OmniBank'),
             (110,'Nettle','37th','OmniBank'),
             (111,'Nettle','67th','OmniBank'),
             (112,'Nickel','93rd','OmniBank'),
             (113,'Obsidian','36th','OmniBank'),
             (114,'Obsidian','79th','OmniBank'),
             (115,'Octopus','27th','OmniBank'),
             (116,'Octopus','71st','OmniBank'),
             (117,'Octopus','77th','OmniBank'),
             (118,'Olive','99th','OmniBank'),
             (119,'Olive','9th','OmniBank'),
             (120,'Oppression','2nd','OmniBank'),
             (121,'Oppression','89th','OmniBank'),
             (122,'Pessimism','19th','OmniBank'),
             (123,'Pessimism','44th','OmniBank'),
             (124,'Pessimism','87th','OmniBank'),
             (125,'Pilchard','44th','OmniBank'),
             (126,'Pilchard','60th','OmniBank'),
             (127,'Pine','42nd','OmniBank'),
             (128,'Pine','44th','OmniBank'),
             (129,'Pyrites','11th','OmniBank'),
             (130,'Pyrites','24th','OmniBank'),
             (131,'Pyrites','90th','OmniBank'),
             (132,'Quail','10th','OmniBank'),
             (133,'Quail','12th','OmniBank'),
             (134,'Quail','18th','OmniBank'),
             (135,'Quail','26th','OmniBank'),
             (136,'Quail','36th','OmniBank'),
             (137,'Quail','41st','OmniBank'),
             (138,'Quail','58th','OmniBank'),
             (139,'Quail','74th','OmniBank'),
             (140,'Qualms','28th','OmniBank'),
             (141,'Qualms','57th','OmniBank'),
             (142,'Qualms','75th','OmniBank'),
             (143,'Quartz','75th','OmniBank'),
             (144,'Quince','48th','OmniBank'),
             (145,'Quince','61st','OmniBank'),
             (146,'Ragweed','31st','OmniBank'),
             (147,'Ragweed','56th','OmniBank'),
             (148,'Raven','11th','OmniBank'),
             (149,'Raven','15th','OmniBank'),
             (150,'Raven','79th','OmniBank'),
             (151,'Raven','98th','OmniBank'),
             (152,'Regret','70th','OmniBank'),
             (153,'Ruby','18th','OmniBank'),
             (154,'Ruby','45th','OmniBank'),
             (155,'Sorrow','48th','OmniBank'),
             (156,'Sorrow','9th','OmniBank'),
             (157,'Squid','10th','OmniBank'),
             (158,'Squid','24th','OmniBank'),
             (159,'Steel','31st','OmniBank'),
             (160,'Steel','64th','OmniBank'),
             (161,'Steel','7th','OmniBank'),
             (162,'Sycamore','16th','OmniBank'),
             (163,'Tapir','11th','OmniBank'),
             (164,'Tapir','41st','OmniBank'),
             (165,'Tapir','NCL','OmniBank'),
             (166,'Teasel','60th','OmniBank'),
             (167,'Teasel','66th','OmniBank'),
             (168,'Teasel','92nd','OmniBank'),
             (169,'Torment','23rd','OmniBank'),
             (170,'Torment','28th','OmniBank'),
             (171,'Torment','31st','OmniBank'),
             (172,'Umbrella','20th','OmniBank'),
             (173,'Umbrella','80th','OmniBank'),
             (174,'Unctuous','23rd','OmniBank'),
             (175,'Unctuous','43rd','OmniBank'),
             (176,'Unicorn','11th','OmniBank'),
             (177,'Unicorn','78th','OmniBank'),
             (178,'Uranium','1st','OmniBank'),
             (179,'Uranium','48th','OmniBank'),
             (180,'Uranium','93rd','OmniBank'),
             (181,'Uranium','97th','OmniBank'),
             (182,'Vauxite','68th','OmniBank'),
             (183,'Vauxite','91st','OmniBank'),
             (184,'Vexation','24th','OmniBank'),
             (185,'Vulture','43rd','OmniBank'),
             (186,'Vulture','82nd','OmniBank'),
             (187,'WCL','77th','OmniBank'),
             (188,'Willow','84th','OmniBank'),
             (189,'Woe','44th','OmniBank'),
             (190,'Woe','85th','OmniBank'),
             (191,'Yak','45th','OmniBank'),
             (192,'Yak','82nd','OmniBank'),
             (193,'Yak','94th','OmniBank'),
             (194,'Yearning','75th','OmniBank'),
             (195,'Yearning','93rd','OmniBank'),
             (196,'Yew','4th','OmniBank'),
             (197,'Zebra','61st','OmniBank'),
             (198,'Zelkova','23rd','OmniBank'),
             (199,'Zelkova','73rd','OmniBank'),
             (200,'Zinc','74th','OmniBank')
        ]),
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
        ("INSERT OR IGNORE INTO `columns` (ID, Name, Coordinate) VALUES (?, ?, ?)", [
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
        ("INSERT OR IGNORE INTO css_profiles (profile_name) VALUES (?)", [("Default",)]),
        ("INSERT OR IGNORE INTO custom_css (profile_name, element, value) VALUES (?, ?, ?)", [
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
        ("INSERT OR IGNORE INTO guilds (ID, Name, Column, Row, next_update) VALUES (?, ?, ?, ?, ?)", [
            (1,'Allurists Guild 1','NA','NA',''),
            (2,'Allurists Guild 2','NA','NA',''),
            (3,'Allurists Guild 3','NA','NA',''),
            (4,'Empaths Guild 1','NA','NA',''),
            (5,'Empaths Guild 2','NA','NA',''),
            (6,'Empaths Guild 3','NA','NA',''),
            (7,'Immolators Guild 1','NA','NA',''),
            (8,'Immolators Guild 2','NA','NA',''),
            (9,'Immolators Guild 3','NA','NA',''),
            (10,'Thieves Guild 1','NA','NA',''),
            (11,'Thieves Guild 2','NA','NA',''),
            (12,'Thieves Guild 3','NA','NA',''),
            (13,'Travellers Guild 1','NA','NA',''),
            (14,'Travellers Guild 2','NA','NA',''),
            (15,'Travellers Guild 3','NA','NA',''),
            (16,'Peacekeepers Mission 1','Emerald','67th',''),
            (17,'Peacekeepers Mission 2','Unicorn','33rd',''),
            (18,'Peacekeepers Mission 3','Emerald','33rd','')
        ]),
        ("INSERT OR IGNORE INTO placesofinterest (ID, Name, Column, Row) VALUES (?, ?, ?, ?)", [
            (1,'Battle Arena','Zelkova','52nd'),
            (2,'Hall of Binding','Vervain','40th'),
            (3,'Hall of Severance','Walrus','40th'),
            (4,'Graveyard','Larch','50th'),
            (5,'Cloister of Secrets','Gloom','1st'),
            (6,'Eternal Aubade of Mystical Treasures','Zelkova','47th'),
            (7,'Kindred Hospital','Woe','13th')
        ]),
        ("INSERT OR IGNORE INTO powers (power_id, name, guild, cost, quest_info, skill_info) VALUES (?, ?, ?, ?, ?, ?)", [
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
        ("INSERT OR IGNORE INTO `rows` (ID, Name, Coordinate) VALUES (?, ?, ?)", [
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
        ("INSERT OR IGNORE INTO shop_items (id, shop_name, item_name, base_price, charisma_level_1, charisma_level_2, charisma_level_3) VALUES (?, ?, ?, ?, ?, ?, ?)", [
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
        ("INSERT OR IGNORE INTO shops (ID, Name, Column, Row, next_update) VALUES (?, ?, ?, ?, ?)", [
            (1,'Ace Porn','NA','NA',''),
            (2,'Checkers Porn Shop','NA','NA',''),
            (3,'Dark Desires','NA','NA',''),
            (4,'Discount Magic','NA','NA',''),
            (5,'Discount Potions','NA','NA',''),
            (6,'Discount Scrolls','NA','NA',''),
            (7,'Herman''s Scrolls','NA','NA',''),
            (8,'Interesting Times','NA','NA',''),
            (9,'McPotions','NA','NA',''),
            (10,'Paper and Scrolls','NA','NA',''),
            (11,'Potable Potions','NA','NA',''),
            (12,'Potion Distillery','NA','NA',''),
            (13,'Potionworks','NA','NA',''),
            (14,'Reversi Porn','NA','NA',''),
            (15,'Scrollmania','NA','NA',''),
            (16,'Scrolls ''n'' Stuff','NA','NA',''),
            (17,'Scrolls R Us','NA','NA',''),
            (18,'Scrollworks','NA','NA',''),
            (19,'Silver Apothecary','NA','NA',''),
            (20,'Sparks','NA','NA',''),
            (21,'Spinners Porn','NA','NA',''),
            (22,'The Magic Box','NA','NA',''),
            (23,'The Potion Shoppe','NA','NA',''),
            (24,'White Light','NA','NA',''),
            (25,'Ye Olde Scrolles','NA','NA','')
        ]),
        ("INSERT OR IGNORE INTO taverns (ID, Column, Row, Name) VALUES (?, ?, ?, ?)", [
            (1,'Gum','33rd','Abbot''s Tavern'),
            (2,'Knotweed','11th','Archer''s Tavern'),
            (3,'Torment','16th','Baker''s Tavern'),
            (4,'Fir','13th','Balmer''s Tavern'),
            (5,'Nettle','3rd','Barker''s Tavern'),
            (6,'Duck','7th','Bloodwood Canopy Cafe'),
            (7,'Haddock','64th','Bowyer''s Tavern'),
            (8,'Qualms','61st','Butler''s Tavern'),
            (9,'Yew','78th','Carter''s Tavern'),
            (10,'Raven','71st','Chandler''s Tavern'),
            (11,'Bleak','64th','Club Xendom'),
            (12,'Pilchard','48th','Draper''s Tavern'),
            (13,'Yak','90th','Falconer''s Tavern'),
            (14,'Ruby','20th','Fiddler''s Tavern'),
            (15,'Ferret','84th','Fisherman''s Tavern'),
            (16,'Pine','68th','Five French Hens'),
            (17,'Steel','26th','Freeman''s Tavern'),
            (18,'Gibbon','98th','Harper''s Tavern'),
            (19,'Ire','63rd','Hawker''s Tavern'),
            (20,'Hessite','55th','Hell''s Angels Clubhouse'),
            (21,'Fir','72nd','Hunter''s Tavern'),
            (22,'Lion','1st','Leacher''s Tavern'),
            (23,'Malachite','76th','Lovers at Dawn Inn'),
            (24,'Ragweed','78th','Marbler''s Tavern'),
            (25,'Ferret','44th','Miller''s Tavern'),
            (26,'Steel','3rd','Oyler''s Tavern'),
            (27,'Diamond','92nd','Painter''s Tavern'),
            (28,'Walrus','83rd','Peace De Résistance'),
            (29,'Fear','34th','Pub Forty-Two'),
            (30,'Qualms','61st','Ratskeller'),
            (31,'Beryl','98th','Rider''s Tavern'),
            (32,'Qualms','5th','Rogue''s Tavern'),
            (33,'Eagle','67th','Shooter''s Tavern'),
            (34,'Bleak','NCL','Smuggler''s Cove'),
            (35,'Anguish','98th','Ten Turtle Doves'),
            (36,'Oppression','45th','The Angel''s Wing'),
            (37,'Oppression','70th','The Axeman and Guillotine'),
            (38,'Ivory','99th','The Blinking Pixie'),
            (39,'Pessimism','37th','The Book and Beggar'),
            (40,'Malachite','70th','The Booze Hall'),
            (41,'Pyrites','41st','The Brain and Hatchling'),
            (42,'Lonely','87th','The Brimming Brew'),
            (43,'Qualms','43rd','The Broken Lover'),
            (44,'Ruby','90th','The Burning Brand'),
            (45,'Walrus','68th','The Cart and Castle'),
            (46,'Lion','1st','The Celtic Moonligh'),
            (47,'Beech','19th','The Clam and Champion'),
            (48,'Nightingale','32nd','The Cosy Walrus'),
            (49,'Sorrow','70th','The Crossed Swords Tavern'),
            (50,'Gum','10th','The Crouching Tiger'),
            (51,'Killjoy','46th','The Crow''s Nest Tavern'),
            (52,'Pine','51st','The Dead of Night'),
            (53,'Lonely','78th','The Demon''s Heart'),
            (54,'Ragweed','6th','The Dog House'),
            (55,'Zinc','94th','The Drunk Cup'),
            (56,'Yak','30th','The Ferryman''s Arms'),
            (57,'Nervous','2nd','The Flirty Angel'),
            (58,'Sorrow','91st','The Freudian Slip'),
            (59,'Walrus','62nd','The Ghastly Flabber'),
            (60,'Lion','95th','The Golden Partridge'),
            (61,'Zebra','50th','The Guardian Outpost'),
            (62,'Obsidian','54th','The Gunny''s Shack'),
            (63,'Vexation','2nd','The Hearth and Sabre'),
            (64,'Dogwood','54th','The Kestrel'),
            (65,'Mongoose','15th','The Last Days'),
            (66,'Unicorn','92nd','The Lazy Sunflower'),
            (67,'Nervous','42nd','The Lightbringer'),
            (68,'Kyanite','19th','The Lounge'),
            (69,'Yearning','48th','The Marsupial'),
            (70,'Hessite','97th','The McAllister Tavern'),
            (71,'Dogwood','78th','The Moon over Orion'),
            (72,'Gibbon','44th','The Ox and Bow'),
            (73,'Jackal','53rd','The Palm and Parson'),
            (74,'Quail','85th','The Poltroon'),
            (75,'Ruby','21st','The Round Room'),
            (76,'Diamond','1st','The Scupper and Forage'),
            (77,'Pine','91st','The Shattered Platter'),
            (78,'Nickel','57th','The Shining Devil'),
            (79,'Alder','57th','The Sign of the Times'),
            (80,'Ennui','80th','The Stick and Stag'),
            (81,'Oppression','70th','The Stick in the Mud'),
            (82,'Malaise','87th','The Sun'),
            (83,'Eagle','34th','The Sunken Sofa'),
            (84,'Turquoise','71st','The Swords at Dawn'),
            (85,'Elm','93rd','The Teapot and Toxin'),
            (86,'Mongoose','92nd','The Thief of Hearts'),
            (87,'Despair','38th','The Thorn''s Pride'),
            (88,'Zebra','36th','The Two Sisters'),
            (89,'Nettle','86th','The Wart and Whisk'),
            (90,'Sycamore','89th','The Whirling Dervish'),
            (91,'Vulture','11th','The Wild Hunt'),
            (92,'Steel','23rd','Treehouse'),
            (93,'Yew','5th','Vagabond''s Tavern'),
            (94,'Anguish','68th','Xendom Tavern'),
            (95,'Pyrites','70th','Ye Olde Gallows Ale House')
        ]),
        ("INSERT OR IGNORE INTO transits (ID, Column, Row, Name) VALUES (?, ?, ?, ?)", [
            (1,'Mongoose','25th','Calliope'),
            (2,'Zelkova','25th','Clio'),
            (3,'Malachite','25th','Erato'),
            (4,'Mongoose','50th','Euterpe'),
            (5,'Zelkova','50th','Melpomene'),
            (6,'Malachite','50th','Polyhymnia'),
            (7,'Mongoose','75th','Terpsichore'),
            (8,'Zelkova','75th','Thalia'),
            (9,'Malachite','75th','Urania')
        ]),
        ("INSERT OR IGNORE INTO userbuildings (ID, Name, Column, Row) VALUES (?, ?, ?, ?)", [
            (1, 'Ace''s House of Dumont', 'Cedar', '99th'),
            (2, 'Alatáriël Maenor', 'Diamond', '50th'),
            (3, 'Alpha Dragon''s and Lyric''s House of Dragon and Flame', 'Amethyst', '90th'),
            (4, 'AmadisdeGaula''s Stellaburgi', 'Wulfenite', '38th'),
            (5, 'Andre''s Crypt', 'Ferret', '10th'),
            (6, 'Annabelle''s Paradise', 'Emerald', '85th'),
            (7, 'Anthony''s Castle Pacherontis', 'Walrus', '39th'),
            (8, 'Anthony''s Gero Claw', 'Vulture', '39th'),
            (9, 'Anthony''s Training Grounds', 'Vulture', '35th'),
            (10, 'Aphaythean Vineyards', 'Willow', '13th'),
            (11, 'Archangel''s Castle', 'Beech', '4th'),
            (12, 'Avant''s Garden', 'Amethyst', '68th'),
            (13, 'BaShalor''s Rose Garden', 'Cobalt', '41st'),
            (14, 'Bitercat''s mews', 'Lion', '42nd'),
            (15, 'Black dragonet''s mansion', 'Oppression', '80th'),
            (16, 'Blutengel''s Temple of Blood', 'Fear', '13th'),
            (17, 'Café Damari', 'Zelkova', '68th'),
            (18, 'Cair Paravel', 'Lion', '27th'),
            (19, 'Capadocian Castle', 'Larch', '49th'),
            (20, 'Carnal Desires', 'Ivy', '66th'),
            (21, 'Castle of Shadows', 'Turquoise', '86th'),
            (22, 'Castle RavenesQue', 'Raven', 'NCL'),
            (23, 'ChaosRaven''s Dimensional Tower', 'Killjoy', '23rd'),
            (24, 'CHASS''s forever-blues hall', 'Torment', '75th'),
            (25, 'CrimsonClover''s Hideaway', 'Diamond', '85th'),
            (26, 'CrowsSong''s Blackbird Towers', 'Wulfenite', '3rd'),
            (27, 'D''dary Manor', 'Aardvark', '1st'),
            (28, 'Daphne''s Dungeons', 'Malachite', '64th'),
            (29, 'DarkestDesire''s Chambers', 'Despair', '56th'),
            (30, 'Darkwolf''s and liquid-vamp''s Country Cottage', 'Wulfenite', '69th'),
            (31, 'Deaths embrace''s Shadow Keep', 'Holly', '81st'),
            (32, 'Devil Miyu''s Abeir-Toril', 'Fear', '2nd'),
            (33, 'Devil Miyu''s Edge of Reason', 'Fear', 'NCL'),
            (34, 'Devil Miyu''s Lair', 'Fear', '1st'),
            (35, 'Dreamcatcher Haven', 'Torment', '2nd'),
            (36, 'Elijah''s Hall of the Lost', 'Zinc', '99th'),
            (37, 'ElishaDraken''s Sanguine Ankh', 'Nightingale', '59th'),
            (38, 'Epineux Manoir', 'Olive', '70th'),
            (39, 'Espy''s Jaded Sorrows', 'Jaded', '69th'),
            (40, 'Freedom Trade Alliance', 'Amethyst', '46th'),
            (41, 'Gypsychild''s Caravan', 'Torment', '69th'),
            (42, 'Halls of Shadow Court', 'Horror', '99th'),
            (43, 'Hells Gate''s Castle of Destruction', 'Lonely', '45th'),
            (44, 'Hesu''s Place', 'Raven', '24th'),
            (45, 'Hexenkessel', 'Jackal', '83rd'),
            (47, 'Ildiko''s and Brom''s Insanity', 'Killjoy', '53rd'),
            (48, 'Jacomo Varis'' Shadow Manor', 'Raven', '96th'),
            (49, 'Jaxi''s and Speedy''s Cave', 'Raven', '23rd'),
            (50, 'Julia''s Villa', 'Gloom', '76th'),
            (51, 'King Lestat''s Le Paradis Caché', 'Cobalt', '90th'),
            (52, 'La Cucina', 'Diamond', '28th'),
            (53, 'Lady Ophy''s Bougainvillea Mansion', 'Jaded', '84th'),
            (54, 'LadyFae''s and nitenurse''s Solas Gealaí Caisleán', 'Raven', '76th'),
            (55, 'Lasc Talon''s Estate', 'Willow', '42nd'),
            (56, 'Lass'' Lair', 'Vervain', '1st'),
            (57, 'Liski''s Shadow Phial', 'Gloom', '99th'),
            (58, 'Lord Galamushi''s Enchanted Mansion', 'Anguish', '52nd'),
            (59, 'Louvain''s Sanctuary', 'Gibbon', '21st'),
            (60, 'Majica''s Playground', 'Willow', '50th'),
            (61, 'Mandruleanu Manor', 'Diamond', '86th'),
            (62, 'Mansion of Malice', 'Horror', '69th'),
            (63, 'Marlena''s Wishing Well', 'Fear', '56th'),
            (64, 'Moirai''s Gate to the Church of Blood', 'Horror', '13th'),
            (65, 'Moondreamer''s Darkest Desire''s Lighthouse', 'Fear', '9th'),
            (66, 'Moonlight Gardens', 'Turquoise', '87th'),
            (67, 'Ms Delgado''s Manor', 'Sorrow', '69th'),
            (68, 'MyMotherInLaw''s Home for Wayward Ghouls', 'Amethyst', '69th'),
            (69, 'Narcisssa''s Vineyard', 'Aardvark', '60th'),
            (70, 'Nemesis'' Asyl', 'Zinc', '85th'),
            (71, 'NightWatch Headquarters', 'Larch', '51st'),
            (72, 'Obsidian''s Arboretum', 'Obsidian', '88th'),
            (73, 'Obsidian''s Castle of Warwick', 'Obsidian', 'NCL'),
            (74, 'Obsidian''s Château de la Lumière', 'Obsidian', '66th'),
            (75, 'Obsidian''s château noir', 'Obsidian', '99th'),
            (76, 'Obsidian''s Hall of Shifting Realms', 'Obsidian', '15th'),
            (77, 'Obsidian''s Penthouse', 'Obsidian', '29th'),
            (78, 'Obsidian''s Silver Towers', 'Obsidian', '51st'),
            (79, 'Obsidian''s Tranquility', 'Obsidian', '80th'),
            (80, 'Obsidian''s, Phoenixxe''s and Em''s Heaven''s Gate', 'Obsidian', '45th'),
            (81, 'Occamrazor''s House of Ears', 'Yew', '30th'),
            (82, 'Ordo Dracul Sanctum', 'Nightingale', '77th'),
            (83, 'Orgasmerilla''s Warehouse', 'Zinc', '80th'),
            (84, 'Pace Family Ranch', 'Fir', '69th'),
            (85, 'Palazzo Lucius', 'Zebra', '27th'),
            (86, 'Pandrora and CBK''s Chamber of Horrors', 'Torment', '95th'),
            (87, 'RemipunX''s Sacred Yew', 'Cobalt', '42nd'),
            (88, 'Renovate''s grove', 'Umbrella', '71st'),
            (89, 'Saki''s Fondest Wish', 'Nightingale', '17th'),
            (90, 'Samantha Dawn''s Salacious Sojourn', 'Anguish', '53rd'),
            (91, 'Sanctuary Hotel', 'Kraken', '27th'),
            (92, 'Sartori''s Domicile', 'Elm', '1st'),
            (93, 'SCORPIOUS1''s Tower of Truth', 'Yearning', '58th'),
            (94, 'Setitevampyr''s temple', 'Raven', '50th'),
            (95, 'Shaarinya`s Sanguine Sanctuary', 'Raven', '77th'),
            (96, 'Shadow bat''s Sanctorium', 'Cobalt', '76th'),
            (97, 'SIE Compound', 'Raven', '13th'),
            (98, 'Sitrence''s Lab', 'Ferret', '3rd'),
            (99, 'Solanea''s Family Home', 'Ruby', '56th'),
            (100, 'The Angelarium', 'Zinc', 'NCL'),
            (101, 'St. John Bathhouse', 'Sycamore', '76th'),
            (102, 'Starreagle''s Paradise Lair', 'Beryl', '24th'),
            (103, 'Steele Industries', 'Umbrella', '44th'),
            (104, 'Stormy jayne''s web', 'Nickel', '99th'),
            (105, 'Talon Castle', 'Willow', '35th'),
            (106, 'tejas_dragon''s Lair', 'Zelkova', '69th'),
            (107, 'The Ailios Asylum', 'Amethyst', '36th'),
            (108, 'The Belly of the Whale', 'Amethyst', '2nd'),
            (109, 'The Calignite', 'Eagle', '16th'),
            (110, 'The COVE', 'Knowteed', '51st'),
            (111, 'The Dragons Lair Club', 'Vervain', '39th'),
            (112, 'The Eternal Spiral', 'Anguish', '69th'),
            (113, 'The goatsucker''s lair', 'Yak', '13th'),
            (114, 'The Halls of Heorot', 'Jaded', '75th'),
            (115, 'The House of Night', 'Walrus', '38th'),
            (116, 'The Inner Circle Manor', 'Diamond', '26th'),
            (117, 'The Ivory Tower', 'Zelkova', '76th'),
            (118, 'The Ixora Estate', 'Lead', '48th'),
            (119, 'The Kyoto Club', 'Lion', '22nd'),
            (120, 'The Lokason Myrkrasetur', 'Wulfenite', '40th'),
            (121, 'The Path of Enlightenment Castle', 'Willow', '80th'),
            (122, 'The RavenBlack Bite', 'Oppression', '40th'),
            (123, 'The Reynolds'' Estate', 'Beryl', '23rd'),
            (124, 'The River Passage', 'Yew', '33rd'),
            (125, 'The Sakura Garden', 'Nickel', '77th'),
            (126, 'The Sanctum of Vermathrax-rex and Bellina', 'Vexation', '99th'),
            (127, 'The Sanguinarium', 'Fear', '4th'),
            (128, 'The Scythe''s Negotiation Offices', 'Vauxite', '88th'),
            (129, 'The Sepulchre of Shadows', 'Ennui', '1st'),
            (130, 'The Tower of Thorns', 'Pilchard', '70th'),
            (131, 'The Towers of the Crossed Swords', 'Torment', '66th'),
            (132, 'The White House', 'Nervous', '75th'),
            (133, 'University of Vampiric Enlightenment', 'Yak', '80th'),
            (134, 'Virgo''s obsidian waygate', 'Obsidian', '2nd'),
            (135, 'Vulture''s Pagoda', 'Vulture', '50th'),
            (136, 'Wilde Sanctuary', 'Willow', '51st'),
            (137, 'Wilde Wolfe Estate', 'Vervain', '50th'),
            (138, 'Willhelm''s Warrior House', 'Horror', '53rd'),
            (139, 'Willow Lake Manse', 'Willow', '99th'),
            (140, 'Willow Woods'' & The Ent Moot', 'Willow', '54th'),
            (141, 'Wolfshadow''s and Crazy''s RBC Casino', 'Lead', '72nd'),
            (142, 'Wyndcryer''s TygerNight''s and Bambi''s Lair', 'Unicorn', '77th'),
            (143, 'Wyvernhall', 'Ivy', '38th'),
            (144, 'X', 'Emerald', 'NCL'),
            (145, 'Requiem of Hades', 'Walrus', '41st')
        ]),
        ("INSERT OR IGNORE INTO discord_servers (id, name, invite_link) VALUES (?, ?, ?)", [
            (1, "Ab Antiquo Headquarters", "https://discord.gg/AhPEzkJyA4"),
            (2, "Hellfire Club", "https://discord.gg/qZCbbKEt3z"),
            (3, "RB Improvement Group", "https://discord.gg/8ent8jn54u"),
            (4, "RBCH", "https://discord.gg/ktdG9FZ"),
            (5, "Raven Black: Boroughs and Barrios", "https://discord.gg/RTSXJ5tC4d"),
            (6, "RavenBlack Community Center", "https://discord.gg/SVMmGcvNCV"),
            (7, "The Moon over Orion", "https://discord.gg/EArPr7vqHC"),
            (8, "The Ravenblack Historical Society", "https://discord.gg/zqPXpw8sMw"),
            (9, "rêverie", "https://discord.gg/jAVHpGvgCf")
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
                    cursor.execute("""
                        INSERT INTO guilds (ID, Name, Column, Row, next_update)
                        SELECT ID, Name, Column, Row, next_update FROM guilds_old
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
                    cursor.execute("""
                        INSERT INTO shops (ID, Name, Column, Row, next_update)
                        SELECT ID, Name, Column, Row, next_update FROM shops_old
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
    Load map-related data from the SQLite database efficiently.

    Also loads the last active character and their most recent destination.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Coordinate mappings
            cursor.execute("SELECT `Name`, `Coordinate` FROM `columns`")
            columns = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT `Name`, `Coordinate` FROM `rows`")
            rows = {row[0]: row[1] for row in cursor.fetchall()}

            def to_coords(col_name: str, row_name: str) -> tuple[int, int]:
                if col_name not in columns or row_name not in rows:
                    logging.warning(f"Could not resolve coordinates for {col_name} & {row_name}")
                    return None, None

                col = columns[col_name] + 1
                row = rows[row_name] + 1
                return col, row

            # Banks
            banks_coordinates = {}
            cursor.execute("SELECT `Column`, `Row`, Name, ID FROM banks")
            for col_name, row_name, _, _ in cursor.fetchall():
                banks_coordinates[f"{col_name} & {row_name}"] = (col_name, row_name)

            # Other coordinate-based structures
            taverns_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM taverns")
            }
            transits_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM transits")
            }
            user_buildings_coordinates = {
                name: to_coords(col, row)
                for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM userbuildings")
            }

            # Color mappings
            color_mappings = {}
            for type_, color in cursor.execute("SELECT Type, Color FROM color_mappings"):
                try:
                    qcolor = PySide6.QtGui.QColor(color)
                    if not qcolor.isValid():
                        logging.warning(f"Invalid color for type '{type_}': '{color}'")
                    color_mappings[type_] = qcolor
                except Exception as e:
                    logging.error(f"Failed to load QColor for '{type_}': {e}")
                    color_mappings[type_] = PySide6.QtGui.QColor("#000000")

            # Shops and Guilds
            shops_coordinates = {}
            for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM shops"):
                if col != "NA" and row != "NA":
                    shops_coordinates[name] = to_coords(col, row)
            guilds_coordinates = {}
            for name, col, row in cursor.execute("SELECT Name, `Column`, `Row` FROM guilds"):
                if col != "NA" and row != "NA":
                    guilds_coordinates[name] = to_coords(col, row)

            # Points of Interest
            places_of_interest_coordinates = {}
            cursor.execute("SELECT Name, `Column`, `Row` FROM placesofinterest")
            rows_data = cursor.fetchall()

            logging.debug("Resolved POI coordinates:")
            for name, col, row in rows_data:
                coords = to_coords(col, row)
                if coords == (None, None):
                    logging.warning(f"Skipping POI {name} due to unresolved coordinates: {col}, {row}")
                else:
                    places_of_interest_coordinates[name] = coords
                    logging.debug(f"{name}: {coords}")

            # Load settings
            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'keybind_config'")
            row = cursor.fetchone()
            keybind_config = int(row[0]) if row else 1

            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'css_profile'")
            row = cursor.fetchone()
            current_css_profile = row[0] if row else "Default"

            # Load last active character
            selected_character = None
            last_destination = None
            cursor.execute("SELECT character_id FROM last_active_character LIMIT 1")
            row = cursor.fetchone()
            character_id = row[0] if row else None

            if character_id:
                cursor.execute("SELECT id, name, password FROM characters WHERE id = ?", (character_id,))
                char_row = cursor.fetchone()
                if char_row:
                    selected_character = {
                        "id": char_row[0],
                        "name": char_row[1],
                        "password": char_row[2]
                    }

                    # Load last destination for this character
                    cursor.execute(
                        "SELECT col, row FROM destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 1",
                        (character_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        last_destination = (row[0], row[1])

            logging.debug("Loaded data from database successfully")
            return (
                columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates,
                user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates,
                places_of_interest_coordinates, keybind_config, current_css_profile,
                selected_character, last_destination
            )

    except sqlite3.Error as e:
        logging.error(f"Failed to load data from database {DB_PATH}: {e}")
        raise


# Load data at startup
try:
    (
        columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates,
        user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates,
        places_of_interest_coordinates, keybind_config, current_css_profile,
        selected_character, last_destination
    ) = load_data()
except sqlite3.Error:
    logging.critical("Database load failed. Using fallback empty data.")
    columns = rows = taverns_coordinates = transits_coordinates = user_buildings_coordinates = \
        shops_coordinates = guilds_coordinates = places_of_interest_coordinates = {}
    banks_coordinates = {}
    color_mappings = {'default': PySide6.QtGui.QColor('#000000')}  # Minimal fallback
    keybind_config = 1
    current_css_profile = "Default"
    selected_character = None
    last_destination = None
