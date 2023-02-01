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
