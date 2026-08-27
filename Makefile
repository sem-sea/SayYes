SHELL := /bin/bash
PY ?= python3
MOCK_PORT ?= 8931
AB_PORT ?= 8932
SMOKE_DIR := $(CURDIR)/.smoke

.DEFAULT_GOAL := check

.PHONY: help check validate selftest links bench bench-smoke ab-smoke report pairs preview clean

help:
	@echo "make check        run every offline check (what CI runs)"
	@echo "make validate     check skills/*/SKILL.md against the Agent Skills spec"
	@echo "make selftest     check every benchmark checker against its fixtures"
	@echo "make links        check that relative links in markdown resolve"
	@echo "make pairs        regenerate benchmark/pairs.jsonl from build_pairs.py"
	@echo "make bench-smoke  exercise the runner against a local mock endpoint"
	@echo "make bench        run the benchmark against a model (needs an API key)"
	@echo "make ab-smoke     exercise ab.py against a local mock endpoint"
	@echo "make report       build the results table from benchmark/results/"
	@echo "make preview      regenerate docs/assets/social-preview.png"

check: validate selftest links
	@echo "all offline checks passed"

validate:
	@$(PY) scripts/validate_skill.py

selftest:
	@$(PY) benchmark/selftest.py

links:
	@$(PY) scripts/check_links.py

pairs:
	@$(PY) benchmark/build_pairs.py

# Exercises run.py end to end against a canned local endpoint. It proves the
# plumbing works; it measures nothing about any model.
bench-smoke:
	@rm -rf "$(SMOKE_DIR)"
	@$(PY) benchmark/mockserver.py --port $(MOCK_PORT) & echo $$! > "$(CURDIR)/.mockpid"
	@for i in $$(seq 1 50); do \
		$(PY) -c "import socket,sys; s=socket.socket(); s.settimeout(0.2); sys.exit(0 if s.connect_ex(('127.0.0.1',$(MOCK_PORT)))==0 else 1)" && break; \
		sleep 0.1; \
	done
	@$(PY) benchmark/run.py --provider openai --model mock-model \
		--base-url http://127.0.0.1:$(MOCK_PORT)/v1 \
		--repeat 1 --limit 6 --attempts 1 \
		--label smoke --out-dir "$(SMOKE_DIR)" > /dev/null; \
		status=$$?; kill $$(cat "$(CURDIR)/.mockpid") 2>/dev/null; rm -f "$(CURDIR)/.mockpid"; \
		test $$status -eq 0
	@$(PY) -c "import json,pathlib,sys; \
rows=[json.loads(l) for l in (pathlib.Path('$(SMOKE_DIR)')/'smoke.jsonl').read_text().splitlines() if l.strip()]; \
assert len(rows)==12, f'expected 12 rows, found {len(rows)}'; \
assert {r['arm'] for r in rows}=={'negative','positive'}, 'expected both arms present'; \
assert all(isinstance(r['compliant'],bool) for r in rows), 'expected a boolean score per row'; \
print(f'bench-smoke ok: {len(rows)} rows scored end to end')"
	@$(MAKE) --no-print-directory ab-smoke
	@rm -rf "$(SMOKE_DIR)"

# Exercises ab.py against the same canned endpoint.
ab-smoke:
	@mkdir -p "$(SMOKE_DIR)"
	@$(PY) benchmark/mockserver.py --port $(AB_PORT) & echo $$! > "$(CURDIR)/.abpid"
	@for i in $$(seq 1 50); do \
		$(PY) -c "import socket,sys; s=socket.socket(); s.settimeout(0.2); sys.exit(0 if s.connect_ex(('127.0.0.1',$(AB_PORT)))==0 else 1)" && break; \
		sleep 0.1; \
	done
	@OPENAI_API_KEY=smoke $(PY) benchmark/ab.py \
		--a "Do not use bullet points." --b "Write the answer as prose paragraphs." \
		--task "Explain how DNS resolution works." --checker no_bullets --repeat 2 \
		--provider openai --model mock --base-url http://127.0.0.1:$(AB_PORT)/v1 \
		--save "$(SMOKE_DIR)/ab.jsonl" > /dev/null; \
		status=$$?; kill $$(cat "$(CURDIR)/.abpid") 2>/dev/null; rm -f "$(CURDIR)/.abpid"; \
		test $$status -eq 0
	@$(PY) -c "import json,pathlib; \
rows=[json.loads(l) for l in (pathlib.Path('$(SMOKE_DIR)')/'ab.jsonl').read_text().splitlines() if l.strip()]; \
assert len(rows)==4, f'expected 4 rows, found {len(rows)}'; \
assert {r['arm'] for r in rows}=={'A','B'}, 'expected both arms present'; \
print(f'ab-smoke ok: {len(rows)} rows scored end to end')"

# Real runs. Set ANTHROPIC_API_KEY or OPENAI_API_KEY first.
bench:
	@test -n "$$ANTHROPIC_API_KEY$$OPENAI_API_KEY" || { \
		echo "set ANTHROPIC_API_KEY or OPENAI_API_KEY first; see docs/HONEST-NUMBERS.md"; exit 1; }
	@test -z "$$ANTHROPIC_API_KEY" || $(PY) benchmark/run.py --provider anthropic --model $${ANTHROPIC_MODEL:-claude-sonnet-5} --repeat $${REPEAT:-3}
	@test -z "$$OPENAI_API_KEY" || $(PY) benchmark/run.py --provider openai --model $${OPENAI_MODEL:-gpt-5} --repeat $${REPEAT:-3}
	@$(MAKE) report

report:
	@$(PY) benchmark/report.py --by-alignment --by-checker

preview:
	@$(PY) scripts/make_preview.py

clean:
	@rm -rf "$(SMOKE_DIR)" "$(CURDIR)/.mockpid" "$(CURDIR)/.abpid" __pycache__ benchmark/__pycache__
