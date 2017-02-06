import fs from 'node:fs';
import path from 'node:path';
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf.mjs';

const [inputPdf, outputDir] = process.argv.slice(2);

if (!inputPdf || !outputDir) {
  console.error('Usage: node extract.mjs <input.pdf> <output-dir>');
  process.exit(2);
}

fs.mkdirSync(outputDir, { recursive: true });

const data = new Uint8Array(fs.readFileSync(inputPdf));
const pdf = await pdfjsLib.getDocument({
  data,
  disableFontFace: true,
  useSystemFonts: true,
  isEvalSupported: false,
}).promise;

const metadata = await pdf.getMetadata().catch((error) => ({ error: String(error) }));
const outline = await pdf.getOutline().catch((error) => ({ error: String(error) }));
const pages = [];

function normalizeWhitespace(value) {
  return value.replace(/\s+/g, ' ').trim();
}

function groupItemsIntoLines(items) {
  const groups = [];

  for (const item of items) {
    const text = normalizeWhitespace(item.str || '');
    if (!text) continue;

    const transform = item.transform || [0, 0, 0, 0, 0, 0];
    const x = transform[4] || 0;
    const y = transform[5] || 0;
    let group = groups.find((candidate) => Math.abs(candidate.y - y) <= 3);

    if (!group) {
      group = { y, items: [] };
      groups.push(group);
    }

    group.items.push({ x, text });
  }

  return groups
    .sort((a, b) => b.y - a.y)
    .map((group) =>
      group.items
        .sort((a, b) => a.x - b.x)
        .map((item) => item.text)
        .join(' ')
    )
    .filter(Boolean);
}

for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
  const page = await pdf.getPage(pageNumber);
  const viewport = page.getViewport({ scale: 1 });
  const content = await page.getTextContent({ includeMarkedContent: true });
  const lines = groupItemsIntoLines(content.items);
  const text = lines.join('\n');

  pages.push({
    pageNumber,
    width: viewport.width,
    height: viewport.height,
    itemCount: content.items.length,
    text,
  });
}

const baseName = path.basename(inputPdf, path.extname(inputPdf));
fs.writeFileSync(
  path.join(outputDir, `${baseName}.json`),
  JSON.stringify({ pageCount: pdf.numPages, metadata, outline, pages }, null, 2),
  'utf8'
);

fs.writeFileSync(
  path.join(outputDir, `${baseName}.txt`),
  pages
    .map((page) => [
      `===== PAGE ${page.pageNumber} / ${pdf.numPages} =====`,
      `size=${Math.round(page.width)}x${Math.round(page.height)} items=${page.itemCount}`,
      page.text,
    ].join('\n'))
    .join('\n\n'),
  'utf8'
);

console.log(`Extracted ${pdf.numPages} pages to ${outputDir}`);
