"""
Countdown Bot - Discord bot that counts down to 2:00pm Friday
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import os
import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID_STR = os.getenv('CHANNEL_ID', '0')

print(f"[INIT] Loading...")
print(f"[INIT] Token present: {bool(TOKEN)}")
print(f"[INIT] Channel ID env: {CHANNEL_ID_STR}")

try:
    CHANNEL_ID = int(CHANNEL_ID_STR)
except:
    CHANNEL_ID = 0
    print(f"[ERROR] Invalid CHANNEL_ID: {CHANNEL_ID_STR}")

print(f"[INIT] Parsed Channel ID: {CHANNEL_ID}")

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


@bot.event
async def on_ready():
    """Bot ready event"""
    global target_time
    print(f"\n[READY] Bot connected: {bot.user}")
    print(f"[READY] Guilds: {len(bot.guilds)}")
    
    # Only fire once
    if hasattr(bot, '_ready_fired'):
        return
    bot._ready_fired = True
    
    try:
        print(f"[READY] Setting up countdown...")
        
        if CHANNEL_ID == 0:
            print("[READY] ERROR: No CHANNEL_ID")
            return
        
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print(f"[READY] ERROR: Channel {CHANNEL_ID} not accessible")
            return
        
        print(f"[READY] Channel: {channel.name} ({CHANNEL_ID})")
        target_time = get_next_friday_2pm()
        print(f"[READY] Target time: {target_time}")
        
        # Send initial message
        try:
            _, msg = get_time_remaining()
            await channel.send(msg)
            print(f"[READY] Initial message sent")
        except Exception as e:
            print(f"[READY] Failed to send initial message: {e}")
        
        # Start background countdown task
        bot.loop.create_task(background_countdown())
        print(f"[READY] Background task started")
        print(f"[READY] Bot is ready! ✓\n")
        
    except Exception as e:
        print(f"[READY] FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


async def background_countdown():
    """Background task that posts countdown updates"""
    print("[BG] Countdown task started")
    
    try:
        while True:
            try:
                total_secs, _ = get_time_remaining()
                
                if total_secs <= 0:
                    print("[BG] Countdown complete")
                    break
                
                # Determine wait time
                if total_secs <= 30:
                    wait = 1
                elif total_secs <= 300:
                    wait = 60
                else:
                    wait = 3600
                
                print(f"[BG] Waiting {wait}s (remaining: {total_secs}s)")
                await asyncio.sleep(wait)
                
                # Post update
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    _, msg = get_time_remaining()
                    await channel.send(msg)
                    print(f"[BG] Posted: {msg}")
                
            except asyncio.CancelledError:
                print("[BG] Task cancelled")
                break
            except Exception as e:
                print(f"[BG] Error in loop: {e}")
                await asyncio.sleep(5)
                
    except Exception as e:
        print(f"[BG] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


@bot.command(name='countdown')
async def countdown_command(ctx):
    """Manual countdown command"""
    _, message = get_time_remaining()
    await ctx.send(message)


# Keep bot alive with heartbeat logging
@bot.event
async def on_message(message):
    """Log message events and process commands"""
    if message.author == bot.user:
        return
    await bot.process_commands(message)


print("\n" + "="*50)
print("[STARTUP] Discord Countdown Bot")
print(f"[STARTUP] Token: {'***' if TOKEN else 'MISSING'}")
print(f"[STARTUP] Channel: {CHANNEL_ID}")
print("="*50 + "\n")

try:
    bot.run(TOKEN)
except KeyboardInterrupt:
    print("\n[SHUTDOWN] Interrupted by user")
except Exception as e:
    print(f"\n[ERROR] Fatal error: {e}")
    import traceback
    traceback.print_exc()

