<!--
# Copyright (C) 2021-2026 by TheAloneTeam@Github, < https://github.com/TheAloneTeam >.
# This file is part of < https://github.com/TheAloneTeam/MeowRobot > project,
# and is released under the "GNU v3.0 License Agreement".
# All rights reserved.
-->

<h1 align="center">
    ──「 MeowRoBot 」──
</h1>

<p align="center">
  <img src="https://yukiapi.site/file/sD81XdB7" alt="MeowRoBot Banner" width="450">
</p>

<p align="center">
  <b>An advanced, modular Telegram Group Management bot with intelligent AI Chatbot integration.</b>
</p>

<p align="center">
  <a href="https://github.com/TheAloneTeam/MeowRoBot/stargazers"><img src="https://img.shields.io/github/stars/TheAloneTeam/MeowRoBot?color=blue&logo=github&style=for-the-badge" alt="Stars"/></a>
  <a href="https://github.com/TheAloneTeam/MeowRoBot/network/members"><img src="https://img.shields.io/github/forks/TheAloneTeam/MeowRoBot?color=blue&logo=github&style=for-the-badge" alt="Forks"/></a>
  <a href="https://github.com/TheAloneTeam/MeowRoBot/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blueviolet?style=for-the-badge" alt="License"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11+-skyblue?style=for-the-badge&logo=python" alt="Python"/></a>
</p>

---

## ✨ Features

- 🤖 **AI Chatbot**: Context-aware natural chat responses in Hinglish and English. Long code blocks are automatically uploaded as downloadable script files.
- 🛡️ **Group Management**: Complete administrative toolset for ban, mute, kick, warn, temp-actions, antichannel, and pin management.
- 🔒 **Comprehensive Lock System**: Lock stickers, voice notes, photos, videos, gifs, audio, documents, forward messages, contacts, bot adds, invitelinks, spoilers, commands, and more.
- 📝 **Notes & Custom Filters**: Save text, photos, audio, videos, and button-rich links to serve fast automated replies.
- 🌙 **Night Mode**: Automatically locks groups at nighttime and re-opens in the morning.
- 👋 **Welcome & Goodbye**: Custom greetings with clean HTML/Markdown formatting and button support.
- 👥 **Couples of the Day**: Fun community engagement feature with stylized font rendering.
- ⚡ **High Performance**: Built with asynchronous Python, utilizing Pyrogram and python-telegram-bot alongside MongoDB and PostgreSQL/SQLite.

---

## 🚀 Deployment

### Deploy on Heroku

[![Deploy on Heroku](https://img.shields.io/badge/Deploy%20To%20Heroku-blueviolet?style=for-the-badge&logo=heroku)](https://dashboard.heroku.com/new?template=https://github.com/TheAloneTeam/MeowRoBot)

---

### Deploy on VPS / Local Machine

```bash
# 1. Update and install dependencies
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install python3-pip git -y

# 2. Clone the repository
git clone https://github.com/TheAloneTeam/MeowRoBot.git
cd MeowRoBot

# 3. Install required Python packages
pip3 install -U pip setuptools
pip3 install -U -r requirements.txt

# 4. Configure environment variables
nano MeowRobot/config.py

# 5. Run the bot
python3 -m MeowRobot
```

---

## ⚙️ Configuration Variables

| Variable | Description | Required | Default |
| :--- | :--- | :---: | :--- |
| `TOKEN` | Telegram Bot token from [@BotFather](https://t.me/BotFather) | **Yes** | — |
| `OWNER_ID` | Telegram User ID of the bot owner | **Yes** | — |
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) | **Yes** | — |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) | **Yes** | — |
| `DB_URI` | Database URL (PostgreSQL / SQLite) | **Yes** | `sqldb.db` |
| `MONGO_DB_URI` | MongoDB connection URI for persistent data | **Yes** | — |
| `SUPPORT_CHAT` | Telegram support group username | No | `TeamAashik` |
| `SUPPORT_CHANNEL` | Telegram updates channel username | No | `AashikTeam` |
| `CHATBOT_API_URL` | Endpoint for the AI Chatbot | No | `https://chatgp-nine.vercel.app/api/chat` |
| `CHATBOT_API_KEY` | Bearer API token for chatbot API | No | `ritesh-8179b3a5da99f300be2d50e1e9789729` |

---

## 💬 Community & Support

<p align="center">
  <a href="https://t.me/TeamAashik"><img src="https://img.shields.io/badge/Support%20Group-TeamAashik-blue?style=for-the-badge&logo=telegram" alt="Support Group"/></a>
  <a href="https://t.me/AashikTeam"><img src="https://img.shields.io/badge/Updates%20Channel-AashikTeam-blue?style=for-the-badge&logo=telegram" alt="Updates Channel"/></a>
</p>

---

## 📜 Credits & License

- **[TheAloneTeam](https://github.com/TheAloneTeam)** — Lead Developer & Maintainer
- **[Paul Larsen](https://github.com/PaulSonOfLars)** — Base framework inspiration
- **[Hamker Cat](https://github.com/TheHamkerCat)** — Modular concepts
- All contributors who help maintain and improve this project!

This project is open-source under the **[MIT License](https://github.com/TheAloneTeam/MeowRoBot/blob/main/LICENSE)**.
