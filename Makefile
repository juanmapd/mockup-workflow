# Mockup Workflow: common tasks. `make help` lists them.
PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: help setup run desktop test check build icon release clean

help:  ## Show this help
	@grep -E '^[a-z]+:.*## ' Makefile | awk -F':.*## ' '{printf "  make %-9s %s\n", $$1, $$2}'

setup:  ## Create the virtualenv and install all dependencies
	test -x $(PY) || python3 -m venv .venv
	$(PY) -m pip install -q --upgrade pip
	$(PIP) install -q -r requirements.txt -r requirements-app.txt -r requirements-dev.txt

run:  ## Start in the browser (http://127.0.0.1:5173)
	$(PY) app.py

desktop:  ## Open the native window without building
	$(PY) desktop.py

test:  ## Run the tests (PSD=path.psd adds the fidelity test)
	MW_TEST_PSD="$(PSD)" $(PY) -m pytest -q

check:  ## Compare a PSD render with Photoshop: make check PSD=path.psd
	$(PY) mockup.py "$(PSD)" --check

build:  ## Build dist/Mockup Workflow.app
	bash scripts/build_app.sh

icon:  ## Regenerate the icon in assets/
	$(PY) scripts/make_icon.py

release:  ## Publish a version: make release VERSION=1.1.0
	@test -n "$(VERSION)" || (echo "Specify the version: make release VERSION=1.1.0" && exit 1)
	$(PY) scripts/release.py $(VERSION)

clean:  ## Remove builds and caches (leaves data and the gallery alone)
	rm -rf build dist __pycache__ tests/__pycache__ .pytest_cache
