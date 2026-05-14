# Countdown Bot 🤖

A Discord bot that counts down to 2:00pm Friday with "Xos becomes a doctor in <hours>" messages.

## Features

- **Hourly updates** until 5 minutes remain
- **Minute-by-minute updates** from 5 minutes to 30 seconds
- **Second-by-second countdown** for the final 30 seconds
- **Automatic scheduling** of countdown messages
- **Manual commands** to check countdown or reset

## Setup

### Prerequisites
- Python 3.9 or higher
- A Discord bot token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Channel ID where you want the bot to post messages

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your credentials:
   ```
   DISCORD_TOKEN=your_bot_token_here
   CHANNEL_ID=your_channel_id_here
   ```

### Getting Your Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" section and click "Add Bot"
4. Copy the token under "TOKEN"
5. Enable necessary Intents under "Privileged Gateway Intents" (Message Content Intent)

### Getting Your Channel ID

1. Enable Developer Mode in Discord (User Settings → App Settings → Advanced → Developer Mode)
2. Right-click the channel where you want messages posted
3. Select "Copy Channel ID"

### Running the Bot

```bash
python bot.py
```

The bot will:
- Connect to Discord
- Calculate time until next Friday 2:00 PM
- Post an initial countdown message
- Automatically post updates at the intervals specified above

## Commands

- `!countdown` - Display current countdown
- `!reset` - Reset countdown to next Friday 2:00 PM

## Project Structure

```
.
├── bot.py                 # Main bot file with countdown logic
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .env                  # Your credentials (not in repo)
└── .github/
    └── copilot-instructions.md  # Project documentation
```

## How It Works

1. Bot calculates the next Friday at 2:00 PM
2. Calculates time remaining
3. Based on time remaining, determines update frequency:
   - **> 5 minutes**: Updates every hour
   - **5 minutes to 30 seconds**: Updates every minute
   - **< 30 seconds**: Updates every second
4. Posts formatted message: "Xos becomes a doctor in X hours/minutes/seconds"

## Troubleshooting

### Bot doesn't post messages
- Verify `CHANNEL_ID` is correct
- Check bot has permissions to post in the channel
- Ensure bot has "Send Messages" permission

### "Token is invalid" error
- Double-check your `DISCORD_TOKEN` in `.env`
- Regenerate token in Developer Portal if needed

### Missing Channel ID error
- Add `CHANNEL_ID=` to your `.env` file with the correct channel ID
