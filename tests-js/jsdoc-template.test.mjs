import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const executable = path.join(projectRoot, 'bin', 'dockle-jsdoc.cjs');
const packageMetadata = JSON.parse(
  await readFile(path.join(projectRoot, 'package.json'), 'utf8'),
);

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
  await writeFile(path.join(tutorials, 'showcase.md'), '# Component reference\n');
  await writeFile(path.join(tutorials, 'tutorials.json'), JSON.stringify({
    showcase: { title: 'Component reference' },
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
  assert.doesNotMatch(document, />showcase<\/a>/);
  assert.doesNotMatch(document, /data-dockle-home/);
  assert.ok(search.docs.some((entry) => entry.text.includes('Add two values')));
  await readFile(path.join(output, 'dockle.css'), 'utf8');
  await readFile(path.join(output, 'dockle.js'), 'utf8');
  await readFile(path.join(output, 'lucide.min.js'), 'utf8');
});
