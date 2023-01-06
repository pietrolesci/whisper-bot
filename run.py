from pyrogram import Client, filters
from pyrogram.types import Message
import uvloop
uvloop.install()


# API_ID="24954710"
# API_HASH="f8d9c83ac504bdc0af5fa697d969a591"
# BOT_TOKEN="5806075360:AAFnPfCjwc5VToQ3xeitN7G0BEOlhid9u4M"

# app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
app = Client("my_bot")


@app.on_message(filters.text & filters.private)
async def echo(client: Client, message: Message):
    await message.reply(message.text)

@app.on_message(filters.voice & filters.private)
async def echo(client: Client, message: Message):
    await message.reply_voice(message.voice.file_id, caption="Transcribed file")
    

app.run()  # Automatically start() and idle()