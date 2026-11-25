// Entry point for the make.fun "Sum up 25 November's world news in one
// image" bounty (news-image-20261125).
//
// The judged picture is entry.png, stored beside this file. This script
// does nothing creative: it places an exact copy of that picture into the
// directory the harness asks for, then reads the copy back and checks it
// is byte-identical to the source and still a 1024x1024 PNG under 1 MiB,
// so a bad copy can never pass silently.
//
// Run it with:  node main.ts
//   MAKEFUN_OUTPUT_DIR   folder that receives entry.png (default /output)
//   MAKEFUN_BOT_DIR      folder holding entry.png (default: this file's folder)

import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const botDir = process.env.MAKEFUN_BOT_DIR ?? dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const source = join(botDir, "entry.png");
const destination = join(outDir, "entry.png");

if (!existsSync(source)) {
  throw new Error(`entry.png not found in ${botDir}`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, destination);

const original = readFileSync(source);
const written = readFileSync(destination);
if (!written.equals(original)) {
  throw new Error(`copied ${destination} differs from ${source}`);
}
if (written.length > 1024 * 1024) {
  throw new Error(`entry.png is ${written.length} bytes, over the 1 MiB cap`);
}
const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!written.subarray(0, 8).equals(pngMagic)) {
  throw new Error("entry.png is not a PNG file");
}
const width = written.readUInt32BE(16);
const height = written.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}

console.log(`entry.png -> ${destination} (${written.length} bytes, 1024x1024 PNG, verified byte-identical)`);
