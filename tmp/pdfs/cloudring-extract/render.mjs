import fs from 'node:fs';
import path from 'node:path';
import { createCanvas } from '@napi-rs/canvas';
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf.mjs';

const [inputPdf, outputDir] = process.argv.slice(2);

if (!inputPdf || !outputDir) {
  console.error('Usage: node render.mjs <input.pdf> <output-dir>');
  process.exit(2);
}

fs.mkdirSync(outputDir, { recursive: true });

const data = new Uint8Array(fs.readFileSync(inputPdf));
const pdf = await pdfjsLib.getDocument({
  data,
  disableFontFace: false,
  useSystemFonts: true,
  isEvalSupported: false,
}).promise;

for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
  const page = await pdf.getPage(pageNumber);
  const viewport = page.getViewport({ scale: 1.5 });
  const canvas = createCanvas(Math.ceil(viewport.width), Math.ceil(viewport.height));
  const context = canvas.getContext('2d');

  await page.render({
    canvasContext: context,
    viewport,
    canvas,
  }).promise;

  const outputPath = path.join(outputDir, `page-${String(pageNumber).padStart(2, '0')}.png`);
  fs.writeFileSync(outputPath, canvas.toBuffer('image/png'));
  console.log(outputPath);
}
