# whisper-bot
A Telegram bot that converts audio to text


## Setup

Create conda environment and install packages

```bash
conda create -n whisper-bot python==3.8 -y
conda activate whisper-bot
pip install -r ./requirements.txt
```

Clone Whisper C++ implementation [repo](https://github.com/ggerganov/whisper.cpp) and download the `small` model

```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp && make small
```

Or simply
```
make setup
```

Create a new app on [Telegram](https://my.telegram.org/apps) and get the `API_ID`, `API_HASH`.
For more info see [Pyrogram docs](https://docs.pyrogram.org/start/setup).

Then, follow the normal procedure to create a bot through [BotFather](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0) and get the `BOT_TOKEN`.

Once you get these variables, store them as environment variables. In case you want to run the app on lightning, you also
need to add them as [secrets](https://lightning.ai/docs/stable/glossary/secrets.html?highlight=secrets).


## Run

Run locally using Pyrogram

```bash
python run.py
```

Run locally with lightning

```
lightning run app app.py
```

Move computation on the cloud

```bash
lightning run app app.py \
    --setup \
    --cloud \
    --secret API_ID=API-ID \  # need to bind the secrets to env vars
    --secret API_HASH=API-HASH \
    --secret BOT_TOKEN=BOT-TOKEN
```
