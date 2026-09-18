import assert from 'node:assert/strict';
import {
  mkdtemp,
  mkdir,
  readFile,
  readdir,
  rm,
  writeFile,
} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { runInNewContext } from 'node:vm';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const executable = path.join(projectRoot, 'bin', 'dockle-jsdoc.cjs');
const packageMetadata = JSON.parse(
  await readFile(path.join(projectRoot, 'package.json'), 'utf8'),
);

test('the packaged highlighter includes every built-in grammar', async () => {
  const source = await readFile(
    path.join(
      projectRoot,
      'src',
      'dockle',
      'sphinx',
      'themes',
      'dockle',
      'static',
      'highlight.min.js',
    ),
    'utf8',
  );
  const context = { console };
  context.globalThis = context;
  context.window = context;
  runInNewContext(source, context);

  const packagedLanguages = (await readdir(path.join(
    projectRoot,
    'node_modules',
    '@highlightjs',
    'cdn-assets',
    'languages',
  ))).filter((filename) => filename.endsWith('.min.js'));
  assert.equal(context.hljs.listLanguages().length, packagedLanguages.length);
  for (const reference of [
    path.join('.dockle', 'example-sources', 'sphinx', 'component-reference.md'),
    path.join('.dockle', 'example-sources', 'sphinx', 'component-reference-rst.rst'),
    path.join('.dockle', 'example-sources', 'doxygen', 'component-reference.md'),
    path.join('.dockle', 'example-sources', 'mkdocs', 'component-reference.md'),
    path.join('.dockle', 'example-sources', 'jsdoc', 'tutorials', 'component-reference.md'),
    path.join('.dockle', 'example-sources', 'rustdoc', 'component-reference.md'),
  ]) {
    const document = await readFile(path.join(projectRoot, reference), 'utf8');
    assert.equal(
      document.match(/class="dockle-language-gallery-header"/g)?.length,
      packagedLanguages.length,
      reference,
    );
  }
  for (const language of [
    'cmake',
    'console',
    'dockerfile',
    'markdown',
    'powershell',
    'rust',
    'shell',
    'toml',
    'typescript',
    'yaml',
  ]) {
    assert.ok(context.hljs.getLanguage(language), language);
  }
});

test('the npm command builds a self-contained native JSDoc site', async (context) => {
  const root = await mkdtemp(path.join(os.tmpdir(), 'dockle-jsdoc-'));
  context.after(() => rm(root, { force: true, recursive: true }));
  const source = path.join(root, 'src');
  const output = path.join(root, 'site');
  const tutorials = path.join(root, 'tutorials');
  await mkdir(source);
  await mkdir(tutorials);
  await writeFile(path.join(root, 'package.json'), JSON.stringify({
    name: 'native-jsdoc-example',
    repository: 'https://example.invalid/native-jsdoc-example',
    version: '1.2.3',
  }));
  await writeFile(path.join(root, 'logo.svg'), '<svg xmlns="http://www.w3.org/2000/svg"/>');
  await writeFile(path.join(root, 'favicon.svg'), '<svg xmlns="http://www.w3.org/2000/svg"/>');
  await writeFile(
    path.join(tutorials, 'component-reference.md'),
    '# Component reference\n',
  );
  await writeFile(path.join(tutorials, 'tutorials.json'), JSON.stringify({
    'component-reference': { title: 'Component reference' },
  }));
  await writeFile(path.join(source, 'example.js'), `/**
 * Add two values.
 * @param {number} left Left value.
 * @param {number} right Right value.
 * @returns {number} Their sum.
 */
export function add(left, right) { return left + right; }
`);
  const configuration = path.join(root, 'jsdoc.json');
  await writeFile(configuration, JSON.stringify({
    opts: {
      destination: output,
      recurse: true,
      tutorials,
    },
    source: {
      include: [source],
    },
    templates: {
      dockle: {
        favicon: 'favicon.svg',
        logo: 'logo.svg',
        targetTitle: 'Native JSDoc example',
      },
    },
  }));

  const result = spawnSync(
    process.execPath,
    [executable, '--configure', configuration, '--pedantic'],
    { cwd: root, encoding: 'utf8' },
  );
  assert.equal(result.status, 0, result.stderr || result.stdout);

  const document = await readFile(path.join(output, 'index.html'), 'utf8');
  const search = JSON.parse(await readFile(path.join(output, 'search.json'), 'utf8'));
  assert.match(document, /data-dockle-framework="jsdoc"/);
  assert.match(document, /data-dockle-theme="jsdoc"/);
  assert.match(document, /native-jsdoc-example/);
  assert.match(document, /https:\/\/example\.invalid\/native-jsdoc-example/);
  assert.ok(document.includes(`Dockle ${packageMetadata.version}`));
  assert.match(document, /JSDoc 4\.0\.5/);
  assert.match(document, /dockle-logo\.svg/);
  assert.match(document, /dockle-favicon\.svg/);
  assert.match(document, />Component reference<\/a>/);
  assert.doesNotMatch(document, />component-reference<\/a>/);
  assert.match(
    document,
    /pre\.prettyprint:not\(\.source\.linenums\)/,
  );
  assert.match(document, /classList\.remove\("prettyprint", "source"\)/);
  assert.doesNotMatch(document, /data-dockle-home/);
  assert.ok(search.docs.some((entry) => entry.text.includes('Add two values')));
  await readFile(path.join(output, 'dockle.css'), 'utf8');
  await readFile(path.join(output, 'dockle.js'), 'utf8');
  await readFile(path.join(output, 'highlight.min.js'), 'utf8');
  await readFile(path.join(output, 'lucide.min.js'), 'utf8');
});
