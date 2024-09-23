
ifneq (,$(wildcard /.dockerenv))
	PYTHON_BIN := /usr/local/bin/python3
	PIP_BIN := /usr/local/bin/pip3
	PYLINT_BIN := ~/.local/bin/pylint
	MYPY_BIN := ~/.local/bin/mypy
	TWINE_BIN := ~/.local/bin/twine
	PIP_INSTALL := $(PIP_BIN) install --progress-bar=off --user
else
	VENV_DIR := ./.venv
	PYTHON_BIN := $(VENV_DIR)/bin/python3
	PIP_BIN := $(VENV_DIR)/bin/pip3
	PYLINT_BIN := $(VENV_DIR)/bin/pylint
	MYPY_BIN := $(VENV_DIR)/bin/mypy
	TWINE_BIN := $(VENV_DIR)/bin/twine
	PIP_INSTALL := $(PIP_BIN) install --progress-bar=off
endif

# Find images, support multiple case insensitive extensions and file names with spaces, consistently sort files
FIND_IMAGES := find exif-samples-master -regextype posix-egrep -iregex ".*\.(bmp|gif|heic|heif|jpg|jpeg|png|tiff|webp)" -print0 | LC_COLLATE=C sort -fz | xargs -0

.PHONY: help
all: help

venv: ## Set up the virtual environment
	virtualenv -p python3 $(VENV_DIR)

lint: ## Run linting (pylint)
	$(PYLINT_BIN) -f colorized ./exifread

mypy: ## Run mypy
	$(MYPY_BIN) --show-error-context ./exifread ./EXIF.py

#test: ## Run all tests
#	$(PYTHON_BIN) -m unittest discover -v -s ./tests

analyze: lint mypy ## Run all static analysis tools

reqs-install: ## Install with all requirements
	$(PIP_INSTALL) .[dev]

samples-download: ## Install sample files used for testing.
	rm -fr master.tar.gz exif-samples-master
	wget https://github.com/ianare/exif-samples/archive/master.tar.gz
	tar -xzf master.tar.gz

run: ## Run EXIF.py on sample images
	$(FIND_IMAGES) EXIF.py -dc

compare: ## Run and compare exif dump
	$(FIND_IMAGES) EXIF.py > exif-samples-master/dump_test
	diff -Zu --color --suppress-common-lines exif-samples-master/dump exif-samples-master/dump_test

build:  ## build distribution
	rm -fr ./dist
	$(PYTHON_BIN) setup.py sdist bdist_wheel

publish: build ## Publish to PyPI
	$(TWINE_BIN) upload --repository testpypi dist/*

help: Makefile
	@echo
	@echo "Choose a command to run:"
	@echo
	@grep --no-filename -E '^[a-zA-Z_%-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf " \033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo
