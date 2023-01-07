sources = .
.PHONY: format lint setup

test: format lint unittest

format:
	isort $(sources)
	black $(sources)

lint:
	flake8 $(sources)

setup:
	conda create -n whisper-bot python==3.8 -y && conda activate whisper-bot
	pip install -r ./requirements.txt
	# git clone https://github.com/ggerganov/whisper.cpp.git
	cd whisper.cpp && make small
