.PHONY: venv init dev qa

venv:
	python3 -m venv venv

init: venv
	. venv/bin/activate
	pip install -e .

dev: init
	pip install -e .[dev]

qa:
	flake8 insta
