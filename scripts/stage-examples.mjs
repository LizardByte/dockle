import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { runInNewContext } from 'node:vm';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const examplesRoot = path.join(root, 'examples');
const stagedExamplesRoot = path.join(root, '.dockle', 'example-sources');
const runtimePath = path.join(
  root,
  'src',
  'dockle',
  'sphinx',
  'themes',
  'dockle',
  'static',
  'highlight.min.js',
);
const commonPath = path.join(
  examplesRoot,
  'shared',
  'component-reference.md.inc',
);
const targets = [
  {
    framework: 'sphinx',
    output: 'component-reference.md',
    specific: path.join(examplesRoot, 'sphinx', 'component-reference.md.inc'),
    useNeutralFence: true,
  },
  {
    framework: 'doxygen',
    output: 'component-reference.md',
    specific: path.join(examplesRoot, 'doxygen', 'component-reference.md.inc'),
  },
  {
    framework: 'mkdocs',
    output: 'component-reference.md',
    specific: path.join(examplesRoot, 'mkdocs', 'component-reference.md.inc'),
  },
  {
    framework: 'jsdoc',
    output: path.join('tutorials', 'component-reference.md'),
  },
  {
    framework: 'rustdoc',
    output: 'component-reference.md',
  },
];

const samples = new Map([
  ['bash', '# Build one target.\ntarget=api\npython -m dockle build "$target"'],
  ['c', '/* Build one target. */\nconst char *target = "api";\nreturn target != 0;'],
  ['cpp', '// Build one target.\nconst std::string target{"api"};\nreturn !target.empty();'],
  ['css', '/* Share the project accent. */\n:root {\n  --dockle-primary: #2962ff;\n}'],
  ['diff', '- framework = "native"\n+ framework = "dockle"'],
  ['dockerfile', 'FROM python:3.13\nRUN pip install dockle\nCMD ["dockle", "build"]'],
  ['http', 'GET /api/ HTTP/1.1\nHost: docs.example.com\nAccept: text/html'],
  ['ini', '[project]\nname=dockle\nenabled=true'],
  ['javascript', '// Build one target.\nconst target = "api";\nconst enabled = target !== "disabled";'],
  ['json', '{\n  "target": "api",\n  "enabled": true\n}'],
  ['makefile', 'target := api\n\nbuild:\n\tdockle build $(target)'],
  ['markdown', '# Dockle\n\nBuild **consistent** documentation with `dockle build`.'],
  ['plaintext', 'Dockle syntax preview\ntarget: api\nenabled: true'],
  ['powershell', '# Build one target.\n$target = "api"\ndockle build $target'],
  ['python', '# Build one target.\ntarget = "api"\nenabled = target != "disabled"'],
  ['rust', '// Build one target.\nlet target = "api";\nlet enabled = target != "disabled";'],
  ['scss', '// Share the project accent.\n$dockle-primary: #2962ff;\n.docs { color: $dockle-primary; }'],
  ['sql', '-- Find one target.\nSELECT name, framework\nFROM targets\nWHERE enabled = TRUE;'],
  ['toml', '# Configure one target.\n[[targets]]\nname = "api"\nenabled = true'],
  ['typescript', '// Build one target.\nconst target: string = "api";\nconst enabled: boolean = true;'],
  ['xml', '<!-- Link to generated documentation. -->\n<nav enabled="true">\n  <a href="/api/">API</a>\n</nav>'],
  ['yaml', '# Configure one target.\ntarget:\n  name: api\n  enabled: true'],
]);

const escapeHtml = (value) => value
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');

const languagePreview = (language) => samples.get(language) || [
  `# Dockle ${language} syntax preview`,
  'name = "dockle"',
  'enabled = true',
  'version = 1',
].join('\n');

const runtime = await readFile(runtimePath, 'utf8');
const context = { console };
context.globalThis = context;
context.window = context;
runInNewContext(runtime, context);

const languages = [...context.hljs.listLanguages()]
  .sort((left, right) => left.localeCompare(right));
const markdownLanguageEntries = (useNeutralFence) => languages.map((language) => {
  const definition = context.hljs.getLanguage(language);
  const aliases = definition.aliases || [];
  const aliasMarkup = aliases.length
    ? `<span>Aliases: ${aliases.map(escapeHtml).join(', ')}</span>`
    : '';
  return [
    '<div class="dockle-language-gallery-header">',
    `<strong>${escapeHtml(definition.name || language)}</strong>`,
    `<code>${escapeHtml(language)}</code>`,
    ...(aliasMarkup ? [aliasMarkup] : []),
    '</div>',
    '',
    `\`\`\`${useNeutralFence ? 'text' : language}`,
    languagePreview(language),
    '```',
  ].join('\n');
});

const markdownLanguageReference = (useNeutralFence) => [
  '## Language highlighting',
  '',
  'Every entry below is an actual fenced code block processed by this documentation',
  'framework before Dockle applies the shared highlighter. The list contains every',
  'canonical grammar bundled by the pinned Highlight.js dependency; aliases are',
  'shown beside the authoring identifier and are included by the filter.',
  '',
  '<div class="dockle-language-gallery"></div>',
  '',
  ...markdownLanguageEntries(useNeutralFence)
    .flatMap((entry) => [entry, '']),
  '<div class="dockle-language-gallery-end"></div>',
].join('\n');

const rstLanguageEntries = languages.map((language) => {
  const definition = context.hljs.getLanguage(language);
  const aliases = definition.aliases || [];
  const aliasesText = aliases.length
    ? ` <span>Aliases: ${aliases.map(escapeHtml).join(', ')}</span>`
    : '';
  const header = [
    '<div class="dockle-language-gallery-header">',
    `<strong>${escapeHtml(definition.name || language)}</strong> `,
    `<code>${escapeHtml(language)}</code>`,
    aliasesText,
    '</div>',
  ].join('');
  const preview = languagePreview(language)
    .split('\n')
    .map((line) => `   ${line}`)
    .join('\n');
  return [
    '.. raw:: html',
    '',
    `   ${header}`,
    '',
    '.. code-block:: text',
    `   :class: language-${language}`,
    '',
    preview,
  ].join('\n');
});

const rstLanguageReference = [
  'Language highlighting',
  '---------------------',
  '',
  'Every entry below is an actual reStructuredText code block processed by Sphinx before Dockle applies the shared',
  'highlighter. The list contains every canonical grammar bundled by the pinned Highlight.js dependency; aliases are',
  'shown beside the authoring identifier and are included by the filter.',
  '',
  '.. raw:: html',
  '',
  '   <div class="dockle-language-gallery"></div>',
  '',
  ...rstLanguageEntries.flatMap((entry) => [entry, '']),
  '.. raw:: html',
  '',
  '   <div class="dockle-language-gallery-end"></div>',
].join('\n');

const common = (await readFile(commonPath, 'utf8')).trim();
const banner = '<!-- Generated by npm run stage:examples; edit the .md.inc sources instead. -->';

await rm(stagedExamplesRoot, { force: true, recursive: true });
await mkdir(stagedExamplesRoot, { recursive: true });

for (const target of targets) {
  const stagedFrameworkRoot = path.join(
    stagedExamplesRoot,
    target.framework,
  );
  await cp(
    path.join(examplesRoot, target.framework),
    stagedFrameworkRoot,
    { recursive: true },
  );
  const sections = [banner, common];
  if (target.specific) {
    sections.push((await readFile(target.specific, 'utf8')).trim());
  }
  sections.push(
    markdownLanguageReference(target.useNeutralFence || false),
  );
  await writeFile(
    path.join(stagedFrameworkRoot, target.output),
    `${sections.join('\n\n')}\n`,
  );
}

const rstBasePath = path.join(
  examplesRoot,
  'sphinx',
  'component-reference-rst.rst.inc',
);
const rstOutputPath = path.join(
  stagedExamplesRoot,
  'sphinx',
  'component-reference-rst.rst',
);
const rstBase = (await readFile(rstBasePath, 'utf8')).trim();
await writeFile(
  rstOutputPath,
  `.. Generated by npm run stage:examples; edit the .rst.inc source instead.\n\n${rstBase}\n\n${rstLanguageReference}\n`,
);
