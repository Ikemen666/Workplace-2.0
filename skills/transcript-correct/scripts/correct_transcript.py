#!/usr/bin/env python3
"""
correct_transcript.py — deterministic first pass for transcript-correct.

Does ONLY the safe, mechanical part:
  1. applies the explicit replacements map from glossary.json (known ASR errors -> right)
  2. emits the canonical proper-noun list so the downstream LLM pass knows what to snap to

It does NOT remove 口癖 / 顺句 / guess names — that is the LLM pass (see SKILL.md),
because those need context judgement. Keeping the mechanical part separate makes it
auditable and reversible.

Usage:
    python3 correct_transcript.py <transcript.txt> [--glossary path] [-o out.txt]

If -o is omitted, writes <transcript>.corrected.txt next to the input and prints a
JSON report (counts + canonical list) to stdout.
"""
import argparse, json, os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
DICTS_DIR = os.path.join(HERE, "..", "references", "dicts")
DEFAULT_GLOSSARY = os.path.join(DICTS_DIR, "general.json")  # always-loaded safe base


def _load_one(path):
    with open(path, "r", encoding="utf-8") as f:
        g = json.load(f)
    reps = {k: v for k, v in g.get("replacements", {}).items() if not k.startswith("_")}
    wordbound = {k: v for k, v in g.get("replacements_wordbound", {}).items() if not k.startswith("_")}
    canon = g.get("canonical", {})
    fillers = g.get("fillers", {})
    protect = [p for p in g.get("protect", []) if not p.startswith("_")]
    return reps, canon, fillers, protect, wordbound


def resolve_dict_paths(domain, glossary):
    """Routing: general.json is ALWAYS loaded first (safe base). --domain adds one or
    more domain dicts by filename stem (comma-separated). --glossary overrides with an
    explicit comma-separated list of paths (general still prepended unless a path is given
    for it)."""
    if glossary:
        return [p.strip() for p in glossary.split(",") if p.strip()]
    paths = [os.path.join(DICTS_DIR, "general.json")]
    if domain:
        for d in domain.split(","):
            d = d.strip()
            if not d or d == "general":
                continue
            paths.append(os.path.join(DICTS_DIR, d + ".json"))
    return paths


def load_glossary(paths):
    """Load and MERGE one or more dict files (later files extend/override earlier)."""
    if isinstance(paths, str):
        paths = [paths]
    reps, wordbound, protect = {}, {}, []
    canon = {"people": [], "orgs": [], "terms": []}
    fillers = {}
    for p in paths:
        if not os.path.exists(p):
            sys.exit("dict not found: " + p + " (check --domain name / dicts/ folder)")
        r, c, f, pr, wb = _load_one(p)
        reps.update(r); wordbound.update(wb); protect.extend(pr)
        if f:
            fillers = f  # fillers live in general; last non-empty wins
        for key in ("people", "orgs", "terms"):
            for x in c.get(key, []):
                if x not in canon[key]:
                    canon[key].append(x)
    return reps, canon, fillers, protect, wordbound


# A transcript content line is everything that is NOT a "说话人 N HH:MM:SS.mmm" header
SPEAKER_HEADER = re.compile(r"^\s*说话人\s*\S+\s+[\d:.]+\s*$")


def strip_fillers(text, fillers):
    """Conservative 口癖 removal. Only touches content lines, never speaker headers.
    Returns (text, stats)."""
    standalone = set(fillers.get("standalone_interjections", []))
    lead = fillers.get("lead_interjections", [])
    pairs = fillers.get("collapse_pairs", {})
    stats = {"lines_dropped": 0, "lead_removed": 0, "pairs_collapsed": 0}

    lead_re = re.compile(r"^(" + "|".join(re.escape(t) for t in lead) + r")[，,]\s*") if lead else None
    # bare-interjection line: only interjection chars + punctuation/space
    bare_re = re.compile(r"^[" + "".join(standalone) + r"，,。.！!？?、\s]+$") if standalone else None

    out = []
    for line in text.split("\n"):
        if SPEAKER_HEADER.match(line) or line.strip() == "":
            out.append(line)
            continue
        s = line
        # 1) collapse explicit stutter/echo pairs (longest first)
        for k in sorted(pairs, key=len, reverse=True):
            if k in s:
                stats["pairs_collapsed"] += s.count(k)
                s = s.replace(k, pairs[k])
        # 2) drop the line if it is now purely a bare interjection
        if bare_re and bare_re.match(s) and not re.search(r"[对好行]", s):
            stats["lines_dropped"] += 1
            continue
        # 3) strip a leading interjection + comma
        if lead_re:
            s2 = lead_re.sub("", s)
            if s2 != s:
                stats["lead_removed"] += 1
                s = s2
        out.append(s)
    return "\n".join(out), stats


def apply_replacements(text, reps, protect=None, wordbound=None):
    """Apply wrong->right replacements.
    - `reps`: naive substring replacement (longest key first).
    - `wordbound`: Latin-acronym replacement matched ONLY at word boundaries (not flanked
      by [A-Za-z0-9]), so e.g. 'AB'->'A/B' never touches 'ABC'/'ABORT'.
    - `protect`: phrases masked before any replacement and restored after (e.g. an idiom
      that happens to contain a person's name as a substring): a whole-word guard for Chinese collisions."""
    counts = {}
    masks = {}
    for i, ph in enumerate(sorted(set(protect or []), key=len, reverse=True)):
        if ph and ph in text:
            token = "%d" % i  # PUA sentinels: cannot appear in real text or keys
            masks[token] = ph
            text = text.replace(ph, token)
    # longest keys first so a longer wrong-phrase wins over a contained shorter one
    for wrong in sorted(reps, key=len, reverse=True):
        right = reps[wrong]
        n = text.count(wrong)
        if n:
            text = text.replace(wrong, right)
            counts[wrong + " -> " + right] = n
    for wrong in sorted(wordbound or {}, key=len, reverse=True):
        right = wordbound[wrong]
        pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(wrong) + r"(?![A-Za-z0-9])")
        text, n = pat.subn(right, text)
        if n:
            counts[wrong + " -> " + right + " (wb)"] = n
    for token, ph in masks.items():
        text = text.replace(token, ph)
    return text, counts


def chunk_on_speaker_boundaries(text, max_chars):
    """Split into ordered chunks at blank-line/speaker boundaries, NEVER mid-utterance.
    A 'block' is a run of lines between blank lines (header + its content). Greedily
    pack whole blocks into a chunk until max_chars, then start a new chunk."""
    blocks = re.split(r"\n\s*\n", text.strip())
    chunks, cur, cur_len = [], [], 0
    for b in blocks:
        b = b.strip("\n")
        if not b:
            continue
        if cur and cur_len + len(b) > max_chars:
            chunks.append("\n\n".join(cur))
            cur, cur_len = [], 0
        cur.append(b)
        cur_len += len(b) + 2
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks


def write_chunks(chunks, chunk_dir):
    os.makedirs(chunk_dir, exist_ok=True)
    # CRITICAL: clear stale chunks from a previous transcript first. Otherwise a later,
    # shorter transcript leaves the previous run's higher-numbered chunk_NNN(.clean).txt
    # behind, and --merge (which globs the dir) would splice two transcripts together.
    for f in os.listdir(chunk_dir):
        if re.match(r"chunk_\d+(\.clean)?\.txt$", f):
            os.remove(os.path.join(chunk_dir, f))
    paths = []
    for i, c in enumerate(chunks, 1):
        p = os.path.join(chunk_dir, "chunk_%03d.txt" % i)
        with open(p, "w", encoding="utf-8") as f:
            f.write(c)
        paths.append(p)
    return paths


# speaker label without the trailing timestamp, e.g. "说话人 2 00:11:29.640" -> "说话人 2"
SPEAKER_LABEL = re.compile(r"^(\s*说话人\s*\S+?)\s+[\d:.]+\s*$")


def sanitize_escapes(text):
    """Defensive: upstream code-driven passes sometimes write LITERAL escape sequences
    (the two chars backslash+n) instead of real newlines. Turn them back into real
    whitespace so they never show up as '\\n' in the rendered doc."""
    return (text.replace("\\r\\n", "\n").replace("\\n", "\n")
                .replace("\\t", " ").replace("\\r", "\n"))


def _xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _docx_paragraph(text, bold=False):
    font = "黑体" if bold else "宋体"
    rpr = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="%s"/>'
           '%s<w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>') % (font, "<w:b/>" if bold else "")
    ppr = '<w:pPr><w:spacing w:before="%d" w:after="20"/></w:pPr>' % (100 if bold else 0)
    return ('<w:p>%s<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p>'
            % (ppr, rpr, _xml_escape(text)))


# A minimal, valid OOXML .docx written with ONLY the Python stdlib (zipfile) — no
# python-docx, no pandoc/textutil. Works in any environment that has Python.
_CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '</Types>')
_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '</Relationships>')


def render_transcript_docx(text, path, keep_timestamps=False):
    """Render a cleaned transcript into a .docx (说话人 lines bold, content as paragraphs).
    Timestamps stripped by default. Pure stdlib — builds the OOXML zip directly so it works
    even where python-docx / pandoc / textutil are unavailable."""
    import zipfile

    text = sanitize_escapes(text)
    if not keep_timestamps:
        # strip the wall-clock from a leading "YYYY-MM-DD HH:MM:SS CST|..." meta line too
        text = re.sub(r"(?m)^(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}(?:\s+[A-Z]{2,4})?", r"\1", text)

    paras = []
    for line in text.split("\n"):
        s = line.rstrip()
        if s == "":
            continue
        m = SPEAKER_LABEL.match(s)
        if m or SPEAKER_HEADER.match(s):
            label = s if keep_timestamps else (m.group(1).strip() if m else s)
            paras.append(_docx_paragraph(label, bold=True))
        else:
            paras.append(_docx_paragraph(s, bold=False))

    document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>' + "".join(paras) + '<w:sectPr/></w:body></w:document>')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CONTENT_TYPES)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("word/document.xml", document)


def sanitize_filename(name):
    """Make a title safe as a filename: drop path separators and illegal chars, trim."""
    name = re.sub(r'[\\/:*?"<>|\n\r\t]', " ", name).strip()
    name = re.sub(r"\s+", " ", name)
    return name[:120] or "transcript"


def apply_title(out, title):
    """If a title is given, replace the output filename's stem with the sanitized title,
    keeping the same directory and extension."""
    if not title:
        return out
    d = os.path.dirname(out)
    ext = os.path.splitext(out)[1] or ".docx"
    return os.path.join(d, sanitize_filename(title) + ext)


def write_final(text, out, keep_timestamps=False):
    """Write final text to .txt or .docx depending on the -o extension."""
    if out.lower().endswith(".docx"):
        render_transcript_docx(text, out, keep_timestamps=keep_timestamps)
    else:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text if text.endswith("\n") else text + "\n")


def merge_clean_chunks(chunk_dir, out, keep_timestamps=False):
    """Concatenate cleaned chunks (chunk_NNN.clean.txt) back in order, write txt or docx.
    Only merges clean chunks that have a matching source chunk_NNN.txt — this stops a
    leftover .clean.txt from a previous (longer) transcript getting spliced in."""
    listing = os.listdir(chunk_dir)
    sources = set()
    for f in listing:
        mm = re.match(r"(chunk_\d+)\.txt$", f)
        if mm:
            sources.add(mm.group(1))
    all_clean = sorted(f for f in listing if re.match(r"chunk_\d+\.clean\.txt$", f))
    files = [f for f in all_clean if f[:-len(".clean.txt")] in sources]
    orphans = [f for f in all_clean if f not in files]
    if not files:
        sys.exit("no chunk_NNN.clean.txt with a matching source chunk in " + chunk_dir)
    missing = sorted(s + ".clean.txt" for s in sources
                     if (s + ".clean.txt") not in set(all_clean))
    parts = []
    for f in files:
        with open(os.path.join(chunk_dir, f), "r", encoding="utf-8") as fh:
            parts.append(sanitize_escapes(fh.read()).strip("\n"))
    write_final("\n\n".join(parts), out, keep_timestamps=keep_timestamps)
    report = {"merged_from": files, "output": out, "chunks": len(files),
              "format": "docx" if out.lower().endswith(".docx") else "txt"}
    if orphans:
        report["ignored_orphan_clean_chunks"] = orphans  # stale leftovers — NOT merged
    if missing:
        report["WARNING_unclean_source_chunks"] = missing  # a chunk was never cleaned!
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?",
                    help="raw transcript file; omit when using --merge")
    ap.add_argument("--domain", default="",
                    help="which domain dict(s) to load on top of general.json, by filename stem, comma-separated. e.g. --domain my-project | my-project,another. Omit = general only (safe for any meeting).")
    ap.add_argument("--glossary", default="",
                    help="override: explicit comma-separated dict path(s) to load instead of the --domain routing")
    ap.add_argument("--strip-fillers", action="store_true",
                    help="also do the conservative 口癖 pass (collapse stutters, drop bare interjections)")
    ap.add_argument("--no-replace", action="store_true",
                    help="skip ALL glossary replacements (the dict may be domain-specific to a project; use this for unrelated meetings to avoid over-correction like a generic 'can' -> a name)")
    ap.add_argument("--chunk-chars", type=int, default=0,
                    help="if >0, also split the cleaned text into ordered chunk files of ~this size, on speaker boundaries (for parallel per-chunk LLM cleaning)")
    ap.add_argument("--chunk-dir", default="/tmp/tc_chunks",
                    help="where to write chunk_NNN.txt (and read back chunk_NNN.clean.txt for --merge)")
    ap.add_argument("--merge", action="store_true",
                    help="merge mode: concat chunk_NNN.clean.txt from --chunk-dir into -o, then exit")
    ap.add_argument("--to-docx", action="store_true",
                    help="render mode: convert an already-cleaned transcript (input) into -o (.docx), then exit")
    ap.add_argument("--keep-timestamps", action="store_true",
                    help="keep the HH:MM:SS timestamp on each 说话人 line in the .docx (default: strip)")
    ap.add_argument("--title", default="",
                    help="name the output file after this title (e.g. the 飞书妙记 title), sanitized; dir+ext kept")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    if args.merge:
        if not args.output:
            sys.exit("--merge requires -o OUTPUT (.txt or .docx)")
        out = apply_title(args.output, args.title)
        merge_clean_chunks(args.chunk_dir, out, keep_timestamps=args.keep_timestamps)
        return
    if args.to_docx:
        if not args.input or not args.output:
            sys.exit("--to-docx requires INPUT and -o OUTPUT.docx")
        out = apply_title(args.output, args.title)
        with open(args.input, "r", encoding="utf-8") as f:
            render_transcript_docx(f.read(), out, keep_timestamps=args.keep_timestamps)
        print(json.dumps({"rendered": out, "from": args.input}, ensure_ascii=False))
        return
    if not args.input:
        sys.exit("input is required (unless --merge)")

    if not os.path.exists(args.input):
        sys.exit("input not found: " + args.input)

    reps, canon, fillers, protect, wordbound = load_glossary(resolve_dict_paths(args.domain, args.glossary))
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    if args.no_replace:
        counts = {}
    else:
        text, counts = apply_replacements(text, reps, protect, wordbound)
    filler_stats = {}
    if args.strip_fillers:
        text, filler_stats = strip_fillers(text, fillers)

    out = args.output or re.sub(r"\.txt$", "", args.input) + ".corrected.txt"
    out = apply_title(out, args.title)
    write_final(text, out, keep_timestamps=args.keep_timestamps)

    chunk_info = {}
    if args.chunk_chars > 0:
        chunks = chunk_on_speaker_boundaries(text, args.chunk_chars)
        paths = write_chunks(chunks, args.chunk_dir)
        chunk_info = {
            "chunk_dir": args.chunk_dir,
            "chunk_count": len(paths),
            "chunk_files": paths,
            "chunk_pass2": "Clean each chunk_NNN.txt in PARALLEL (one subagent each) -> write chunk_NNN.clean.txt in the same dir, then run this script with --merge --chunk-dir <dir> -o FINAL. This avoids the single-output token cap on long transcripts.",
        }

    report = {
        "input": args.input,
        "output": out,
        "replacements_applied": counts,
        "total_replacements": sum(counts.values()),
        "filler_stats": filler_stats,
        "canonical_people": canon.get("people", []),
        "canonical_orgs": canon.get("orgs", []),
        "canonical_terms": canon.get("terms", []),
        "chunking": chunk_info,
        "next_step": "Hand `output` (or the chunk files) to the LLM pass per SKILL.md: remove 口癖/填充词, light 顺句, snap names to canonical_people, mark uncertain with [?].",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
