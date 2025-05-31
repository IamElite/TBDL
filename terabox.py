from aria2p import API as Aria2API, Client as Aria2Client
import asyncio
from dotenv import load_dotenv
from datetime import datetime
import os
import logging
import math
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
import time
import urllib.parse
from urllib.parse import urlparse
from flask import Flask, render_template
from threading import Thread

# Load environment variables from config.env
load_dotenv('config.env', override=True)

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s - %(filename)s:%(lineno)d"
)

logger = logging.getLogger(__name__)

# Suppress verbose logging from Pyrogram to keep logs clean
logging.getLogger("pyrogram.session").setLevel(logging.ERROR)
logging.getLogger("pyrogram.connection").setLevel(logging.ERROR)
logging.getLogger("pyrogram.dispatcher").setLevel(logging.ERROR)

# Get Aria2 host and port from environment variables, with fallbacks
ARIA2_HOST = os.environ.get('ARIA2_HOST', 'http://localhost')
ARIA2_PORT = int(os.environ.get('ARIA2_PORT', 6800))
ARIA2_SECRET = os.environ.get('ARIA2_SECRET', 'lollog') # Assuming secret might be needed

# Initialize Aria2 API client
try:
    aria2 = Aria2API(
        Aria2Client(
            host=ARIA2_HOST,
            port=ARIA2_PORT,
            secret=ARIA2_SECRET
        )
    )
    # Set global options for Aria2 downloads
    options = {
        "max-tries": "50",
        "retry-wait": "3",
        "continue": "true",
        "allow-overwrite": "true",
        "min-split-size": "4M",
        "split": "10"
    }
    aria2.set_global_options(options)
    logger.info(f"Aria2 client initialized successfully at {ARIA2_HOST}:{ARIA2_PORT}")
except Exception as e:
    logger.error(f"Failed to initialize Aria2 client: {e}. Please ensure Aria2 is running and accessible.")
    # Exit if Aria2 connection fails at startup, as it's a critical dependency
    exit(1)


# Load Telegram API credentials and other configurations from environment variables
API_ID = os.environ.get('TELEGRAM_API', '')
if len(API_ID) == 0:
    logging.error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)

API_HASH = os.environ.get('TELEGRAM_HASH', '')
if len(API_HASH) == 0:
    logging.error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    logging.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

DUMP_CHAT_ID = os.environ.get('DUMP_CHAT_ID', '')
if len(DUMP_CHAT_ID) == 0:
    logging.error("DUMP_CHAT_ID variable is missing! Exiting now")
    exit(1)
else:
    DUMP_CHAT_ID = int(DUMP_CHAT_ID)

USER_SESSION_STRING = os.environ.get('USER_SESSION_STRING', '')
if len(USER_SESSION_STRING) == 0:
    logging.info("USER_SESSION_STRING variable is missing! Bot will split Files in 2Gb...")
    USER_SESSION_STRING = None

# Initialize Pyrogram bot client
app = Client("jetbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user = None
# Define split size for files, adjusted if user session string is provided
SPLIT_SIZE = 2093796556 # Approximately 2 GB
if USER_SESSION_STRING:
    user = Client("jetu", api_id=API_ID, api_hash=API_HASH, session_string=USER_SESSION_STRING)
    SPLIT_SIZE = 4241280205 # Approximately 4 GB for user client

# List of valid Terabox domains for URL validation
VALID_DOMAINS = [
    'terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com',
    'momerybox.com', 'teraboxapp.com', '1024tera.com',
    'terabox.app', 'gibibox.com', 'goaibox.com', 'terasharelink.com',
    'teraboxlink.com', 'terafileshare.com'
]
last_update_time = 0

# Function to check if a given URL is from a valid Terabox domain
def is_valid_url(url):
    parsed_url = urlparse(url)
    return any(parsed_url.netloc.endswith(domain) for domain in VALID_DOMAINS)

# Function to format file sizes into human-readable format
def format_size(size):
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"

# Handler for the /start command
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    developer_button = InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ ⚡️", url="https://github.com")
    repo69 = InlineKeyboardButton("ʀᴇᴘᴏ 🌐", url="https://github.com")
    user_mention = message.from_user.mention
    reply_markup = InlineKeyboardMarkup([[developer_button], [repo69]])
    final_msg = f"ᴡᴇʟᴄᴏᴍᴇ, {user_mention}.\n\n🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ. sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ ɪ ᴡɪʟʟ ᴅᴏᴡɴʟᴏᴀᴅ ᴡɪᴛʜɪɴ ғᴇᴡ sᴇᴄᴏɴᴅs ᴀɴᴅ sᴇɴᴅ ɪᴛ ᴛᴏ ʏᴏᴜ ✨."
    video_file_id = "/app/Jet-Mirror.mp4" # Path to a video file for the start message
    if os.path.exists(video_file_id):
        await client.send_video(
            chat_id=message.chat.id,
            video=video_file_id,
            caption=final_msg,
            reply_markup=reply_markup
            )
    else:
        await message.reply_text(final_msg, reply_markup=reply_markup)

# Function to update the status message in Telegram
async def update_status_message(status_message, text):
    try:
        await status_message.edit_text(text)
    except Exception as e:
        logger.error(f"Failed to update status message: {e}")

# Handler for incoming text messages (Terabox links)
@app.on_message(filters.text)
async def handle_message(client: Client, message: Message):
    # Ignore commands other than /start and messages without a sender
    if message.text.startswith('/') and not message.text.startswith('/start'):
        return
    if not message.from_user:
        return

    user_id = message.from_user.id

    # Extract valid Terabox URL from the message text
    url = None
    for word in message.text.split():
        if is_valid_url(word):
            url = word
            break

    if not url:
        await message.reply_text("Please provide a valid Terabox link.")
        return

    # Encode the URL and construct the final API URL for Terabox
    encoded_url = urllib.parse.quote(url)
    final_url = f"https://wdzone-terabox-api.vercel.app/api?url={encoded_url}"

    # Add the download to Aria2
    download = aria2.add_uris([final_url])
    status_message = await message.reply_text("sᴇɴᴅɪɴɢ ʏᴏᴜ ᴛʜᴇ ᴍᴇᴅɪᴀ...🤤")

    start_time = datetime.now()

    # Monitor download progress and update status message
    while not download.is_complete:
        await asyncio.sleep(15) # Wait for 15 seconds before updating status
        download.update() # Refresh download status from Aria2
        progress = download.progress

        elapsed_time = datetime.now() - start_time
        elapsed_minutes, elapsed_seconds = divmod(elapsed_time.seconds, 60)

        status_text = (
            f"┏ ғɪʟᴇɴᴀᴍᴇ: {download.name}\n"
            f"┠ [{'★' * int(progress / 10)}{'☆' * (10 - int(progress / 10))}] {progress:.2f}%\n"
            f"┠ ᴘʀᴏᴄᴇssᴇᴅ: {format_size(download.completed_length)} ᴏғ {format_size(download.total_length)}\n"
            f"┠ sᴛᴀᴛᴜs: 📥 Downloading\n"
            f"┠ ᴇɴɢɪɴᴇ: <b><u>Aria2c v1.37.0</u></b>\n"
            f"┠ sᴘᴇᴇᴅ: {format_size(download.download_speed)}/s\n"
            f"┠ ᴇᴛᴀ: {download.eta} | ᴇʟᴀᴘsᴇᴅ: {elapsed_minutes}m {elapsed_seconds}s\n"
            f"┖ ᴜsᴇʀ: <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> | ɪᴅ: {user_id}\n"
        )
        while True:
            try:
                await update_status_message(status_message, status_text)
                break
            except FloodWait as e:
                logger.error(f"Flood wait detected! Sleeping for {e.value} seconds")
                await asyncio.sleep(e.value)

    file_path = download.files[0].path
    caption = (
        f"✨ {download.name}\n"
        f"👤 ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʙʏ : <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
    )

    last_update_time = time.time()
    UPDATE_INTERVAL = 15 # Interval for status message updates

    # Helper function to update status message with flood wait handling
    async def update_status(message, text):
        nonlocal last_update_time
        current_time = time.time()
        if current_time - last_update_time >= UPDATE_INTERVAL:
            try:
                await message.edit_text(text)
                last_update_time = current_time
            except FloodWait as e:
                logger.warning(f"FloodWait: Sleeping for {e.value}s")
                await asyncio.sleep(e.value)
                await update_status(message, text) # Retry after flood wait
            except Exception as e:
                logger.error(f"Error updating status: {e}")

    # Callback function for upload progress
    async def upload_progress(current, total):
        progress = (current / total) * 100
        elapsed_time = datetime.now() - start_time
        elapsed_minutes, elapsed_seconds = divmod(elapsed_time.seconds, 60)

        status_text = (
            f"┏ ғɪʟᴇɴᴀᴍᴇ: {download.name}\n"
            f"┠ [{'★' * int(progress / 10)}{'☆' * (10 - int(progress / 10))}] {progress:.2f}%\n"
            f"┠ ᴘʀᴏᴄᴇssᴇᴅ: {format_size(current)} ᴏғ {format_size(total)}\n"
            f"┠ sᴛᴀᴛᴜs: 📤 Uploading to Telegram\n"
            f"┠ ᴇɴɢɪɴᴇ: <b><u>PyroFork v2.2.11</u></b>\n"
            f"┠ sᴘᴇᴇᴅ: {format_size(current / elapsed_time.seconds if elapsed_time.seconds > 0 else 0)}/s\n"
            f"┠ ᴇʟᴀᴘsᴇᴅ: {elapsed_minutes}m {elapsed_seconds}s\n"
            f"┖ ᴜsᴇʀ: <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> | ɪᴅ: {user_id}\n"
        )
        await update_status(status_message, status_text)

    # Function to split video files using FFmpeg
    async def split_video_with_ffmpeg(input_path, output_prefix, split_size):
        try:
            original_ext = os.path.splitext(input_path)[1].lower() or '.mp4'
            start_time = datetime.now()
            last_progress_update = time.time()

            # Get total duration of the video using ffprobe
            proc = await asyncio.create_subprocess_exec(
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', input_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            total_duration = float(stdout.decode().strip())

            file_size = os.path.getsize(input_path)
            parts = math.ceil(file_size / split_size)

            if parts == 1:
                return [input_path] # No splitting needed if file size is within limits

            duration_per_part = total_duration / parts
            split_files = []

            for i in range(parts):
                current_time = time.time()
                if current_time - last_progress_update >= UPDATE_INTERVAL:
                    elapsed = datetime.now() - start_time
                    status_text = (
                        f"✂️ Splitting {os.path.basename(input_path)}\n"
                        f"Part {i+1}/{parts}\n"
                        f"Elapsed: {elapsed.seconds // 60}m {elapsed.seconds % 60}s"
                    )
                    await update_status(status_message, status_text)
                    last_progress_update = current_time

                output_path = f"{output_prefix}.{i+1:03d}{original_ext}"
                cmd = [
                    'ffmpeg', '-y', '-ss', str(i * duration_per_part), # Use ffmpeg
                    '-i', input_path, '-t', str(duration_per_part),
                    '-c', 'copy', '-map', '0',
                    '-avoid_negative_ts', 'make_zero',
                    output_path
                ]

                proc = await asyncio.create_subprocess_exec(*cmd)
                await proc.wait() # Wait for FFmpeg process to complete
                split_files.append(output_path)

            return split_files
        except Exception as e:
            logger.error(f"Split error: {e}")
            raise # Re-raise the exception to be caught by the caller

    # Function to handle file upload to Telegram, including splitting if necessary
    async def handle_upload():
        file_size = os.path.getsize(file_path)

        if file_size > SPLIT_SIZE:
            await update_status(
                status_message,
                f"✂️ Splitting {download.name} ({format_size(file_size)})"
            )

            split_files = await split_video_with_ffmpeg(
                file_path,
                os.path.splitext(file_path)[0],
                SPLIT_SIZE
            )

            try:
                for i, part in enumerate(split_files):
                    part_caption = f"{caption}\n\nPart {i+1}/{len(split_files)}"
                    await update_status(
                        status_message,
                        f"📤 Uploading part {i+1}/{len(split_files)}\n"
                        f"{os.path.basename(part)}"
                    )

                    if USER_SESSION_STRING:
                        # Upload using user client if session string is provided
                        sent = await user.send_video(
                            DUMP_CHAT_ID, part,
                            caption=part_caption,
                            progress=upload_progress
                        )
                        await app.copy_message(
                            message.chat.id, DUMP_CHAT_ID, sent.id
                        )
                    else:
                        # Upload using bot client
                        sent = await client.send_video(
                            DUMP_CHAT_ID, part,
                            caption=part_caption,
                            progress=upload_progress
                        )
                        # Forward the video to the user's chat from the dump chat
                        await client.send_video(
                            message.chat.id, sent.video.file_id,
                            caption=part_caption
                        )
                    os.remove(part) # Delete the split part after upload
            finally:
                # Ensure all split parts are removed even if an error occurs
                for part in split_files:
                    try: os.remove(part)
                    except: pass
        else:
            await update_status(
                status_message,
                f"📤 Uploading {download.name}\n"
                f"Size: {format_size(file_size)}"
            )

            if USER_SESSION_STRING:
                # Upload using user client if session string is provided
                sent = await user.send_video(
                    DUMP_CHAT_ID, file_path,
                    caption=caption,
                    progress=upload_progress
                )
                await app.copy_message(
                    message.chat.id, DUMP_CHAT_ID, sent.id
                )
            else:
                # Upload using bot client
                sent = await client.send_video(
                    DUMP_CHAT_ID, file_path,
                    caption=caption,
                    progress=upload_progress
                )
                # Forward the video to the user's chat from the dump chat
                await client.send_video(
                    message.chat.id, sent.video.file_id,
                    caption=caption
                )
        # Remove the original downloaded file after upload (or splitting and uploading)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Start the upload process
    start_time = datetime.now()
    await handle_upload()

    # Clean up status message and original user message
    try:
        await status_message.delete()
        await message.delete()
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

# Initialize Flask app for web server (for keeping the bot alive)
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return render_template("index.html") # Assuming an index.html exists for the web server

# Function to run Flask app in a separate thread
def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# Function to start the Flask web server
def keep_alive():
    Thread(target=run_flask).start()

# Function to start the Pyrogram user client (if USER_SESSION_STRING is provided)
async def start_user_client():
    if user:
        await user.start()
        logger.info("User client started.")

# Wrapper function to run the async user client in a new event loop
def run_user():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_user_client())

# Main execution block
if __name__ == "__main__":
    keep_alive() # Start Flask web server

    if user:
        logger.info("Starting user client...")
        Thread(target=run_user).start() # Start user client in a separate thread

    logger.info("Starting bot client...")
    app.run() # Start the main bot client (this is a blocking call)
