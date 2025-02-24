from pyrogram import Client, filters
import os
import subprocess
import shutil
import time

API_ID = "23122482"
API_HASH = "8d6a0daeb1fed02340bd273e57cb1766"
BOT_TOKEN = "7625460128:AAFGfkHYXjG4F9XEltII-5ctPqOiP32UHww"

bot = Client("video_cutter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.video)
async def video_handler(client, message):
    start_time = time.time()
    msg = await message.reply("📥 Downloading video...")

    async def progress(current, total):
        percent = (current / total) * 100
        progress_bar = "▓" * int(percent / 5) + "░" * (20 - int(percent / 5))
        await msg.edit(f"📥 Downloading... {percent:.2f}%\n[{progress_bar}]")

    video_path = await message.download(progress=progress)
    
    await msg.edit("✅ Download complete! 🔄 Splitting video...")

    temp_folder = "/storage/emulated/0/Download/Telegram/All Clips"
    gallery_folder = "/storage/emulated/0/DCIM/Camera"
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(gallery_folder, exist_ok=True)

    output_pattern = os.path.join(temp_folder, "clip_%02d.mp4")

    split_cmd = f'ffmpeg -i "{video_path}" -c copy -map 0 -segment_time 00:01:00 -f segment "{output_pattern}"'
    
    split_start = time.time()
    subprocess.run(split_cmd, shell=True)
    split_end = time.time()

    clips = sorted(os.listdir(temp_folder))
    total_clips = len(clips)

    await msg.edit(f"✅ Video split done in {split_end - split_start:.2f} sec! 🎬 Total clips: {total_clips} \n📤 Sending & Saving to Gallery...")

    for index, file in enumerate(clips, start=1):
        progress_bar = "▓" * int((index / total_clips) * 20) + "░" * (20 - int((index / total_clips) * 20))
        await msg.edit(f"📤 Sending clip {index}/{total_clips}...\n[{progress_bar}]")

        file_path = os.path.join(temp_folder, file)
        new_file_name = f"clip {index}.mp4"
        new_file_path = os.path.join(gallery_folder, new_file_name)

        shutil.move(file_path, new_file_path)  # **Gallery me save kare bina manually "Save to Gallery" click kiye**
        await message.reply_video(video=new_file_path, caption=f"📽 Clip {index}/{total_clips}")

    end_time = time.time()
    await msg.edit(f"✅ All clips sent & saved in Gallery in {end_time - start_time:.2f} sec! 🎉")

    os.remove(video_path)

bot.run()