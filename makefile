sources = .
.PHONY: format lint setup

test: format lint unittest

format:
	isort $(sources)
	black $(sources)

lint:
	flake8 $(sources)

setup:
	conda create -n whisper-bot python==3.8 -y && conda activate whisper-bot && pip install lightning && pip install -r ./requirements.txt

deploy:
	lightning run app app.py --cloud --secret API_ID=API-ID --secret API_HASH=API-HASH --secret BOT_TOKEN=BOT-TOKEN --no-cache

run:
	lightning run app app.py