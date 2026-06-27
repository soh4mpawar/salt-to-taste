const { createCanvas } = require("canvas");
const fs = require("fs");
const path = require("path");

function generateIcon(size) {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext("2d");

  // Orange background
  ctx.fillStyle = "#ff9500";
  ctx.beginPath();
  ctx.roundRect(0, 0, size, size, size * 0.2);
  ctx.fill();

  // Salt shaker emoji-style shape
  ctx.fillStyle = "white";
  const cx = size / 2, cy = size / 2;
  const r = size * 0.28;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.fill();

  // Salt dots
  ctx.fillStyle = "#ff9500";
  [[-0.1, -0.1], [0.1, -0.1], [0, 0.1]].forEach(([dx, dy]) => {
    ctx.beginPath();
    ctx.arc(cx + dx * size, cy + dy * size, size * 0.04, 0, Math.PI * 2);
    ctx.fill();
  });

  return canvas.toBuffer("image/png");
}

const publicDir = path.join(__dirname, "../public");
if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
}

fs.writeFileSync(path.join(publicDir, "icon-192.png"), generateIcon(192));
fs.writeFileSync(path.join(publicDir, "icon-512.png"), generateIcon(512));
console.log("Icons generated");
