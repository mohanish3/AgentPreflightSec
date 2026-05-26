import { chromium } from 'playwright';
import { readFileSync, mkdirSync } from 'node:fs';

const targets = [
  {
    inFile: 'assets/screenshots/cli-poisoned-output.txt',
    outFile: 'assets/screenshots/cli-poisoned-playwright.png',
    title: 'AgentPreflight CLI scan - poisoned fixture',
  },
  {
    inFile: 'assets/screenshots/cli-clean-output.txt',
    outFile: 'assets/screenshots/cli-clean-playwright.png',
    title: 'AgentPreflight CLI scan - clean fixture',
  },
];

mkdirSync('assets/screenshots', { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });

for (const t of targets) {
  const content = readFileSync(t.inFile, 'utf8');
  const html = `<!doctype html><html><body style="margin:0;background:#0b1020;color:#dbeafe;font-family: ui-monospace, SFMono-Regular, Menlo, monospace;">
    <div style="padding:24px;">
      <h1 style="font-size:24px;margin:0 0 16px 0;">${t.title}</h1>
      <pre style="white-space:pre-wrap;line-height:1.35;font-size:14px;background:#111827;padding:16px;border-radius:8px;border:1px solid #334155;">${content.replace(/</g, '&lt;')}</pre>
    </div>
  </body></html>`;
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.screenshot({ path: t.outFile, fullPage: true });
  console.log(`wrote ${t.outFile}`);
}

await browser.close();
