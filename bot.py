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

# Use stderr for immediate output (won't be buffered)
def log(msg):
    print(f"{msg}", file=sys.stderr, flush=True)

log("[START] Loading bot...")

try:
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    CHANNEL_ID_STR = os.getenv('CHANNEL_ID', '0')
    
    log(f"[START] TOKEN present: {bool(TOKEN)}")
    log(f"[START] CHANNEL_ID raw: {CHANNEL_ID_STR}")
    
    try:
        CHANNEL_ID = int(CHANNEL_ID_STR)
    except:
        CHANNEL_ID = 0
        log(f"[ERROR] Invalid CHANNEL_ID: {CHANNEL_ID_STR}")
    
    log(f"[START] CHANNEL_ID parsed: {CHANNEL_ID}")


    log(f"[START] Creating bot intents...")
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    
    log(f"[START] Creating bot instance...")
    bot = commands.Bot(command_prefix='!', intents=intents)
    log(f"[START] Bot instance created")

except Exception as e:
    log(f"[FATAL] Error during initialization: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

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


async def get_channel_or_fetch(channel_id: int):
    """Get the channel from cache or fetch it if missing."""
    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as e:
            log(f"Error fetching channel {channel_id}: {e}")
            return None
    return channel


async def post_countdown():
    """Post a countdown message to the channel"""
    channel = await get_channel_or_fetch(CHANNEL_ID)
    if channel is None:
        log(f"Channel {CHANNEL_ID} not found")
        return
    
    total_secs, message = get_time_remaining()
    
    try:
        await channel.send(message)
        log(f"Posted countdown: {message}")
    except Exception as e:
        log(f"Error posting message: {e}")


@bot.event
async def on_ready():
    """Bot ready event"""
    global target_time
    log(f"\n[READY] Bot connected: {bot.user}")
    log(f"[READY] Guilds: {len(bot.guilds)}")
    
    # Only fire once
    if hasattr(bot, '_ready_fired'):
        return
    bot._ready_fired = True
    
    try:
        log(f"[READY] Setting up countdown...")
        
        if CHANNEL_ID == 0:
            log("[READY] ERROR: No CHANNEL_ID")
            return
        
        channel = await get_channel_or_fetch(CHANNEL_ID)
        if not channel:
            log(f"[READY] ERROR: Channel {CHANNEL_ID} not accessible")
            return
        
        log(f"[READY] Channel: {channel.name} ({CHANNEL_ID})")
        target_time = get_next_friday_2pm()
        log(f"[READY] Target time: {target_time}")
        
        # Send initial message immediately
        try:
            await post_countdown()
            log(f"[READY] Initial countdown sent immediately")
        except Exception as e:
            log(f"[READY] Failed to send initial message: {e}")
        
        # Start background countdown task
        bot.loop.create_task(background_countdown())
        log(f"[READY] Background task started")
        log(f"[READY] Bot is ready! ✓\n")
        
    except Exception as e:
        log(f"[READY] FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)


def get_next_wait_time(total_secs: int) -> float:
    """Return seconds until the next scheduled update."""
    now = datetime.now()
    if total_secs <= 30:
        return 1.0
    if total_secs <= 300:
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        wait = (next_minute - now).total_seconds()
        return max(1.0, wait)
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    wait = (next_hour - now).total_seconds()
    # Don't sleep past the 5-minute window — we need to switch to per-minute updates
    wait = min(wait, total_secs - 300)
    return max(1.0, wait)


async def background_countdown():
    """Background task that posts countdown updates"""
    log("[BG] Countdown task started")
    
    try:
        while True:
            try:
                total_secs, _ = get_time_remaining()
                
                if total_secs <= 0:
                    log("[BG] Countdown complete")
                    break
                
                wait = get_next_wait_time(total_secs)
                log(f"[BG] Waiting {wait:.1f}s (remaining: {total_secs}s)")
                await asyncio.sleep(wait)
                
                # Post update
                channel = await get_channel_or_fetch(CHANNEL_ID)
                if channel:
                    _, msg = get_time_remaining()
                    await channel.send(msg)
                    log(f"[BG] Posted: {msg}")
                
            except asyncio.CancelledError:
                log("[BG] Task cancelled")
                break
            except Exception as e:
                log(f"[BG] Error in loop: {e}")
                await asyncio.sleep(5)
                
    except Exception as e:
        log(f"[BG] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)


@bot.command(name='countdown')
async def countdown_command(ctx):
    """Manual countdown command"""
    _, message = get_time_remaining()
    await ctx.send(message)


GOOPED_UP_GIRL_ID = 311874651750006785
XOS_ID = 361616461925580800
ADIZZEL_ID = 361378854528614403


# Keep bot alive with heartbeat logging
@bot.event
async def on_message(message):
    """Log message events and process commands"""
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        if message.author.id == GOOPED_UP_GIRL_ID:
            try:
                await message.reply("Yes mommy")
                log(f"Replied 'Yes mommy' to {message.author}")
            except Exception as e:
                log(f"Error replying to mention: {e}")
        elif message.author.id == XOS_ID:
            total_secs, _ = get_time_remaining()
            if total_secs <= 0:
                try:
                    await message.reply("Yes doctor")
                    log(f"Replied 'Yes doctor' to {message.author}")
                except Exception as e:
                    log(f"Error replying to mention: {e}")

    if (
        message.author.id == GOOPED_UP_GIRL_ID
        and any(u.id == ADIZZEL_ID for u in message.mentions)
        and "what do you think" in message.content.lower()
    ):
        try:
            await message.channel.send(
                f"\N{PLEADING FACE} yes <@{ADIZZEL_ID}> what do you think of me"
            )
            log(f"Sent pleading-face line in response to {message.author}")
        except Exception as e:
            log(f"Error sending pleading-face reply: {e}")

    await bot.process_commands(message)


log("\n" + "="*60)
log("[STARTUP] Discord Countdown Bot Starting")
log(f"[STARTUP] Token loaded: {'YES' if TOKEN else 'NO'}")
log(f"[STARTUP] Channel ID: {CHANNEL_ID}")
log("="*60 + "\n")
log("[MAIN] Calling bot.run()...")

try:
    bot.run(TOKEN)
except KeyboardInterrupt:
    log("\n[SHUTDOWN] Interrupted by user")
except Exception as e:
    log(f"\n[ERROR] Fatal error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc(file=sys.stderr)

