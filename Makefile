PYTHON ?= python
MANIM ?= $(PYTHON) -m manim

# Default options (override from CLI)
SCRIPT ?= binary_search.py
SCENE ?=
QUALITY ?= qh
PREVIEW ?= 1
EXTRA ?=

# Render all *_manim.py scripts by default
SCRIPTS ?= $(wildcard *_manim.py)

PREVIEW_FLAG :=
ifneq (,$(filter 1 true yes on,$(PREVIEW)))
PREVIEW_FLAG := -p
endif

.PHONY: help render render-all

help:
	@echo "Usage:"
	@echo "  make render SCRIPT=<file.py> [SCENE=<SceneName>] [QUALITY=ql|qm|qh|qk] [PREVIEW=1|0] [EXTRA='...']"
	@echo "  make render-all [SCRIPTS='a.py b.py'] [QUALITY=ql|qm|qh|qk] [PREVIEW=1|0] [EXTRA='...']"
	@echo ""
	@echo "Examples:"
	@echo "  make render SCRIPT=binary_search.py SCENE=BinarySearch QUALITY=qh PREVIEW=1"
	@echo "  make render SCRIPT=main.py QUALITY=qm PREVIEW=0"
	@echo "  make render-all QUALITY=ql PREVIEW=0"

render:
	@if [ ! -f "$(SCRIPT)" ]; then \
		echo "Error: script not found -> $(SCRIPT)"; \
		exit 1; \
	fi
	@echo "Rendering $(SCRIPT) $(if $(SCENE),scene=$(SCENE),all-scenes) quality=$(QUALITY) preview=$(PREVIEW)"
	@$(MANIM) -$(QUALITY) $(PREVIEW_FLAG) "$(SCRIPT)" $(SCENE) $(EXTRA)

render-all:
	@if [ -z "$(strip $(SCRIPTS))" ]; then \
		echo "Error: no scripts found. Set SCRIPTS manually."; \
		exit 1; \
	fi
	@for s in $(SCRIPTS); do \
		if [ -f "$$s" ]; then \
			echo "Rendering $$s (all scenes) quality=$(QUALITY) preview=$(PREVIEW)"; \
			$(MANIM) -$(QUALITY) $(PREVIEW_FLAG) "$$s" $(EXTRA) || exit $$?; \
		else \
			echo "Skip missing script: $$s"; \
		fi; \
	done
