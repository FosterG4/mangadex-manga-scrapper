# GitHub Actions Workflows

This directory contains automated testing workflows for the MangaDex Manga Downloader.

## Workflows

### 1. Quick Tests (`quick-test.yml`)

**Triggers:** Every push and pull request to `main`

**Duration:** ~2 minutes

**What it does:**
- ✅ Runs fast unit tests
- ✅ Checks API connectivity (ping test)
- ✅ Validates all imports work
- ✅ Validates configuration
- ✅ Checks for accidentally committed `.env` files

**Purpose:** Fast feedback for developers

### 2. Full Tests (`test.yml`)

**Triggers:** Push/PR to `main` or `develop`, manual dispatch

**Duration:** ~5-10 minutes

**What it does:**

#### Test Matrix
- **Python versions:** 3.9, 3.10, 3.11, 3.12
- **Operating systems:** Ubuntu, Windows
- **Total combinations:** 8 test runs

#### Test Jobs

**1. Unit Tests**
- Runs all unit tests
- Tests API connectivity
- Tests search functionality (1 result limit)
- Tests download manager initialization
- Lint checks (Python 3.11+)

**2. Integration Tests (Limited)**
- Quick integration tests with limits
- Downloads only 1 chapter for testing
- 5-minute timeout to prevent long runs
- Continues on error (non-blocking)

**3. Code Quality**
- Syntax error checks
- Import order validation (isort)
- Security checks (bandit)

**4. Build Check**
- Verifies dependencies install
- Checks if main.py runs
- Validates all imports

## Test Limits

To keep CI/CD fast and avoid rate limiting:

### API Call Limits
- Search: `limit=1` (only 1 result)
- Chapters: `limit=1` (only 1 chapter)
- Downloads: Skipped in CI (structure test only)

### Timeouts
- Quick tests: 5 minutes total
- Integration tests: 5 minutes per job
- Individual tests: 1-3 minutes

### Rate Limiting
- Respects MangaDex's ~5 req/s limit
- Uses default `RATE_LIMIT_DELAY=0.25s`
- Minimal API calls during tests

## Running Workflows Manually

### Via GitHub UI
1. Go to **Actions** tab
2. Select workflow (Quick Tests or Tests)
3. Click **Run workflow**
4. Choose branch
5. Click **Run workflow**

### Via GitHub CLI
```bash
# Run quick tests
gh workflow run quick-test.yml

# Run full tests
gh workflow run test.yml
```

## Viewing Results

### Status Badges
Check the README badges for current status:
- [![Tests](https://github.com/thorryuk/mangadex-manga-scrapper/workflows/Tests/badge.svg)](https://github.com/thorryuk/mangadex-manga-scrapper/actions)
- [![Quick Tests](https://github.com/thorryuk/mangadex-manga-scrapper/workflows/Quick%20Tests/badge.svg)](https://github.com/thorryuk/mangadex-manga-scrapper/actions)

### Actions Tab
1. Go to repository
2. Click **Actions** tab
3. View workflow runs
4. Click on a run to see details
5. Click on a job to see logs

## Troubleshooting

### Tests Failing?

**Check:**
1. **API connectivity** - Is MangaDex API online?
2. **Rate limits** - Did we exceed API limits?
3. **Dependencies** - Are requirements.txt up to date?
4. **Python version** - Compatible with 3.9+?

**Common Issues:**

#### API Connection Failed
```
Solution: MangaDex API might be down, check https://mangadex.org
Action: Re-run workflow after a few minutes
```

#### Rate Limited
```
Solution: Too many API calls in tests
Action: Increase RATE_LIMIT_DELAY in tests
```

#### Import Errors
```
Solution: Missing dependency or wrong Python version
Action: Update requirements.txt or Python version
```

## Adding New Tests

### To Quick Tests
Edit `.github/workflows/quick-test.yml`:
```yaml
- name: Your new test
  run: |
    python -c "your test code here"
  timeout-minutes: 1
```

### To Full Tests
Edit `.github/workflows/test.yml`:
```yaml
- name: Your new test
  run: |
    python -m unittest tests.your_test
```

## Best Practices

### ✅ DO
- Keep tests fast (<5 minutes)
- Use minimal API calls
- Add timeouts to prevent hanging
- Test on multiple Python versions
- Test on multiple OS (Ubuntu, Windows)

### ❌ DON'T
- Download large amounts of data
- Make excessive API calls
- Run tests without timeouts
- Test features requiring authentication
- Commit `.env` files

## Environment Variables

Available in workflows:
- `RUN_INTEGRATION_TESTS=true` - Enable integration tests
- `TEST_DOWNLOAD_LIMIT=1` - Limit downloads in tests
- `GITHUB_ACTIONS=true` - Indicates running in CI

## Security

### Secrets
No secrets are currently used. If needed:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add repository secrets
3. Reference in workflow: `${{ secrets.SECRET_NAME }}`

### API Keys
Not required for public MangaDex API endpoints.

## Maintenance

### Updating Workflows
1. Edit workflow files
2. Commit and push
3. Workflow runs automatically
4. Check results in Actions tab

### Updating Dependencies
When updating `requirements.txt`:
1. Tests will automatically use new dependencies
2. Check if tests still pass
3. Update Python version matrix if needed

## Performance

### Current Performance
- **Quick Tests:** ~2 minutes
- **Full Tests:** ~5-10 minutes
- **Total CI time:** ~7-12 minutes

### Optimization Tips
- Use caching for pip dependencies (already enabled)
- Limit API calls in tests
- Use `continue-on-error` for non-critical tests
- Run expensive tests only on specific branches

## Contributing

When adding features:
1. Add unit tests
2. Update workflows if needed
3. Ensure tests pass locally
4. Check CI results after pushing

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python setup action](https://github.com/actions/setup-python)
- [Checkout action](https://github.com/actions/checkout)
