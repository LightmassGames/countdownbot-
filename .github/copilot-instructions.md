<!-- Countdown Bot - Discord Bot for counting down to Friday 2:00pm -->

## Project Overview
Countdown bot is a Discord bot that provides a countdown to 2:00pm Friday with intervals:
- Hourly updates until 5 minutes remain
- Minute-by-minute updates from 5 minutes to 30 seconds
- Second-by-second countdown for the final 30 seconds

## Setup Instructions
1. Install Python 3.9+
2. Create `.env` file with `DISCORD_TOKEN=your_token_here`
3. Run `pip install -r requirements.txt`
4. Run `python bot.py`

## Project Structure
- `bot.py` - Main bot file with countdown logic
- `requirements.txt` - Python dependencies
- `.env` - Discord bot token (not in repo)
