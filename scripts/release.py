#!/usr/bin/env python3
"""
Publish a new version of Mockup Workflow.

  python scripts/release.py 1.1.0            # bump the version, run the tests, build, zip, commit and tag
  python scripts/release.py 1.1.0 --no-build # without building the app

Steps:
  1. Check the version is semantic (MAJOR.MINOR.PATCH), greater than the current one, and that there are no
     uncommitted changes.
  2. Update version.py and turn the CHANGELOG "Unreleased" section into the new version with today's date.
  3. Run the tests.
  4. Build dist/Mockup Workflow.app and zip it as releases/Mockup-Workflow-<version>-macOS.zip.
  5. Commit "Release <version>" and create the annotated tag v<version>.
Nothing is pushed to any remote.
"""
import datetime
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PY = os.path.join(ROOT, '.venv', 'bin', 'python')


def run(*cmd, **kw):
    print('$', ' '.join(cmd))
    return subprocess.run(cmd, cwd=ROOT, check=True, **kw)


def out(*cmd):
    return subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def parse(v):
    m = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)', v)
    if not m:
        sys.exit(f'"{v}" is not a valid version: use MAJOR.MINOR.PATCH, for example 1.1.0')
    return tuple(int(x) for x in m.groups())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 1:
        sys.exit(__doc__)
    new = args[0]
    build = '--no-build' not in sys.argv

    vpath = os.path.join(ROOT, 'version.py')
    vsrc = open(vpath, encoding='utf-8').read()
    current = re.search(r"__version__ = '([^']+)'", vsrc).group(1)
    if parse(new) <= parse(current):
        sys.exit(f'The new version ({new}) must be greater than the current one ({current}).')
    if out('git', 'status', '--porcelain'):
        sys.exit('There are uncommitted changes. Commit or discard them before releasing.')
    if out('git', 'tag', '-l', f'v{new}'):
        sys.exit(f'Tag v{new} already exists.')

    cpath = os.path.join(ROOT, 'CHANGELOG.md')
    log = open(cpath, encoding='utf-8').read()
    head = '## [Unreleased]'
    if head not in log:
        sys.exit('CHANGELOG.md has no "## [Unreleased]" section.')
    pending = log.split(head, 1)[1].split('\n## [', 1)[0].strip()
    if not pending:
        sys.exit('The CHANGELOG "Unreleased" section is empty: list the changes in this version.')

    today = datetime.date.today().isoformat()
    open(vpath, 'w', encoding='utf-8').write(vsrc.replace(f"__version__ = '{current}'", f"__version__ = '{new}'"))
    open(cpath, 'w', encoding='utf-8').write(log.replace(head, f'{head}\n\n## [{new}] - {today}', 1))
    print(f'Version {current} -> {new}')

    run(PY, '-m', 'pytest', '-q')
    if build:
        run('bash', 'scripts/build_app.sh')
        os.makedirs(os.path.join(ROOT, 'releases'), exist_ok=True)
        zip_path = os.path.join('releases', f'Mockup-Workflow-{new}-macOS.zip')
        run('ditto', '-c', '-k', '--keepParent', 'dist/Mockup Workflow.app', zip_path)
        print(f'Package: {zip_path}')

    run('git', 'add', 'version.py', 'CHANGELOG.md')
    run('git', 'commit', '-m', f'Release {new}')
    run('git', 'tag', '-a', f'v{new}', '-m', f'Mockup Workflow {new}')
    print(f'\nDone: version {new} tagged v{new}.')


if __name__ == '__main__':
    main()
