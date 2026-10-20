.PHONY: install build serve test experiments clean

VENV = .venv
PYTHON = $(VENV)/Scripts/python
UVICORN = $(VENV)/Scripts/uvicorn
PYTEST = $(VENV)/Scripts/pytest

install:
	uv pip install -e ".[dev]"

build:
	$(PYTHON) -m smarttest.cli build-all

serve:
	$(UVICORN) smarttest.api.main:app --reload --port 8000 --host 0.0.0.0

test:
	$(PYTEST) -v tests/

experiments:
	$(PYTHON) -m smarttest.cli experiments --force

clean:
	rm -rf artifacts/
