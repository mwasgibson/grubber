# Release process for grubber

## Before releasing
- Run tests: `pytest`
- Update CHANGELOG.md
- Bump the version (see below)

## Where to bump the version
Common locations:
- pyproject.toml (PEP 621): update `project.version`
- pyproject.toml with poetry: update `tool.poetry.version`
- setup.cfg: update `metadata.version`
- grubber/__init__.py: update `__version__ = "X.Y.Z"`

Follow semantic versioning MAJOR.MINOR.PATCH.

## Manual release (local)
1. Commit and push changes to main.
2. Create annotated tag:
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z

3. Build artifacts:
   python -m pip install --upgrade build
   python -m build

4. Upload to PyPI:
   pip install --upgrade twine
   twine upload dist/* -u __token__ -p <PYPI_TOKEN>

(Use username `__token__` and your token string as password)

## Automatic release (GitHub Actions)
- Add secret PYPI_API_TOKEN to repo (Settings → Secrets → Actions)
- Push an annotated tag: workflow triggers on `push: tags: - 'v*'`

## Rollback
- Remove release on PyPI web UI (if needed)
- Delete tag and GitHub release if you want to revert the GitHub side
