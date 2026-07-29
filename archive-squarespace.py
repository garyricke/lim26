#!/usr/bin/env python3
"""
Archive the old Squarespace site before it's cancelled.

Squarespace hosts both the pages and the images. When the subscription lapses,
all of it disappears — including ~1,400 devotion and news posts going back to
2017. This pulls the whole thing down to local disk in a form we can search,
read, and rebuild from.

For each page it writes:
  archive/squarespace/html/<slug>.html   raw HTML, exactly as served
  archive/squarespace/posts/<slug>.md    clean markdown + YAML frontmatter
  archive/squarespace/images/…           every image the page references
  archive/squarespace/index.json         one record per page
  archive/squarespace/index.html         browsable, searchable index

Run:  ./.venv-archive/bin/python archive-squarespace.py [--limit N] [--skip-images]
Resumable — anything already downloaded is skipped, so it's safe to re-run.
"""

import argparse, hashlib, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

SITE = "https://www.lutheranindianministries.org"
OUT = Path("archive/squarespace")
UA = {"User-Agent": "Mozilla/5.0 (compatible; LIM site archive; owner-operated backup)"}
# Squarespace rate-limits hard: 6 workers at 0.12s got 964 x HTTP 429 on the
# first full run. Two workers with a ~1s pause completes without throttling.
WORKERS = 2
PAUSE = 1.0
MAX_RETRIES = 5


def get(url, timeout=45):
    """GET with backoff on 429/5xx, honouring Retry-After when present."""
    delay = 5.0
    for attempt in range(MAX_RETRIES):
        r = requests.get(url, headers=UA, timeout=timeout)
        if r.status_code == 429 or 500 <= r.status_code < 600:
            if attempt == MAX_RETRIES - 1:
                r.raise_for_status()
            wait = delay
            ra = r.headers.get("Retry-After")
            if ra:
                try:
                    wait = max(wait, float(ra))
                except ValueError:
                    pass
            time.sleep(wait)
            delay *= 2
            continue
        r.raise_for_status()
        return r
    raise RuntimeError(f"exhausted retries: {url}")


# ── URL list ──────────────────────────────────────────────────────────────────
def canonical_urls():
    """Unique pages from the sitemap.

    /news/<slug> and /news-notes/<slug> serve the same post, so keep one per
    slug. Prefer whichever section holds more of the archive.
    """
    xml = get(f"{SITE}/sitemap.xml").text
    locs = [u.strip() for u in re.findall(r"<loc>(.*?)</loc>", xml)]

    by_slug, order = {}, []
    for u in locs:
        parts = [p for p in urlparse(u).path.split("/") if p]
        slug = parts[-1] if parts else "home"
        section = parts[0] if len(parts) > 1 else ""
        # /news-notes wins over /news for the same slug
        if slug in by_slug:
            if by_slug[slug][1] == "news" and section == "news-notes":
                by_slug[slug] = (u, section)
            continue
        by_slug[slug] = (u, section)
        order.append(slug)
    return [(s, by_slug[s][0], by_slug[s][1]) for s in order]


# ── extraction ────────────────────────────────────────────────────────────────
def article_ld(soup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(tag.string or "")
        except Exception:
            continue
        if isinstance(d, dict) and d.get("@type") in ("Article", "BlogPosting", "NewsArticle"):
            return d
    return {}


def clean_body(soup):
    """The post body, with Squarespace's chrome stripped out."""
    node = soup.select_one('[data-content-field="main-content"]') \
        or soup.select_one(".blog-item-content") \
        or soup.select_one("article")
    if not node:
        return None
    for junk in node.select("script, style, noscript, .sqs-block-form, "
                            ".BlogItem-share, .item-pagination, .comments"):
        junk.decompose()
    # Squarespace lazy-loads: the real src lives in data-src
    for img in node.find_all("img"):
        real = img.get("data-src") or img.get("src")
        if real:
            img["src"] = real.split("?")[0]
        for attr in ("data-src", "srcset", "data-srcset", "sizes", "data-image"):
            img.attrs.pop(attr, None)
    return node


def image_urls(node, ld):
    urls = set()
    if node:
        for img in node.find_all("img"):
            src = img.get("src", "")
            if src.startswith("http"):
                urls.add(src.split("?")[0])
    hero = ld.get("image")
    if isinstance(hero, str) and hero.startswith("http"):
        urls.add(hero.split("?")[0])
    return sorted(urls)


def yaml_escape(v):
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'


# ── per-page work ─────────────────────────────────────────────────────────────
def fetch_page(slug, url, section):
    raw_path = OUT / "html" / f"{slug}.html"
    if raw_path.exists():
        html = raw_path.read_text(encoding="utf-8", errors="replace")
    else:
        r = get(url)
        html = r.text
        raw_path.write_text(html, encoding="utf-8")
        time.sleep(PAUSE)

    soup = BeautifulSoup(html, "lxml")
    ld = article_ld(soup)
    body = clean_body(soup)

    og = soup.find("meta", property="og:title")
    title = ld.get("headline") or (og["content"].split(" — ")[0] if og else slug)
    desc = soup.find("meta", attrs={"name": "description"})

    md = markdownify(str(body), heading_style="ATX", strip=["script", "style"]) if body else ""
    md = re.sub(r"\n{3,}", "\n\n", md).strip()

    rec = {
        "slug": slug,
        "url": url,
        "section": section,
        "title": title.strip(),
        "date": (ld.get("datePublished") or "")[:10],
        "modified": (ld.get("dateModified") or "")[:10],
        "author": ld.get("author") if isinstance(ld.get("author"), str) else "",
        "description": (desc["content"].strip() if desc and desc.get("content") else ""),
        "images": image_urls(body, ld),
        "words": len(md.split()),
    }

    front = "\n".join([
        "---",
        f"title: {yaml_escape(rec['title'])}",
        f"slug: {rec['slug']}",
        f"date: {rec['date']}",
        f"author: {yaml_escape(rec['author'])}",
        f"original_url: {rec['url']}",
        f"section: {rec['section']}",
        f"images: {json.dumps(rec['images'])}",
        "---",
        "",
    ])
    (OUT / "posts" / f"{slug}.md").write_text(front + md + "\n", encoding="utf-8")
    return rec


def fetch_image(url):
    name = unquote(urlparse(url).path.strip("/").split("/")[-1]) or "image"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)[:120]
    # Squarespace reuses filenames across posts, so prefix with a digest of the
    # path. Must be hashlib, not hash() — the builtin is salted per process, so
    # a re-run would rename every file and re-download the whole library.
    digest = hashlib.md5(urlparse(url).path.encode()).hexdigest()[:8]
    key = f"{digest}-{name}"
    dest = OUT / "images" / key
    if dest.exists() and dest.stat().st_size:
        return url, key, dest.stat().st_size
    r = get(url, timeout=60)
    dest.write_bytes(r.content)
    time.sleep(PAUSE)
    return url, key, len(r.content)


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="only the first N pages (for testing)")
    ap.add_argument("--skip-images", action="store_true")
    args = ap.parse_args()

    for sub in ("html", "posts", "images"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    pages = canonical_urls()
    if args.limit:
        pages = pages[:args.limit]
    print(f"{len(pages)} unique pages to archive")

    records, failures = [], []
    with ThreadPoolExecutor(WORKERS) as pool:
        futs = {pool.submit(fetch_page, *p): p for p in pages}
        for i, fut in enumerate(as_completed(futs), 1):
            slug, url, _ = futs[fut]
            try:
                records.append(fut.result())
            except Exception as e:
                failures.append({"slug": slug, "url": url, "error": str(e)})
            if i % 100 == 0 or i == len(pages):
                print(f"  pages {i}/{len(pages)}  ({len(failures)} failed)")

    records.sort(key=lambda r: (r["date"] or "0000"), reverse=True)

    # images
    img_map, img_bytes = {}, 0
    if not args.skip_images:
        all_imgs = sorted({u for r in records for u in r["images"]})
        print(f"{len(all_imgs)} unique images")
        with ThreadPoolExecutor(WORKERS) as pool:
            futs = {pool.submit(fetch_image, u): u for u in all_imgs}
            for i, fut in enumerate(as_completed(futs), 1):
                try:
                    url, key, size = fut.result()
                    img_map[url] = key
                    img_bytes += size
                except Exception as e:
                    failures.append({"image": futs[fut], "error": str(e)})
                if i % 200 == 0 or i == len(all_imgs):
                    print(f"  images {i}/{len(all_imgs)}  ({img_bytes/1e6:.0f} MB)")

    (OUT / "index.json").write_text(json.dumps({
        "archived": time.strftime("%Y-%m-%d"),
        "source": SITE,
        "pages": len(records),
        "images": len(img_map),
        "image_bytes": img_bytes,
        "records": records,
        "image_map": img_map,
        "failures": failures,
    }, indent=2), encoding="utf-8")

    write_index(records, img_bytes, len(img_map))
    print(f"\ndone — {len(records)} pages, {len(img_map)} images "
          f"({img_bytes/1e6:.0f} MB), {len(failures)} failures")
    print(f"open {OUT}/index.html")


def write_index(records, img_bytes, img_count):
    rows = "\n".join(
        f'<tr data-t="{(r["title"] + " " + r["slug"]).lower().replace(chr(34), "")}">'
        f'<td class="d">{r["date"] or "—"}</td>'
        f'<td><a href="posts/{r["slug"]}.md">{BeautifulSoup(r["title"], "lxml").get_text()}</a>'
        f'<div class="u">{r["section"]}/{r["slug"]}</div></td>'
        f'<td class="n">{r["words"]}</td>'
        f'<td class="n">{len(r["images"])}</td>'
        f'<td><a class="ext" href="{r["url"]}" target="_blank" rel="noopener">live&nbsp;↗</a></td></tr>'
        for r in records
    )
    html = f"""<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Squarespace Archive — Lutheran Indian Ministries</title>
<style>
 *{{margin:0;padding:0;box-sizing:border-box}}
 body{{font:15px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#282924;background:#EBE9E4;padding:2rem 1.25rem}}
 .w{{max-width:1050px;margin:0 auto}}
 h1{{font-size:1.7rem;margin-bottom:.3rem}}
 .sub{{color:#5a5a52;margin-bottom:1.5rem;font-size:.94rem}}
 .stats{{display:flex;gap:2rem;flex-wrap:wrap;background:#fff;border-radius:10px;padding:1rem 1.3rem;margin-bottom:1.3rem}}
 .stats b{{display:block;font-size:1.5rem;line-height:1.2}}
 .stats span{{font-size:.76rem;letter-spacing:.09em;text-transform:uppercase;color:#5a5a52}}
 #q{{width:100%;padding:.75rem 1rem;border:2px solid #d9d6ce;border-radius:8px;font-size:1rem;margin-bottom:1rem;font-family:inherit}}
 #q:focus{{outline:none;border-color:#282924}}
 table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden}}
 th,td{{padding:.6rem .8rem;text-align:left;border-bottom:1px solid #EBE9E4;vertical-align:top}}
 th{{background:#282924;color:#fff;font-size:.74rem;letter-spacing:.09em;text-transform:uppercase;position:sticky;top:0}}
 td.d{{white-space:nowrap;color:#5a5a52;font-size:.85rem;font-variant-numeric:tabular-nums}}
 td.n{{text-align:right;color:#5a5a52;font-size:.85rem;font-variant-numeric:tabular-nums}}
 a{{color:#282924}} .u{{font-size:.76rem;color:#8a8665}} .ext{{font-size:.8rem;color:#ED1C24;text-decoration:none;white-space:nowrap}}
 tr:hover{{background:#faf9f7}}
</style>
<div class="w">
<h1>Squarespace Archive</h1>
<p class="sub">Everything from the old lutheranindianministries.org, captured before the subscription lapses.
Markdown in <code>posts/</code>, original HTML in <code>html/</code>, images in <code>images/</code>.</p>
<div class="stats">
  <div><b>{len(records)}</b><span>Pages</span></div>
  <div><b>{img_count}</b><span>Images</span></div>
  <div><b>{img_bytes/1e6:.0f} MB</b><span>Media</span></div>
  <div><b>{sum(r['words'] for r in records):,}</b><span>Words</span></div>
  <div><b>{time.strftime('%b %-d, %Y')}</b><span>Archived</span></div>
</div>
<input id="q" placeholder="Search {len(records)} pages by title or slug…" autocomplete="off">
<table><thead><tr><th>Date</th><th>Title</th><th>Words</th><th>Imgs</th><th></th></tr></thead>
<tbody id="tb">
{rows}
</tbody></table>
</div>
<script>
var q=document.getElementById('q'),rows=[].slice.call(document.querySelectorAll('#tb tr'));
q.addEventListener('input',function(){{
  var v=q.value.toLowerCase().trim();
  rows.forEach(function(r){{r.style.display=!v||r.dataset.t.indexOf(v)>-1?'':'none';}});
}});
</script>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
