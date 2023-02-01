# whisper-bot
A Telegram bot that converts voice messages to text


## Local environment setup

Create conda environment and install packages

```bash
conda create -n whisper-bot python==3.8 -y
conda activate whisper-bot
# install this independently as on lightning cloud it will already be there
pip install lightning  
pip install -r ./requirements.txt
```

or simply

```bash
make setup
```

## Prepare telegram bot

Create a new app on [Telegram](https://my.telegram.org/apps) and get the `API_ID`, `API_HASH`.
For more info see [Pyrogram docs](https://docs.pyrogram.org/start/setup).

Then, follow the normal procedure to create a bot through [BotFather](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0) and get the `BOT_TOKEN`.

Once you get these variables, store them as environment variables. In case you want to run the app on lightning, you also
need to add them as [secrets](https://lightning.ai/docs/stable/glossary/secrets.html?highlight=secrets).


## Run

Run locally using

```
lightning run app app.py
```

Move computation to the cloud

```bash
lightning run app app.py \
    --setup \
    --cloud \
    --secret API_ID=API-ID \  # need to bind the secrets to env vars
    --secret API_HASH=API-HASH \
    --secret BOT_TOKEN=BOT-TOKEN
```
