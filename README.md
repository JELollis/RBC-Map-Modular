# RBC Community Map Application

This project is an attempt to create an interactive map coded in Python for use with **Vampires! The Dark Alleyway**, located at [RavenBlack City](https://quiz.ravenblack.net/blood.pl).

![Main Application](Screenshots/Main%20Application.png "Main Application")

---

## Features

### 1) Minimap Features
- **Track Current Location**: Automatically track the current location based on the game’s right frame.
- **Nearest Points of Interest**:
  - **Red Line**: Drawn to the nearest transit station.
  - **Blue Line**: Drawn to the nearest bank.
  - **Orange Line**: Drawn to the nearest pub.
- **Zoom Levels**: Display a 3x3 (default), 5x5, 7x7, or 9x9 grid around the player’s position.
- **Manual Centering**:
  - **Click to Center**: Click on a square in the minimap grid to center it.
  - **Dropdown Selection**: Select a location using the dropdowns below the map and click "Go" to center the minimap on that location.
- **Destination Tracking**:
  - **Set Destination**: Click "Set Destination" to mark the destination on the map.
  - **Green Line**: Paints a green line on the map to the destination.
- **Customizable Themes**: Personalize the minimap and interface themes for a more customized experience.

![Minimap Theme](Screenshots/Minimap%20Theme.png "Minimap Theme")

---

### 2) Character Management
- **Quick Switch**: Store login credentials to quickly and easily switch between characters.
- **Local Data Storage**:
  - User data is securely stored in a local SQLite database.
  - No user data is stored on external servers.

![New User Dialog](Screenshots/New%20User%20Dialog.png "New User Dialog")

---

### 3) Keybinding Support (NEW in v0.10.3)
- **WASD and Arrow Key Movement**: Toggle between **WASD** and **Arrow Key** navigation.
- **Persistent Settings**: Keybinding configuration is stored in SQLite for consistency across sessions.

---

### 4) Shopping List Tool
- Create and manage shopping lists for in-game items.
- Automatically calculate total costs for required items.
- View available coins and plan purchases accordingly.

![Shopping List Tool](Screenshots/Shopping%20List%20Tool.png "Shopping List Tool")

---

### 5) CSS Customization Tool (Updated in v0.10.3)
- **Modify Interface Styling**: Customize the UI with CSS modifications.
- **New Features**: **Box Shadow, Font Selection, and Background Image Support**.
- **Live Preview**: See CSS changes in real-time before applying them.
![CSS Customization Tool](Screenshots/CSS%20Customization%20Dialog.png "CSS Customization Tool")
---

### 6) Database Viewer
- A utility to interact with the underlying data tables.
- Provides detailed views and management options for advanced users.

![Database Viewer](Screenshots/Database%20Viewer.png "Database Viewer")

---

### 7) Damage Calculator
- Calculate the amount of damage needed to reduce a target to staking level.
- Analyze various combinations of items and their effects.

![Damage Calculator](Screenshots/Damage%20Calculator.png "Damage Calculator")

---

### 8) Power Information
- View detailed information about the powers available in the game, including their descriptions, costs, and effects.

![Power Information](Screenshots/Power%20Information.png "Power Information")

---

### 9) Interface and Theme Customization
- Customize the application's interface with personalized themes, including the minimap and main interface elements.

![Interface Theme](Screenshots/Interface%20Theme.png "Interface Theme")

---

## Development

This project is hosted on GitHub: [RBC-Map GitHub Repository](https://github.com/JELollis/RBC-Map). Contributions and feedback are always welcome!

### License
The RBC City Map Application is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

---

### Contributors

#### Development Team:
- **Windows Compatibility**: Jonathan Lollis (Nesmuth), Justin Solivan
- **Apple OSx Compatibility**: Joseph Lemois
- **Linux Compatibility**: Josh "Blaskewitts" Corse, Fern Lovebond
- **Design and Layout**: Shuvi, Blair Wilson (Ikunnaprinsess)

#### Special Thanks:
- [**LIAM²**](http://liam2.leprichaunproductions.com/home.php) by Cain "Leprechaun" McBride, which inspired this project.
- [**A View in the Dark**](https://aviewinthedark.net/) by Cliff Burton, providing the source for shops and guilds data.
- [**RavenBlack Wiki**](https://ravenblack.city/) contributors.
- **Anders** for **RBNav** and ongoing support.

---

We hope this tool enhances your experience in RavenBlack City. Thank you for using the RBC City Map application!
