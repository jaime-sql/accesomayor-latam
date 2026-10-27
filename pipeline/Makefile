.PHONY: audit test
audit:
	./run.sh $(FRAME) $(OUT) $(ARGS)
FRAME ?= ../data/page_frame.csv
OUT ?= out
ARGS ?=

test:
	[ -d .venv ] || python3 -m venv .venv
	.venv/bin/pip install -q -r requirements.txt
	.venv/bin/python -m pytest -q
