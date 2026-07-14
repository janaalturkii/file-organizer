# Contributing

## Running tests

```bash
pip install -r requirements.txt
pytest -v
```

> Note: on Windows with OneDrive + Defender, newly created test files can be
> corrupted with null bytes. Create test fixture files directly in VS Code's
> editor rather than via shell redirects if you hit parsing errors.

## Internship checklist (per feature)

- [ ] Create a feature branch: `git checkout -b feature/<name>`
- [ ] Implement + add/update tests
- [ ] `pytest -v` passes locally
- [ ] Push branch, open a PR against `main`
- [ ] CI passes (GitHub Actions)
- [ ] Address trainer review comments
- [ ] Merge