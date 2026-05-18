<div align="center">
  <h1>🛡️ Activity Hider (AI-Powered Panic Button)</h1>
  <p>
    <strong>A next-generation, context-aware panic button powered by GPT-4o-mini.</strong>
  </p>
  
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
  [![PyQt6](https://img.shields.io/badge/PyQt-6-green.svg?style=flat-square&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/intro)
  [![OpenAI](https://img.shields.io/badge/AI-GPT--4o--mini-black.svg?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

  <p>
    Have you ever needed to instantly hide your screen when someone walks into the room? <br>
    <i>Activity Hider doesn't just hide your game; it analyzes your context using AI and instantly brings up a completely unrelated, safe application to perfectly camouflage your activity!</i>
  </p>
</div>

<hr>

## ✨ Features

- 🧠 **Context-Aware AI Decisions:** Powered by GitHub Models (GPT-4o-mini), the application analyzes what you are currently doing (e.g., gaming vs. coding) and instantly opens an app from the **opposite** category to provide the perfect alibi.
- ⚡ **Lightning Fast Execution:** Minimizes all active windows in milliseconds and maximizes your "decoy" application seamlessly using low-level Win32 APIs.
- 🕵️ **Silent Background Operation:** Lives entirely in your system tray without any annoying console windows. 
- 🚀 **UAC-Bypass Auto Start:** Registers itself to Windows Task Scheduler with the highest privileges, ensuring it starts silently on boot without triggering UAC prompts, while retaining the ability to hook into elevated games (like Valorant or CS2).
- 🎛️ **Modern GUI Settings:** A sleek, PyQt6-based dashboard to manage your camouflage app pool, run AI system scans to automatically find apps on your PC, and configure repeat limits to ensure the AI doesn't pick the same decoy twice.

## 🛠️ Installation

**1. Clone the repository:**
```bash
git clone https://github.com/mtozsoy/ActivityHider.git
cd ActivityHider
```

**2. Create a virtual environment & install dependencies:**
```bash
python -m venv .venv
# Activate the venv (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install required packages
pip install PyQt6 qdarkstyle openai pywin32 keyboard python-dotenv
```

**3. Configure AI API Key:**
This project relies on GitHub Models for AI inference. 
- Get a free Personal Access Token from GitHub.
- Create a `.env` file in the root directory.
- Add your token:
```env
GITHUB_TOKEN=ghp_your_personal_access_token_here
```

## 🎮 Usage

1. Run the application:
```bash
python main.py
```
*(Note: The app will request Administrator privileges if it doesn't already have them, as it needs to intercept hotkeys even when anti-cheat protected games are in focus).*

2. The application will minimize to your system tray (look for the red shield icon).
3. **Double-click** the tray icon to open the GUI dashboard.
4. **Settings Tab:** Click `[Yapay Zeka ile Sistemi Tara]` to automatically scan and categorize the software on your PC, building your camouflage arsenal.
5. Hit the **Panic Hotkey (F12)** anytime, anywhere. Watch the magic happen!

## 🏗️ Architecture

- `main.py`: Orchestrates the hotkey listening loop and executes the "Panic Sequence".
- `ai_engine.py`: Polls the system every few seconds, analyzes the current active window, and queries GPT-4o-mini to prepare a contextually appropriate decoy application in advance.
- `gui_app.py`: A multithreaded PyQt6 interface for configuration and live AI status monitoring.
- `app_scanner.py`: Scans Windows start menu/desktop shortcuts and categorizes them automatically.
- `startup_manager.py`: Interacts with Windows `schtasks` to manage silent logon startups.

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 📄 License
[MIT](https://choosealicense.com/licenses/mit/)
