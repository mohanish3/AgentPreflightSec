# MVP screenshots draft pack

## Included now

### CLI scan (poisoned fixture)
- Command capture file: `assets/screenshots/cli-poisoned-output.txt`
- Recommended screenshot filename for submission: `assets/screenshots/cli-poisoned-playwright.png`

### CLI scan (clean fixture)
- Command capture file: `assets/screenshots/cli-clean-output.txt`
- Recommended screenshot filename for submission: `assets/screenshots/cli-clean-playwright.png`

## Playwright capture script (ready for cloud/CI)

Use this script in GitHub Actions or any runner with npm registry access:

```bash
npm i -D playwright
npx playwright install --with-deps chromium
node scripts/capture-cli-screenshots.mjs
```

Script path added in this update: `scripts/capture-cli-screenshots.mjs`.

## Additional MVP screenshots to capture
1. SARIF artifact upload in GitHub Security tab.
2. JSON report output snippet.
3. Optional `fix` command before/after.

