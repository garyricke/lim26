#!/usr/bin/env python3
"""
Extract all visible copy from the LIM 2026 site for client review.

Output:
  - site-copy.md  : human-readable doc with stable IDs (for the client / Google Docs)
  - site-copy.map.json : sidecar mapping ID -> {file, css_path, text, line_hint}
                         used to round-trip edits back into source.
"""
import json, re, os, sys
from bs4 import BeautifulSoup, NavigableString, Tag

REPO = "/Users/garyricke/Documents/lim2026"

PAGES = [
    ("index.html",                              "idx", "Homepage"),
    ("about.html",                              "abt", "About LIM"),
    ("healing-groups.html",                     "hgs", "Healing Groups"),
    ("blog-i-can-do-all-things.html",           "bph", "Blog: I Can Do All Things (Philippians)"),
    ("blog-the-choice.html",                    "bch", "Blog: The Choice"),
    ("blog-discovering-identity-bev.html",      "bbv", "Blog: Discovering Identity (Bev)"),
    ("healing-group-military-march2026.html",   "bmm", "Blog: Military Healing Group (March 2026)"),
]

SKIP_TAGS = {"script", "style", "noscript", "svg", "path", "head", "meta", "link", "br", "hr", "source", "track"}

# Tags whose direct text we collect as a single block.
# We group leaf-level text content by their nearest "block" ancestor so it reads naturally.
BLOCK_TAGS = {"h1","h2","h3","h4","h5","h6","p","li","button","label","figcaption","summary","blockquote","dt","dd","caption","th","td","option"}

# Inline tags whose text gets folded into the surrounding block.
INLINE_TAGS = {"a","span","strong","em","b","i","u","small","mark","sub","sup","abbr","cite","code","kbd","samp","time","var","q","s","del","ins"}

def get_section_label(node):
    """Find a stable section name for a node by walking up to the nearest section/header/footer/main with id or aria-label."""
    cur = node
    while cur is not None and isinstance(cur, Tag):
        if cur.name in ("section","header","footer","main","nav","aside","article","dialog"):
            label = cur.get("aria-label") or cur.get("id") or cur.name
            return f"{cur.name}#{label}"
        # treat divs that look like modals (role=dialog or id starts with m-) as their own section
        if cur.name == "div":
            elid = cur.get("id") or ""
            role = cur.get("role") or ""
            if role == "dialog" or elid.startswith("m-"):
                label = cur.get("aria-label") or elid or "modal"
                return f"modal#{label}"
        cur = cur.parent
    return "(other)#other"

def css_path(node):
    """Build a short CSS-ish path for round-tripping."""
    parts = []
    cur = node
    while isinstance(cur, Tag) and cur.name != "[document]":
        seg = cur.name
        if cur.get("id"):
            seg += f"#{cur['id']}"
            parts.insert(0, seg)
            break
        cls = cur.get("class")
        if cls:
            seg += "." + ".".join(cls[:2])
        # add nth-of-type so we can disambiguate
        if cur.parent and isinstance(cur.parent, Tag):
            sibs = [s for s in cur.parent.find_all(cur.name, recursive=False)]
            if len(sibs) > 1:
                idx = sibs.index(cur) + 1
                seg += f":nth-of-type({idx})"
        parts.insert(0, seg)
        cur = cur.parent
    return " > ".join(parts)

def collect_text(node):
    """Get text of a block, folding in inline children, normalizing whitespace."""
    parts = []
    for child in node.descendants:
        if isinstance(child, NavigableString):
            par = child.parent
            if par and par.name in SKIP_TAGS:
                continue
            t = str(child)
            if t.strip():
                parts.append(t)
    txt = " ".join(parts)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def is_block_with_text(node):
    if not isinstance(node, Tag):
        return False
    if node.name in SKIP_TAGS:
        return False
    if node.name in BLOCK_TAGS:
        return True
    # treat <a> as a block when it's a CTA button or a nav link (not when it's an inline link inside a paragraph)
    if node.name == "a":
        cls = " ".join(node.get("class") or [])
        if "btn" in cls or "nav-link" in cls or "drop-link" in cls or "dropdown" in cls:
            return True
        # nav links: anchor whose ancestor is a <nav> or whose parent is <li>
        par = node.parent
        if par and isinstance(par, Tag) and par.name in ("li","nav"):
            return True
        anc = node.find_parent("nav")
        if anc:
            return True
    return False

def find_line_hint(haystack_lines, needle, start_at=0):
    if not needle:
        return None
    snippet = needle[:60]
    for i in range(start_at, len(haystack_lines)):
        if snippet in haystack_lines[i]:
            return i + 1
    return None

def slug_section(label):
    # turn "section#hero" into "hero"
    s = label.split("#",1)[-1]
    s = re.sub(r"[^a-zA-Z0-9]+","-", s).strip("-").lower()
    return s or "section"

def extract_page(path, slug, title):
    html = open(os.path.join(REPO, path), encoding="utf-8").read()
    lines = html.splitlines()
    soup = BeautifulSoup(html, "html.parser")

    doc_title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    meta_desc = ""
    md = soup.find("meta", attrs={"name":"description"})
    if md and md.get("content"):
        meta_desc = md["content"].strip()
    og_title = ""
    ot = soup.find("meta", attrs={"property":"og:title"})
    if ot and ot.get("content"):
        og_title = ot["content"].strip()
    og_desc = ""
    od = soup.find("meta", attrs={"property":"og:description"})
    if od and od.get("content"):
        og_desc = od["content"].strip()

    # remove script/style entirely
    for t in soup(SKIP_TAGS):
        t.decompose()

    body = soup.body or soup

    # Walk in order; for each block element with text, emit a record.
    seen_ids = set()
    records = []
    counter = 0
    cursor_line = 0

    for el in body.descendants:
        # also capture form input placeholders/values as copy
        if isinstance(el, Tag) and el.name in ("input","textarea","select") and (el.get("placeholder") or (el.name=="input" and el.get("type") in ("submit","button") and el.get("value"))):
            text = el.get("placeholder") or el.get("value") or ""
            text = re.sub(r"\s+"," ", text).strip()
            if not text:
                continue
            section_label = get_section_label(el)
            counter += 1
            cid = f"{slug}-{counter:03d}"
            records.append({
                "id": cid, "tag": "input-placeholder" if el.get("placeholder") else "input-value",
                "section": section_label, "section_slug": slug_section(section_label),
                "text": text, "css": css_path(el),
                "line": find_line_hint(lines, text, cursor_line),
            })
            continue

        if not is_block_with_text(el):
            continue
        # skip if a parent block is also a block (e.g., li > p) — keep the deeper one if it has more text? simpler: emit both? we'll emit only if no ancestor in BLOCK_TAGS up to nearest section
        # Actually, the cleanest: emit a block only if no ancestor element (until <section>/<header>/<footer>/<main>/<aside>/<article>) is also a block_tag with the SAME text.
        text = collect_text(el)
        if not text:
            continue
        # filter out blocks whose entire text is duplicated by child blocks
        # (we emit children separately). Use is_block_with_text() so we also
        # consider promoted <a> tags as children.
        child_blocks_text = []
        for c in el.find_all(True, recursive=True):
            if c is el: continue
            if is_block_with_text(c):
                ct = collect_text(c)
                if ct: child_blocks_text.append(ct)
        if child_blocks_text:
            joined_children = " ".join(child_blocks_text)
            joined_children_norm = re.sub(r"\s+"," ", joined_children).strip()
            if joined_children_norm == text:
                continue

        section_label = get_section_label(el)
        counter += 1
        cid = f"{slug}-{counter:03d}"
        seen_ids.add(cid)

        line_hint = find_line_hint(lines, text, cursor_line)
        if line_hint:
            cursor_line = line_hint  # roughly forward-only

        records.append({
            "id": cid,
            "tag": el.name,
            "section": section_label,
            "section_slug": slug_section(section_label),
            "text": text,
            "css": css_path(el),
            "line": line_hint,
        })

    return {"path": path, "slug": slug, "title": title, "doc_title": doc_title,
            "meta_desc": meta_desc, "og_title": og_title, "og_desc": og_desc, "records": records}

def render_md(pages):
    out = []
    out.append("# LIM 2026 — Site Copy for Review\n")
    out.append("This document contains all customer-facing copy for the new site, organized page by page and section by section.\n")
    out.append("## How to make edits\n")
    out.append("1. **Do NOT change anything inside square brackets** like `[idx-001]`. These are stable IDs that let us locate each piece of copy back in the source code.\n")
    out.append("2. To edit a line, change the text *after* the ID. Keep the ID exactly as it is.\n")
    out.append("3. To delete a line, leave the ID in place and write `[DELETE]` after it (or strike it through in Google Docs with track changes on).\n")
    out.append("4. To add a new line in a section, add it where you want and write `[NEW]` at the start. We'll insert it.\n")
    out.append("5. When done, send the doc back and we'll apply every change to the live site.\n")
    out.append("\n---\n")

    # table of contents
    out.append("## Table of Contents\n")
    for p in pages:
        anchor = re.sub(r"[^a-z0-9]+","-", p["title"].lower()).strip("-")
        out.append(f"- [{p['title']}](#{anchor})")
    out.append("")

    for p in pages:
        out.append(f"\n---\n\n## {p['title']}\n")
        out.append(f"_File: `{p['path']}`_\n")
        out.append(f"\n### SEO & Browser\n")
        if p['doc_title']:
            out.append(f"- `[{p['slug']}-meta-title]` **Browser tab title** — {p['doc_title']}")
        if p['meta_desc']:
            out.append(f"- `[{p['slug']}-meta-desc]` **Meta description (search results)** — {p['meta_desc']}")
        if p['og_title'] and p['og_title'] != p['doc_title']:
            out.append(f"- `[{p['slug']}-og-title]` **Social share title** — {p['og_title']}")
        if p['og_desc'] and p['og_desc'] != p['meta_desc']:
            out.append(f"- `[{p['slug']}-og-desc]` **Social share description** — {p['og_desc']}")

        # group records by section, preserving first-seen order
        order = []
        groups = {}
        for r in p["records"]:
            key = r["section"]
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(r)

        for sect in order:
            recs = groups[sect]
            kind, _, label = sect.partition("#")
            # strip leading "m-" from modal ids
            if kind == "modal" and label.startswith("m-"):
                label = label[2:]
            pretty_label = label.replace("-"," ").replace("_"," ").strip().title() or kind.title()
            # capitalize "Lim" → "LIM"
            pretty_label = re.sub(r"\bLim\b", "LIM", pretty_label)
            kind_prefix = {
                "section":"", "article":"", "main":"",
                "header":"Header — ", "footer":"Footer — ",
                "nav":"Nav — ", "aside":"Sidebar — ", "dialog":"Modal — ",
                "modal":"Modal — ", "(other)":"Other — ",
            }.get(kind, kind.title()+" — ")
            out.append(f"\n### {kind_prefix}{pretty_label}\n")
            for r in recs:
                if r["tag"] == "a":
                    cls = ""  # detect from sidecar later if needed
                    css = r.get("css","")
                    if ".btn" in css:
                        tag_label = "Button (link)"
                    elif "nav" in r["section"].lower() or ".drop" in css:
                        tag_label = "Nav link"
                    else:
                        tag_label = "Link"
                else:
                    tag_label = {
                        "h1":"H1","h2":"H2","h3":"H3","h4":"H4","h5":"H5","h6":"H6",
                        "p":"Paragraph","li":"List item","button":"Button","label":"Label",
                        "figcaption":"Caption","summary":"Summary","blockquote":"Quote",
                        "dt":"Term","dd":"Definition","caption":"Caption","th":"Table header",
                        "td":"Table cell","option":"Option",
                        "input-placeholder":"Form placeholder","input-value":"Form button"
                    }.get(r["tag"], r["tag"].title())
                out.append(f"- `[{r['id']}]` **{tag_label}** — {r['text']}")
            out.append("")
    return "\n".join(out)

def render_md_clean(pages):
    """Stripped-down version: just IDs and copy text, organized by page and section. Easier reading for reviewers."""
    out = []
    out.append("# LIM 2026 — Site Copy for Review (Clean)\n")
    out.append("All customer-facing copy on the site, page by page. Each block is preceded by an ID like `[idx-001]`.\n")
    out.append("## How to make edits\n")
    out.append("1. **Do NOT change anything inside square brackets** like `[idx-001]`. These IDs let us locate each piece of copy back in the source.\n")
    out.append("2. To edit, change the line beneath the ID. Keep the ID exactly as it is.\n")
    out.append("3. To delete a block, leave the ID in place and write `[DELETE]` beneath it (or strike it through with track changes).\n")
    out.append("4. To add a new block in a section, write `[NEW]` on its own line and the new copy beneath. We'll insert it.\n")
    out.append("5. Send the doc back when done — we'll apply every change.\n")
    out.append("\n---\n")

    out.append("## Table of Contents\n")
    for p in pages:
        anchor = re.sub(r"[^a-z0-9]+","-", p["title"].lower()).strip("-")
        out.append(f"- [{p['title']}](#{anchor})")
    out.append("")

    for p in pages:
        out.append(f"\n---\n\n## {p['title']}\n")

        # SEO
        seo_lines = []
        if p['doc_title']:
            seo_lines.append(f"[{p['slug']}-meta-title]\n\n{p['doc_title']}")
        if p['meta_desc']:
            seo_lines.append(f"[{p['slug']}-meta-desc]\n\n{p['meta_desc']}")
        if p['og_title'] and p['og_title'] != p['doc_title']:
            seo_lines.append(f"[{p['slug']}-og-title]\n\n{p['og_title']}")
        if p['og_desc'] and p['og_desc'] != p['meta_desc']:
            seo_lines.append(f"[{p['slug']}-og-desc]\n\n{p['og_desc']}")
        if seo_lines:
            out.append("### SEO & Browser\n")
            out.append("\n\n".join(seo_lines))
            out.append("")

        order = []
        groups = {}
        for r in p["records"]:
            key = r["section"]
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(r)

        for sect in order:
            recs = groups[sect]
            kind, _, label = sect.partition("#")
            if kind == "modal" and label.startswith("m-"):
                label = label[2:]
            pretty_label = label.replace("-"," ").replace("_"," ").strip().title() or kind.title()
            pretty_label = re.sub(r"\bLim\b", "LIM", pretty_label)
            kind_prefix = {
                "section":"", "article":"", "main":"",
                "header":"Header — ", "footer":"Footer — ",
                "nav":"Nav — ", "aside":"Sidebar — ", "dialog":"Modal — ",
                "modal":"Modal — ", "(other)":"Other — ",
            }.get(kind, kind.title()+" — ")
            out.append(f"\n### {kind_prefix}{pretty_label}\n")
            for r in recs:
                out.append(f"[{r['id']}]")
                out.append("")
                out.append(r["text"])
                out.append("")
    return "\n".join(out)

def main():
    all_pages = []
    sidecar = {"pages": []}
    for path, slug, title in PAGES:
        p = extract_page(path, slug, title)
        all_pages.append(p)
        sidecar["pages"].append({
            "path": path, "slug": slug, "title": title,
            "records": p["records"],
        })
    md = render_md(all_pages)
    md_clean = render_md_clean(all_pages)
    out_md = os.path.join(REPO, "site-copy.md")
    out_md_clean = os.path.join(REPO, "site-copy-clean.md")
    out_json = os.path.join(REPO, "site-copy.map.json")
    open(out_md, "w", encoding="utf-8").write(md)
    open(out_md_clean, "w", encoding="utf-8").write(md_clean)
    open(out_json, "w", encoding="utf-8").write(json.dumps(sidecar, indent=2, ensure_ascii=False))
    total = sum(len(p["records"]) for p in all_pages)
    print(f"Wrote {out_md}  ({total} copy blocks across {len(all_pages)} pages)")
    print(f"Wrote {out_md_clean}  (clean version)")
    print(f"Wrote {out_json}")

if __name__ == "__main__":
    main()
