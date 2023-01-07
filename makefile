sources = .
.PHONY: format lint setup

test: format lint unittest

format:
	isort $(sources)
	black $(sources)

lint:
	flake8 $(sources)

setup:
	git clone https://github.com/ggerganov/whisper.cpp.git
	cd whisper.cpp
	make small
