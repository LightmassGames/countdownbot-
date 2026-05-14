"""
Countdown Bot - Discord bot that counts down to 2:00pm Friday
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))  # Set in .env

# Create bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Global variables
current_update_task = None
target_time = None
last_message_time = None


def get_next_friday_2pm():
    """Calculate the next Friday at 2:00 PM"""
    now = datetime.now()
    
    # Days until Friday (Friday is 4, Monday is 0)
    days_until_friday = (4 - now.weekday()) % 7
    
    # If today is Friday and it's after 2 PM, get next Friday
    if days_until_friday == 0 and now.hour >= 14:
        days_until_friday = 7
    
    target = now + timedelta(days=days_until_friday)
    target = target.replace(hour=14, minute=0, second=0, microsecond=0)
    
    return target


def get_time_remaining():
    """Get remaining time and return (total_seconds, formatted_string)"""
    global target_time
    if target_time is None:
        target_time = get_next_friday_2pm()
    
    now = datetime.now()
    remaining = target_time - now
    total_seconds = int(remaining.total_seconds())
    
    if total_seconds <= 0:
        return 0, "Xos is now a doctor!"
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return total_seconds, f"Xos becomes a doctor in {hours} hour{'s' if hours != 1 else ''}"
    elif minutes > 0:
        return total_seconds, f"Xos becomes a doctor in {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        return total_seconds, f"Xos becomes a doctor in {seconds} second{'s' if seconds != 1 else ''}"


async def post_countdown():
    """Post a countdown message to the channel"""
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel {CHANNEL_ID} not found")
        return
    
    total_secs, message = get_time_remaining()
    
    try:
        await channel.send(message)
    except Exception as e:
        print(f"Error posting message: {e}")


async def schedule_next_update():
    """Schedule the next countdown update based on time remaining"""
    global current_update_task
    
    total_secs, _ = get_time_remaining()
    
    if total_secs <= 0:
        print("Countdown complete!")
        return
    
    # Final 30 seconds: update every second
    if total_secs <= 30:
        wait_time = 1
    # 30 seconds to 5 minutes: update every minute
    elif total_secs <= 300:
        wait_time = 60
    # More than 5 minutes: update every hour
    else:
        wait_time = 3600
    
    # Cancel existing task if any
    if current_update_task is not None:
        current_update_task.cancel()
    
    # Schedule next update
    current_update_task = bot.loop.create_task(countdown_update(wait_time))


async def countdown_update(wait_seconds):
    """Wait and then post update"""
    try:
        await discord.utils.sleep_until(datetime.now() + timedelta(seconds=wait_seconds))
        await post_countdown()
        await schedule_next_update()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error in countdown_update: {e}")


@bot.event
async def on_ready():
    """Bot ready event - start countdown"""
    global target_time
    try:
        print(f'{bot.user} has connected to Discord!')
        print(f"Bot ID: {bot.user.id}")
        
        if CHANNEL_ID == 0:
            print("ERROR: CHANNEL_ID not set in .env file")
            return
        
        channel = bot.get_channel(CHANNEL_ID)
        if channel is None:
            print(f"ERROR: Channel {CHANNEL_ID} not found. Bot may not have access.")
            return
        
        print(f"Channel found: {channel.name}")
        
        target_time = get_next_friday_2pm()
        print(f"Countdown target: {target_time}")
        print(f"Posting to channel: {CHANNEL_ID}")
        
        # Post initial message and schedule updates
        await post_countdown()
        await schedule_next_update()
        print("Bot ready and countdown scheduled!")
    except Exception as e:
        print(f"ERROR in on_ready: {e}")
        import traceback
        traceback.print_exc()


@bot.command(name='countdown')
async def countdown_command(ctx):
    """Manual countdown command"""
    _, message = get_time_remaining()
    await ctx.send(message)


@bot.command(name='reset')
async def reset_command(ctx):
    """Reset the countdown to next Friday"""
    global target_time, current_update_task
    
    if current_update_task:
        current_update_task.cancel()
    
    target_time = get_next_friday_2pm()
    print(f"Countdown reset to: {target_time}")
    
    await ctx.send(f"Countdown reset to next Friday 2:00 PM")
    await post_countdown()
    await schedule_next_update()


if __name__ == '__main__':
    try:
        print(f"Starting bot with token and channel ID: {CHANNEL_ID}")
        bot.run(TOKEN)
    except Exception as e:
        print(f"Fatal error starting bot: {e}")
        import traceback
        traceback.print_exc()
