
ifneq (,$(wildcard /.dockerenv))
	PYTHON_BIN := /usr/local/bin/python3
	PIP_BIN := /usr/local/bin/pip3
	PRE_COMMIT_BIN := ~/.local/bin/pre-commit
	TWINE_BIN := ~/.local/bin/twine
	PIP_INSTALL := $(PIP_BIN) install --progress-bar=off --user
else
	VENV_DIR := ./.venv
	PYTHON_BIN := $(VENV_DIR)/bin/python3
	PIP_BIN := $(VENV_DIR)/bin/pip3
	PRE_COMMIT_BIN := $(VENV_DIR)/bin/pre-commit
	TWINE_BIN := $(VENV_DIR)/bin/twine
	PIP_INSTALL := $(PIP_BIN) install --progress-bar=off
endif

# If exifread is installed locally (e.g. pip install -e .), use it, else fallback to local bin
EXIF_PY := $(if $(shell which EXIF.py),EXIF.py,./EXIF.py)

# Find images, support multiple case insensitive extensions and file names with spaces
FIND_IMAGES := find tests/resources -regextype posix-egrep -iregex ".*\.(bmp|gif|heic|heif|jpg|jpeg|png|tiff|webp)" -print0 | LC_COLLATE=C sort -fz | xargs -0


.PHONY: help
all: help

venv: ## Set up the virtual environment
	virtualenv -p python3 $(VENV_DIR)

test: ## Run exifread on all sample images
	$(FIND_IMAGES) $(EXIF_PY) -dc

test-diff: ## Run and compare exif dump
	$(FIND_IMAGES) $(EXIF_PY) > tests/resources/dump_test
	diff -Zu --color --suppress-common-lines tests/resources/dump tests/resources/dump_test

analyze: ## Run all static analysis tools
	$(PRE_COMMIT_BIN) run --all

reqs-install: ## Install with all requirements
	$(PIP_INSTALL) .[dev]

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
