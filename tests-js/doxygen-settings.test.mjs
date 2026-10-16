import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { createContext, runInContext } from 'node:vm';

const runtimePath = fileURLToPath(new URL(
  '../src/dockle/sphinx/themes/dockle/static/doxygen-settings.js', import.meta.url,
));
const runtime = await readFile(runtimePath, 'utf8');
const fixturePath = fileURLToPath(new URL('./fixtures/doxygen-cookie.js', import.meta.url));
const cookieSource = await readFile(fixturePath, 'utf8');

function createStorage() {
  const values = new Map();
  return {
    values,
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key),
  };
}

function createBrowser(chromium) {
  const cookies = new Map();
  return {
    cookies,
    localStorage: createStorage(),
    sessionStorage: createStorage(),
    window: chromium ? { chrome: {} } : {},
    cookieDocument: {
      get cookie() {
        return [...cookies].map(([key, value]) => `${key}=${value}`).join('; ');
      },
      set cookie(assignment) {
        const [pair] = assignment.split(';');
        const separator = pair.indexOf('=');
        const key = pair.slice(0, separator);
        const value = pair.slice(separator + 1);
        if (!value && /;\s*expires=/i.test(assignment)) cookies.delete(key);
        else cookies.set(key, value);
      },
    },
  };
}

function loadSettings(browser, root, pages = ['index.html', 'usage.html', 'd0/d00/source.html']) {
  const document = Object.create(browser.cookieDocument);
  document.currentScript = { src: `https://docs.example.test${root}cookie.js` };
  document.addEventListener = () => {};
  const context = createContext({ ...browser, document, URL, dockleDoxygenNavigationPages: pages });
  runInContext(cookieSource, context, { filename: fixturePath });
  runInContext(runtime, context, { filename: runtimePath });
  return runInContext('Cookie', context);
}

for (const [browserName, chromium] of [['Firefox', false], ['Chromium', true]]) {
  test(`${browserName} ignores legacy state and isolates projects and versions`, () => {
    const browser = createBrowser(chromium);
    browser.cookies.set('doxygen_navpath', 'foreign.html');
    browser.sessionStorage.setItem('doxygen_navpath', 'foreign.html');
    const first = loadSettings(browser, '/projects/first/master/');
    const second = loadSettings(browser, '/projects/second/master/');
    const release = loadSettings(browser, '/projects/first/v1/');

    assert.equal(first.readSetting('navpath', ''), '');
    first.writeSetting('navpath', 'usage.html#details', 0);
    assert.equal(first.readSetting('navpath', ''), 'usage.html#details');
    assert.equal(second.readSetting('navpath', ''), '');
    assert.equal(release.readSetting('navpath', ''), '');
    assert.notEqual(first.cookie_namespace, second.cookie_namespace);
    assert.notEqual(first.cookie_namespace, release.cookie_namespace);
    assert.equal(
      first.cookie_namespace,
      'dockle_doxygen_%2Fprojects%2Ffirst%2Fmaster%2F_',
    );
  });

  test(`${browserName} preserves valid pages and rejects removed or unindexed pages`, () => {
    const browser = createBrowser(chromium);
    const settings = loadSettings(browser, '/projects/first/master/');
    for (const page of ['index.html', 'usage.html#removed-anchor', 'd0/d00/source.html#l123']) {
      settings.writeSetting('navpath', page, 0);
      assert.equal(settings.readSetting('navpath', ''), page);
    }
    for (const page of ['removed.html', 'foreign.html#section', 'dockle-search.html']) {
      settings.writeSetting('navpath', page, 0);
      assert.equal(settings.readSetting('navpath', 'index.html'), 'index.html');
      assert.equal(settings.readSetting('navpath', ''), '');
      assert.equal(browser.cookies.has(`${settings.cookie_namespace}navpath`), false);
      assert.equal(browser.sessionStorage.values.has(`${settings.cookie_namespace}navpath`), false);
    }
  });

  test(`${browserName} drops a saved page removed by a rebuild`, () => {
    const browser = createBrowser(chromium);
    const before = loadSettings(browser, '/projects/first/master/', ['index.html', 'removed.html']);
    before.writeSetting('navpath', 'removed.html#details', 0);
    assert.equal(before.readSetting('navpath', ''), 'removed.html#details');
    const after = loadSettings(browser, '/projects/first/master/', ['index.html']);
    assert.equal(after.readSetting('navpath', ''), '');
  });

  test(`${browserName} keeps ordinary settings and later valid sidebar writes`, () => {
    const settings = loadSettings(createBrowser(chromium), '/projects/first/master/');
    assert.equal(settings.readSetting('navpath', ''), '');
    settings.writeSetting('width', '300');
    assert.equal(settings.readSetting('width', '250'), '300');
    settings.writeSetting('navpath', 'removed.html', 0);
    assert.equal(settings.readSetting('navpath', ''), '');
    settings.writeSetting('navpath', 'usage.html', 0);
    assert.equal(settings.readSetting('navpath', ''), 'usage.html');
  });
}

test('Chromium rejects invalid state from both persistent and session storage', () => {
  const browser = createBrowser(true);
  const settings = loadSettings(browser, '/projects/first/master/');
  const key = `${settings.cookie_namespace}navpath`;
  browser.localStorage.setItem(key, 'removed.html');
  browser.sessionStorage.setItem(key, 'foreign.html');
  assert.equal(settings.readSetting('navpath', ''), '');
  assert.equal(settings.readSetting('navpath', ''), '');
  assert.equal(browser.localStorage.values.has(key), false);
  assert.equal(browser.sessionStorage.values.has(key), false);
});

test('documentation roots with spaces or Unicode remain distinct', () => {
  const browser = createBrowser(false);
  const first = loadSettings(browser, '/projects/first%20name/master/');
  const second = loadSettings(browser, '/projects/first-name/master/');
  const unicode = loadSettings(browser, '/projects/caf%C3%A9/master/');
  first.writeSetting('navpath', 'usage.html', 0);
  unicode.writeSetting('navpath', 'index.html', 0);
  assert.equal(first.readSetting('navpath', ''), 'usage.html');
  assert.equal(second.readSetting('navpath', ''), '');
  assert.equal(unicode.readSetting('navpath', ''), 'index.html');
});

test('Doxygen versions without the Cookie helper are left untouched', () => {
  assert.doesNotThrow(() => runInContext(runtime, createContext({}), { filename: runtimePath }));
});

test('responsive layout discards native panel dimensions on initialization and resize', () => {
  const panels = new Map();
  for (const id of ['side-nav', 'nav-tree', 'doc-content', 'page-nav']) {
    const values = new Map([
      ['height', '999px'], ['width', '250px'], ['margin-left', '250px'],
      ['overflow', 'auto'],
    ]);
    panels.set(id, { style: {
      getPropertyValue: (property) => values.get(property) ?? '',
      removeProperty: (property) => values.delete(property),
    }, values });
  }
  const observers = [];
  const events = [];
  const container = { style: {} };
  panels.get('page-nav').offsetWidth = 224;
  const context = createContext({
    Cookie: { readSetting() {} },
    dockleDoxygenNavigationPages: [],
    URL,
    document: {
      currentScript: { src: 'https://docs.example.test/cookie.js' },
      addEventListener: (...args) => events.push(args),
      getElementById: (id) => id === 'container' ? container : panels.get(id),
    },
    MutationObserver: class {
      constructor(callback) { this.callback = callback; }
      observe(panel, options) { observers.push({ panel, options, callback: this.callback }); }
    },
  });
  runInContext(runtime, context, { filename: runtimePath });
  assert.equal(events[0][0], 'DOMContentLoaded');
  assert.equal(events[0][2].once, true);
  events[0][1]();
  assert.equal(observers.length, 4);
  assert.equal(container.style.gridTemplateColumns, 'auto 224px');
  for (const { panel, options, callback } of observers) {
    assert.equal(options.attributes, true);
    assert.deepEqual(Array.from(options.attributeFilter), ['style']);
    assert.equal(panel.values.get('overflow'), 'auto');
    const removed = ['height', 'width', 'margin-left'].filter((p) => !panel.values.has(p));
    assert.ok(removed.length > 0);
    for (const property of removed) panel.values.set(property, '123px');
    callback();
    for (const property of removed) assert.equal(panel.values.has(property), false);
    // Repeated delivery after our own removals must not cause more style writes.
    panel.style.removeProperty = () => assert.fail('unchanged styles were rewritten');
    callback();
  }
  panels.get('page-nav').offsetWidth = 0;
  container.style.gridTemplateColumns = 'auto 6px';
  observers[3].callback();
  assert.equal(container.style.gridTemplateColumns, 'auto 6px');
  panels.clear();
  assert.doesNotThrow(() => events[0][1]());
});
