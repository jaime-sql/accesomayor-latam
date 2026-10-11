// Audits ONE url: Lighthouse (mobile, slow 4G throttling) then axe-core WCAG 2.2 in the same pinned Chrome.
// Prints JSON to stdout. visible_text is passed to the Python caller for in-memory readability and is never written to disk.
import puppeteer from 'puppeteer-core';
import lighthouse from 'lighthouse';
import { readFileSync } from 'node:fs';
const [url, chromePath] = process.argv.slice(2);
const UA_TAG = 'AccesoMayor-LatAm/0.1 accessibility-research';
const axeSrc = readFileSync(new URL('./node_modules/axe-core/axe.min.js', import.meta.url), 'utf8');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const out = { lighthouse: null, axe: null, visible_text: null, errors: [] };
const browser = await puppeteer.launch({ executablePath: chromePath, headless: true,
  args: ['--no-sandbox', '--disable-dev-shm-usage'] });
try {
  const port = new URL(browser.wsEndpoint()).port;
  try {
    const r = await lighthouse(url, { port: Number(port), output: 'json', logLevel: 'error',
      onlyCategories: ['performance', 'accessibility'], formFactor: 'mobile', throttlingMethod: 'simulate',
      screenEmulation: { mobile: true, width: 412, height: 823, deviceScaleFactor: 1.75, disabled: false } });
    const lhr = r.lhr, a = k => lhr.audits[k]?.numericValue ?? null;
    out.lighthouse = { version: lhr.lighthouseVersion, runtime_error: lhr.runtimeError?.code ?? null,
      perf: lhr.categories.performance.score, a11y: lhr.categories.accessibility.score,
      fcp_ms: a('first-contentful-paint'), lcp_ms: a('largest-contentful-paint'), tbt_ms: a('total-blocking-time'),
      cls: a('cumulative-layout-shift'), si_ms: a('speed-index'), total_bytes: a('total-byte-weight'),
      final_url: lhr.finalDisplayedUrl ?? lhr.finalUrl ?? null };
  } catch (e) { out.errors.push('lighthouse:' + (e.code || e.message).toString().slice(0, 120)); }
  await sleep(5000); // >=5 s before the next load of the same domain
  const page = await browser.newPage();
  await page.setUserAgent((await browser.userAgent()) + ' ' + UA_TAG);
  await page.emulate({ viewport: { width: 412, height: 823, isMobile: true, hasTouch: true, deviceScaleFactor: 1.75 },
    userAgent: (await browser.userAgent()) + ' ' + UA_TAG });
  try {
    const resp = await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
    out.http_status = resp ? resp.status() : null;
    out.final_url = page.url();
    out.lang = await page.evaluate(() => document.documentElement.lang || null);
    out.title = await page.title();
    await page.evaluate(axeSrc);
    out.final_url_lh = out.lighthouse?.final_url ?? null;
    const res = await page.evaluate(() => axe.run(document, { runOnly: { type: 'tag',
      values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] }, resultTypes: ['violations'] }));
    out.axe = { version: res.testEngine.version,
      violations: res.violations.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.length,
        tags: v.tags.filter(t => /^wcag\d{3,}$/.test(t)) })),
      incomplete: res.incomplete.length };
    out.visible_text = await page.evaluate(() => document.body ? document.body.innerText : '');
  } catch (e) { out.errors.push('axe:' + e.message.slice(0, 120)); }
} finally { await browser.close(); }
process.stdout.write(JSON.stringify(out));
