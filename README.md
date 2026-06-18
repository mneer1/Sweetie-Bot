English
An advanced Discord moderation and automation bot built with discord.py. It automatically fetches artwork from Derpibooru, filters content dynamically based on custom tags, and routes them through an interactive admin review queue before publishing to public channels.

Features
Automated Content Scraper: Periodically checks for new media matching specific criteria.

Dynamic Tag Control: Whitelist or blacklist tags on-the-fly using chat commands.

Interactive Approvals: Buttons for Admins to Approve (✅) or Deny (❌) posts directly from Discord.

Action Logs & Statistics: Automatically logs which admin took action and saves metrics locally to stats.json.

Public Webhook Delivery: Sends approved content with an embedded "Download Image" button for end-users.

Modular Architecture: Utilizes Discord Cogs to cleanly separate command categories.

SWEETIE BOT/
│
├── commands/                  # Bot Cogs (Modules)
│   ├── admin.py               # Cleaning chat and latency tools
│   ├── stats_and_legendary.py # System statistics and high-voted posts
│   └── tags.py                # Live API tag manager
│
├── .gitignore                 # Prevents uploading local data (like stats.json)
├── bot.py                     # Main application entry point
├── CHANGELOG.md               # Version history
├── config.py                  # Secrets, Tokens, and default tags
├── derpibooru.py              # Dynamic API query builder
└── requirements.txt           # Python dependencies


Setup & Installation
Clone the repository:

git clone https://github.com/yourusername/sweetie-bot.git
cd sweetie-bot

Install dependencies:
pip install -r requirements.txt

Configure Environment:
Open config.py and fill in your credentials:

TOKEN = "YOUR_DISCORD_BOT_TOKEN"
WEBHOOK_URL = "YOUR_PUBLIC_CHANNEL_WEBHOOK_URL"
ADMIN_CHANNEL_ID = 123456789012345678  # Admin review channel ID

Run the Bot:
python bot.py

| Command | Permission | Description |
| :--- | :--- | :--- |
| `!add_tag <tag>` | Administrator | Adds a tag to the safe inclusion list. |
| `!block_tag <tag>` | Administrator | Adds a tag to the exclusion filter list. |
| `!show_tags` | Manage Messages | Displays current inclusion and exclusion filters. |
| `!clear <1-100>` | Manage Messages | Clears a specified number of messages from the channel. |
| `!stats` | Manage Messages | Displays overall review statistics and admin performance leaderboard. |
| `!legendary` | Everyone | Fetches a random highly-upvoted "Safe" post from the platform. |
| `!test` | Everyone | Basic response test to ensure the bot is online. |