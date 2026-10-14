/*
 * Render any of the project's Markdown documents as a Word document.
 *
 *   node scripts/md_to_docx.js <input.md> <output.docx>
 *
 * The audit is regenerated from each run's export, so the Word version is
 * generated too rather than converted by hand. Nothing here adds content: it
 * is a renderer for the Markdown the Python generator produces.
 *
 * Author: Victoria Love Franklin - Developer, PhD Student, Data Science, Research Scholar
 * Copyright (c) 2026 Victoria Love Franklin. All rights reserved. See LICENSE.
 */
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, AlignmentType, PageOrientation, Tab,
  LevelFormat, ExternalHyperlink, Footer, PageNumber,
} = require("docx");

const NAVY = "14213A", WINE = "6E1F2B", GOLD = "C49A4A";
const INK = "1A1A1A", MUTED = "5A5F6A", RULE = "D8D8D8", BAND = "F2F0EB";

// US Letter, one-inch margins.
const PAGE_W = 12240, MARGIN = 1440;
const CONTENT_W = PAGE_W - MARGIN * 2;   // 9360 DXA

/* ---------- inline formatting ---------- */

// Split a line into runs, honouring **bold**, `code`, *italic* and [text](url).
function inline(text, base = {}) {
  const out = [];
  const re = /(\[([^\]]+)\]\(([^)]+)\))|(\*\*([^*]+)\*\*)|(`([^`]+)`)|(\*([^*]+)\*)/g;
  let last = 0, m;
  const push = (t, opts) => { if (t) out.push(new TextRun({ text: t, ...base, ...opts })); };
  while ((m = re.exec(text)) !== null) {
    push(text.slice(last, m.index));
    if (m[1]) {
      out.push(new ExternalHyperlink({
        link: m[3],
        children: [new TextRun({ text: m[2], ...base, style: "Hyperlink", color: "1D4F91", underline: {} })],
      }));
    } else if (m[4]) {
      // Recurse, so `code` and [links] inside **bold** keep their own styling
      // instead of being emitted with their markers intact.
      out.push(...inline(m[5], { ...base, bold: true }));
    } else if (m[6]) {
      push(m[7], { font: "Consolas", size: 18, color: WINE });
    } else if (m[8]) {
      out.push(...inline(m[9], { ...base, italics: true }));
    }
    last = re.lastIndex;
  }
  push(text.slice(last));
  return out.length ? out : [new TextRun({ text: "", ...base })];
}

const stripInline = (s) =>
  s.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/[*`]/g, "");

/* ---------- block helpers ---------- */

function para(text, opts = {}) {
  return new Paragraph({
    children: inline(text, opts.run || {}),
    spacing: { after: opts.after ?? 120, line: 276 },
    ...(opts.props || {}),
  });
}

function rule() {
  return new Paragraph({
    text: "",
    spacing: { before: 80, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE } },
  });
}

// A fenced block. One paragraph per source line so line breaks survive, with a
// tinted panel behind the whole run and no inline parsing of the contents.
function codeBlock(lines) {
  const edge = { style: BorderStyle.SINGLE, size: 4, color: RULE };
  return lines.map((text, idx) => new Paragraph({
    children: [new TextRun({ text: text || " ", font: "Consolas", size: 17, color: NAVY })],
    spacing: {
      before: idx === 0 ? 120 : 0,
      after: idx === lines.length - 1 ? 180 : 0,
      line: 240,
    },
    indent: { left: 180, right: 180 },
    shading: { type: ShadingType.CLEAR, fill: BAND },
    border: {
      left: edge,
      right: edge,
      ...(idx === 0 ? { top: edge } : {}),
      ...(idx === lines.length - 1 ? { bottom: edge } : {}),
    },
  }));
}

function quote(lines) {
  return new Paragraph({
    children: inline(lines.join(" ")),
    spacing: { before: 120, after: 160, line: 276 },
    indent: { left: 360 },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: GOLD, space: 12 } },
    shading: { type: ShadingType.CLEAR, fill: BAND },
  });
}

// Column widths: give the first column a little more room, the rest equal.
function widthsFor(n) {
  if (n === 1) return [CONTENT_W];
  const first = Math.round(CONTENT_W * (n <= 3 ? 0.34 : 0.26));
  const rest = Math.floor((CONTENT_W - first) / (n - 1));
  const w = [first, ...Array(n - 1).fill(rest)];
  w[n - 1] += CONTENT_W - w.reduce((a, b) => a + b, 0);  // absorb rounding
  return w;
}

function cell(text, width, { header = false } = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    margins: { top: 60, bottom: 60, left: 108, right: 108 },
    shading: header ? { type: ShadingType.CLEAR, fill: NAVY } : undefined,
    children: [new Paragraph({
      children: inline(text, header ? { bold: true, color: "FFFFFF", size: 18 } : { size: 18 }),
      spacing: { after: 0, line: 240 },
    })],
  });
}

function buildTable(rows) {
  const n = Math.max(...rows.map((r) => r.length));
  const widths = widthsFor(n);
  const pad = (r) => r.concat(Array(n - r.length).fill(""));
  const border = { style: BorderStyle.SINGLE, size: 2, color: RULE };
  return new Table({
    columnWidths: widths,
    width: { size: CONTENT_W, type: WidthType.DXA },
    borders: { top: border, bottom: border, left: border, right: border,
               insideHorizontal: border, insideVertical: border },
    rows: rows.map((r, i) => new TableRow({
      tableHeader: i === 0,
      children: pad(r).map((c, j) => cell(c, widths[j], { header: i === 0 })),
    })),
  });
}


// List items are laid out as a borderless two-column table rather than with a
// hanging indent: LibreOffice honours w:hanging for the first line but drops
// w:left on wrapped lines, which pushed continuation text back to the margin.
// A cell boundary cannot be ignored that way.
const MARKER_W = 340;
function listTable(items) {
  const textW = CONTENT_W - MARKER_W;
  const cellOpts = { margins: { top: 0, bottom: 0, left: 0, right: 0 } };
  const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return new Table({
    columnWidths: [MARKER_W, textW],
    width: { size: CONTENT_W, type: WidthType.DXA },
    borders: { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder,
               insideHorizontal: noBorder, insideVertical: noBorder },
    rows: items.map(it => new TableRow({ children: [
      new TableCell({ ...cellOpts, width: { size: MARKER_W, type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: it.marker })],
                                   spacing: { after: 90, line: 276 } })] }),
      new TableCell({ ...cellOpts, width: { size: textW, type: WidthType.DXA },
        children: [new Paragraph({ children: inline(it.text),
                                   spacing: { after: 90, line: 276 } })] }),
    ]})),
  });
}

/* ---------- markdown walk ---------- */

function convert(md) {
  const lines = md.split("\n");
  const body = [];
  let i = 0, para_buf = [], quote_buf = [], list_buf = [];

  const flushPara = () => {
    if (para_buf.length) { body.push(para(para_buf.join(" "))); para_buf = []; }
  };
  const flushQuote = () => {
    if (quote_buf.length) { body.push(quote(quote_buf)); quote_buf = []; }
  };
  const flushList = () => {
    if (list_buf.length) { body.push(listTable(list_buf)); list_buf = []; }
  };
  const flushAll = () => { flushPara(); flushQuote(); flushList(); };

  while (i < lines.length) {
    const line = lines[i];
    const t = line.trim();

    // Fenced code block. Taken verbatim, before anything else can claim the
    // lines: a fence may hold pipes, hashes and hyphens that otherwise read as
    // tables, headings or rules.
    if (t.startsWith("```")) {
      flushAll();
      const buf = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        buf.push(lines[i].replace(/\s+$/, ""));
        i++;
      }
      i++;  // closing fence
      while (buf.length && buf[buf.length - 1] === "") buf.pop();
      if (buf.length) body.push(...codeBlock(buf));
      continue;
    }

    if (t === "") { flushAll(); i++; continue; }

    if (/^---+$/.test(t)) { flushAll(); body.push(rule()); i++; continue; }

    if (t.startsWith("> ")) { flushPara(); quote_buf.push(t.slice(2)); i++; continue; }

    // Headings
    const h = t.match(/^(#{1,3})\s+(.*)$/);
    if (h) {
      flushAll();
      const level = h[1].length, text = h[2];
      if (level === 1) {
        body.push(new Paragraph({
          children: inline(text, { bold: true, size: 44, color: NAVY }),
          spacing: { after: 160 },
        }));
      } else {
        body.push(new Paragraph({
          children: inline(text, {
            bold: true,
            size: level === 2 ? 30 : 24,
            color: level === 2 ? NAVY : WINE,
          }),
          heading: level === 2 ? HeadingLevel.HEADING_1 : HeadingLevel.HEADING_2,
          spacing: { before: level === 2 ? 320 : 240, after: 120 },
          ...(level === 2
            ? { border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: GOLD, space: 6 } } }
            : {}),
        }));
      }
      i++; continue;
    }

    // Tables
    if (t.startsWith("|") && i + 1 < lines.length && /^\|[\s:\-|]+\|$/.test(lines[i + 1].trim())) {
      flushAll();
      const cells = (row) => row.trim().replace(/^\|/, "").replace(/\|$/, "")
        .split("|").map((c) => c.trim());
      const rows = [cells(lines[i])];
      i += 2;
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        rows.push(cells(lines[i])); i++;
      }
      body.push(buildTable(rows));
      body.push(new Paragraph({ text: "", spacing: { after: 160 } }));
      continue;
    }

    // Bullets
    const b = t.match(/^[-*]\s+(.*)$/);
    if (b) {
      flushPara(); flushQuote();
      list_buf.push({ marker: "\u2022", text: b[1] });
      i++; continue;
    }

    // Ordered list
    const o = t.match(/^(\d+)\.\s+(.*)$/);
    if (o) {
      flushPara(); flushQuote();
      list_buf.push({ marker: `${o[1]}.`, text: o[2] });
      i++; continue;
    }

    // A wrapped source line belongs to the list item above it, if there is
    // one; a blank line closes the list, so this cannot swallow later prose.
    if (list_buf.length) { list_buf[list_buf.length - 1].text += " " + t; i++; continue; }
    para_buf.push(t);
    i++;
  }
  flushAll();
  return body;
}

/* ---------- document ---------- */

const AUTHOR = "Victoria Love Franklin";

function main(inPath, outPath) {
  const md = fs.readFileSync(inPath, "utf8");
  // The running head and the file's own metadata come from the document's H1,
  // so this converter renders any of the project's documents unchanged.
  const h1 = md.match(/^#\s+(.+)$/m);
  const docTitle = (h1 ? h1[1] : "NWGS Grid").replace(/\s*[—–]\s*/g, " - ").trim();
  const children = convert(md);

  const doc = new Document({
    creator: AUTHOR,
    lastModifiedBy: AUTHOR,
    title: docTitle,
    description: `${docTitle}. Generated from the repository and from a weekly run's export.`,
    styles: {
      default: { document: { run: { font: "Calibri", size: 21, color: INK } } },
    },
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [{
            level: 0, format: LevelFormat.BULLET, text: "\u2022",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 420, hanging: 220 } } },
          }],
        },
        {
          reference: "steps",
          levels: [{
            level: 0, format: LevelFormat.DECIMAL, text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 420, hanging: 220 } } },
          }],
        },
      ],
    },
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_W, height: 15840, orientation: PageOrientation.PORTRAIT },
          margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
        },
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({
              children: [`${docTitle}    |    `, PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES],
              size: 16, color: MUTED,
            })],
          })],
        }),
      },
      children,
    }],
  });

  return Packer.toBuffer(doc).then((buf) => {
    fs.writeFileSync(outPath, buf);
    console.log(`Wrote ${outPath} (${(buf.length / 1024).toFixed(1)} KB)`);
  });
}

if (require.main === module) {
  const [, , inPath, outPath] = process.argv;
  if (!inPath || !outPath) {
    console.error("usage: node scripts/audit_to_docx.js <input.md> <output.docx>");
    process.exit(1);
  }
  main(inPath, outPath).catch((e) => { console.error(e); process.exit(1); });
}
