"""
Countdown Bot - Discord bot that counts down to 2:00pm Friday
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))

print(f"[INIT] Token: {bool(TOKEN)}, Channel: {CHANNEL_ID}")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

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
    """Schedule the next countdown update"""
    try:
        while True:
            total_secs, _ = get_time_remaining()
            
            if total_secs <= 0:
                print("[INFO] Countdown done")
                break
            
            # Determine wait time
            if total_secs <= 30:
                wait_time = 1
            elif total_secs <= 300:
                wait_time = 60
            else:
                wait_time = 3600
            
            await asyncio.sleep(wait_time)
            await post_countdown()
            
    except Exception as e:
        print(f"[ERROR] Schedule: {e}")


@bot.event
async def on_ready():
    """Bot ready event"""
    global target_time
    print(f"\n[SUCCESS] Connected as: {bot.user}")
    
    try:
        if CHANNEL_ID == 0:
            print("[ERROR] No CHANNEL_ID set")
            return
         
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print(f"[ERROR] Channel {CHANNEL_ID} not found")
            return
        
        print(f"[SUCCESS] Found channel: {channel.name}")
        
        target_time = get_next_friday_2pm()
        print(f"[SUCCESS] Target: {target_time}")
        
        await post_countdown()
        bot.loop.create_task(schedule_next_update())
        print("[SUCCESS] Bot ready!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


@bot.command(name='countdown')
async def countdown_command(ctx):
    """Manual countdown command"""
    _, message = get_time_remaining()
    await ctx.send(message)


print("[STARTUP] Running bot...")
bot.run(TOKEN)
