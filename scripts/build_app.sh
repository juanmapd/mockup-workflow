#!/bin/bash
# Build Mockup Workflow.app (output in dist/). Usage: ./build_app.sh
set -e
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt -r requirements-app.txt
VERSION=$(.venv/bin/python -c 'from version import __version__; print(__version__)')
echo "Building Mockup Workflow $VERSION..."
rm -rf build dist
.venv/bin/pyinstaller --noconfirm MockupWorkflow.spec
# Register the app so Finder opens .mwf files with it.
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$PWD/dist/Mockup Workflow.app"
echo "Done: dist/Mockup Workflow.app ($VERSION)"
