"""Build the LIM history page and its Word version from one source.

    python tools-lim-history/build.py

Writes the body of docs-lim-history.html (between the BUILD markers) and
lim-history.docx at the repo root (served at /lim-history/word).
Needs python-docx and cairosvg (for the logo in the Word file).

Inline markup in the content strings:
  **bold**   *italic*   [[confirm]] — a fact Robert must confirm; highlighted
  on screen and in Word, plain in print.
"""
import html, io, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs-lim-history.html"
DOCX = ROOT / "lim-history.docx"
LOGO = ROOT / "brand/lutheranindianMinistries-logo-horz-stacked.svg"

TITLE = "A History of Lutheran Indian Ministries"
LABEL = "Prepared for the Board of Directors"
DATE = "October 2026"

LEDE = ("Lutheran Indian Ministries began more than fifty years ago as a handful of pilots and "
        "pastors flying the Gospel into northern communities that no road reached. It is now a "
        "Native-led ministry that equips Native people to carry that Gospel to their own "
        "communities. This history traces how that change came about, what it cost, and where "
        "it has led.")

SECTIONS = [
    ("Wings Over the North", "1970–1984", [
        "On **June 16, 1970**, the **Lutheran Association of Missionaries and Pilots (LAMP)** was "
        "incorporated in Canada. Its founder, **Rev. Les Stahlke**, was a Lutheran pastor who "
        "combined his flying skills with Christian outreach to people in remote, sparsely settled "
        "areas of northern Alberta who had no pastoral care. Over the years LAMP added more "
        "pilot-pastors and extended its reach into the Northwest Territories, British Columbia, "
        "Alberta, Manitoba, Saskatchewan and Ontario.",
        "LAMP built working relationships with the major denominations that had historically held "
        "spiritual responsibility for many northern communities. From those relationships grew a "
        "full-time volunteer corps, **Christians-in-Service (CIS)**, whose members lived and worked "
        "in northern communities as a Christian presence, helping local service providers and "
        "assisting local churches.",
        "In **1981** LAMP added the **Volunteers-in-Ministry (VIM)** program. Like CIS volunteers, "
        "VIM volunteers provided their own financial support, and over the years they came from "
        "all over North America. LAMP also sent **Vacation Bible School** teams, typically three "
        "to five teachers who spent one to two weeks in a northern Native community.",
    ]),
    ("An American Partner", "1985–1993", [
        "On **January 3, 1985**, **Lutheran Association of Missionaries and Pilots U.S., Inc.** was "
        "incorporated in the United States, with an office in **Milwaukee, Wisconsin**. Its purpose "
        "was to help Christian churches carry out ministry in the sparsely settled and physically "
        "isolated areas of Canada. In **March 1989** the work expanded to **Alaska**.",
        "LAMP now operated as two national organizations, one Canadian and one American, sharing a "
        "name, a logo and a mission field: a bush-aviation ministry carrying pastors into remote "
        "Native communities across northern Canada and Alaska with limited or no road access.",
    ]),
    ("A Change of Conviction", "1993–1999", [
        "**Rev. Don Johnson**, a Native American LCMS pastor, joined the staff in September 1993 and "
        "was appointed interim Executive Director in January 1994, the first Native American to "
        "lead the organization.",
        "Under his leadership the emphasis shifted toward equipping Native American, First Nations "
        "and Alaska Native people to become spiritual leaders in their own communities. Beginning "
        "in 1995, and approved by both boards in **1996**, a long-range plan reoriented the work "
        "from presence toward **evangelism, discipleship, and the recruitment and training of "
        "Native Christians to serve as pastors to their own people**. The vision was to disciple "
        "Native people for ministry, and Native Christians joined the staff.",
        "That reorientation was not universally welcomed, and the two national organizations came "
        "to hold genuinely different convictions about how the work should be done.",
    ]),
    ("The Separation", "2000–2005", [
        "By 2000 the partnership had become unworkable. Joint board meetings no longer produced "
        "agreement, and staff of both LAMP U.S. and LAMP Canada were leaving. On **April 25, 2000**, "
        "the joint executive staff wrote to the U.S. board asking it to act. On **May 5, 2000**, the "
        "**U.S. board voted to end the ministry partnership**.",
        "The U.S. organization's own work kept growing. As more Native leaders served their people "
        "through the ministry, it expanded in **2001** to the **Makah Indian Reservation at Neah "
        "Bay, Washington**, and later to the Lower Elwha and other tribes of the Olympic Peninsula.",
        "Litigation followed over the shared name and marks. The federal court's orders were clear "
        "in their outcome: the U.S. organization **could no longer use the acronym LAMP**, though it "
        "kept its legal name, and its newsletter could no longer be called *The LAMPLighter*. A "
        "settlement order, **still in force today**, requires each organization to notify the other "
        "of any estate gift executed between **January 1, 1985 and April 1, 2005**. Fewer gifts fall "
        "inside that window with each passing year.",
    ]),
    ("One Ministry, Many Nations", "2006–2015", [
        "In **2006**, Lutheran Association of Missionaries and Pilots U.S. merged with the **Council "
        "for Lutheran American Indian Ministries (CLAIM)**, bringing Lutheran ministry among Native "
        "Americans under a single organization. Alongside the existing work in Alaska, Canada and "
        "the Olympic Peninsula, the merger added ministry in **Kansas**, through **Haskell LIGHT**, "
        "and in **New Mexico**, through **Shepherd of the Valley Lutheran Church** in Navajo.",
        "In **March 2010** the ministry adopted a new name that better reflected its mission and "
        "vision: **Lutheran Indian Ministries (LIM)**. Its legal name remains Lutheran Association "
        "of Missionaries and Pilots U.S., Inc. In **2014** LIM extended its work to **Hawaii**, "
        "serving Native Hawaiian people.",
    ]),
    ("Transition and Testing", "2016–2021", [
        "Don Johnson retired in 2016 after more than two decades. **Tim Young Eagle** (Pawnee), a "
        "former board member and long-time advocate of Native American outreach, succeeded him as "
        "Executive Director and served from 2016 to 2020. In **2018** the ministry expanded to the "
        "many tribes living in and around **Phoenix, Arizona**.",
        "Under Tim's leadership LIM moved into **urban Native communities** and began adding social "
        "and healing ministry to its work. It affirmed the diversity of God's creation and the unity "
        "all believers share in Christ, encouraging Native Christians to use every gift God has "
        "given them, including their languages and cultures, to glorify their Savior, Jesus Christ.",
        "An effort to offer fee-for-service programs in Phoenix brought the hardest chapter in the "
        "organization's recent history. LIM contracted with outside billing agencies to handle "
        "Medicaid claims. **Those agencies were committing fraud, without LIM's knowledge.** The "
        "organization and several staff were charged. **LIM and its Chief Financial Officer were "
        "dismissed from the charges**, and a portion of the fee-for-service revenue was returned to "
        "Medicaid.",
        "**Robert Heffle** was hired in **December [[2021]]**, in the middle of that litigation, and "
        "brought all court proceedings with the State of Arizona to a settlement.",
    ]),
    ("A New Footing", "Recent years", [
        "When the requirements for LCMS **Recognized Service Organizations (RSOs)** changed to call "
        "for a board made up entirely of LCMS members, LIM was not renewed as an RSO. Without that "
        "status LIM could no longer call pastors, and the change led it to rethink its role in "
        "Native missions.",
        "Its focus turned to supporting the LCMS congregations and pastors who serve Native "
        "communities. LIM began an annual **Pastor Gathering** to support pastors, solve problems "
        "together and hear their needs. Rather than calling a pastor to Neah Bay, LIM now supports "
        "the congregation there with a direct financial contribution, while the pastor is "
        "supervised by the Northwest District and the congregation's board.",
    ]),
    ("Healing the Wounds of Trauma", "2022 onward", [
        "In **2022** the LIM board approved a focus on the trauma that affects Native communities "
        "and families, with the aim of offering Christ-centered programs to meet that need. LIM "
        "adopted ***Healing the Wounds of Trauma: How the Church Can Help***, from the American "
        "Bible Society's Trauma Healing Institute.",
        "The first trainings were held in **Fairbanks and Anchorage, Alaska**. Those trained, "
        "including LIM staff, an LCMS pastor and an Elder, went on to lead in-person healing groups "
        "in cities, villages and reservations. When invited, LIM holds a healing group, trains "
        "local facilitators, and offers ongoing support virtually and in person. Healing groups are "
        "now also offered **online**, so that people can experience Christ-centered healing and "
        "learn to help others in their own communities who have experienced trauma.",
    ]),
    ("Into the Word", "2026", [
        "In **2026** LIM invited people to read through the **Bible in a Year** together, with a "
        "reading guide and a general schedule. Sixteen people signed up in the first week and "
        "**91** in all, and 8 to 15 take part in each bi-weekly online meeting. The group expects "
        "to finish reading the entire Bible in **March 2027**. Next, LIM plans to invite a group to "
        "read through the New Testament, with context for each chapter offered by an LCMS pastor.",
    ]),
    ("Where the Ministry Stands", "Today", [
        "LIM today is a **Native-led ministry** organized around three commitments: to **proclaim** "
        "the Gospel in Native communities, to **disciple** Native leaders, most visibly through "
        "Haskell LIGHT, and to **heal** the wounds of trauma in Native communities and families.",
        "That third commitment has become some of the ministry's most consequential work. Its "
        "healing groups, built on the Trauma Healing Institute curriculum and led by trained Native "
        "facilitators, meet in person and online at no cost to those who attend.",
        "LIM continues to proclaim the Gospel of Jesus Christ among Native American people, "
        "equipping Nations with the Word of God and with resources that help heal social "
        "suffering, while valuing Native cultures. Its message to Native people is that even the "
        "wounded can be used by God to reach others, and that generational change is possible.",
    ]),
]

TIMELINE = [
    ("1970", "LAMP incorporated in Canada (June 16), founded by Rev. Les Stahlke"),
    ("1981", "Volunteers-in-Ministry program begins"),
    ("1985", "LAMP U.S. incorporated (January 3), Milwaukee, Wisconsin"),
    ("1989", "Ministry expands to Alaska (March)"),
    ("1994", "Rev. Don Johnson becomes the first Native American to lead the ministry"),
    ("1996", "Both boards approve the long-range plan to train Native leaders"),
    ("2000", "U.S. board ends the partnership with LAMP Canada (May 5)"),
    ("2001", "Ministry expands to Neah Bay, Washington"),
    ("2006", "Merger with CLAIM adds Kansas (Haskell LIGHT) and New Mexico"),
    ("2010", "New name: Lutheran Indian Ministries (March)"),
    ("2014", "Ministry expands to Hawaii"),
    ("2016", "Tim Young Eagle succeeds Don Johnson"),
    ("2018", "Ministry expands to Phoenix, Arizona"),
    ("[[2021]]", "Robert Heffle hired (December)"),
    ("2022", "Board adopts the trauma-healing focus; healing groups begin"),
    ("2026", "Bible in a Year reading group begins"),
]

SOURCE = ("Compiled from LIM's *History of LAMP* (2018, updated 2023), the August 2026 board "
          "draft, and additions by Robert Heffle, October 2026.")

TOKEN = re.compile(r"(\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*|\[\[.+?\]\])")


def runs(text):
    """Split markup into (text, bold, italic, confirm) runs."""
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("***"):
            yield part[3:-3], True, True, False
        elif part.startswith("**"):
            yield part[2:-2], True, False, False
        elif part.startswith("[["):
            yield part[2:-2], False, False, True
        elif part.startswith("*"):
            yield part[1:-1], False, True, False
        else:
            yield part, False, False, False


def to_html(text):
    out = []
    for t, b, i, c in runs(text):
        t = html.escape(t, quote=False).replace("–", "&ndash;")
        if c:
            t = f'<span class="confirm">{t}</span>'
        if i:
            t = f"<em>{t}</em>"
        if b:
            t = f"<strong>{t}</strong>"
        out.append(t)
    return "".join(out)


def build_html():
    h = [f'  <p class="lede">{to_html(LEDE)}</p>', ""]
    for title, era, paras in SECTIONS:
        h.append(f"  <h3>{to_html(title)}</h3>")
        h.append(f'  <span class="era">{to_html(era)}</span>')
        h += [f"  <p>{to_html(p)}</p>" for p in paras]
        h.append("")
    h.append('  <div class="timeline">')
    h.append("    <h3>Timeline at a Glance</h3>")
    h.append("    <dl>")
    for year, what in TIMELINE:
        h.append(f"      <dt>{to_html(year)}</dt><dd>{to_html(what)}</dd>")
    h.append("    </dl>")
    h.append("  </div>")
    h.append("")
    h.append(f'  <p class="foot">{to_html(SOURCE)}</p>')
    body = "\n".join(h)
    page = PAGE.read_text()
    page, n = re.subn(r"(<!-- BUILD:START -->\n).*?(  <!-- BUILD:END -->)",
                      lambda m: m.group(1) + body + "\n" + m.group(2), page, flags=re.S)
    assert n == 1, "BUILD markers not found in " + PAGE.name
    PAGE.write_text(page)


def build_docx():
    import cairosvg
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_COLOR_INDEX
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor

    CHAR = RGBColor(0x28, 0x29, 0x24)
    MUTED = RGBColor(0x5A, 0x5A, 0x52)
    SAGE = RGBColor(0x8A, 0x86, 0x65)
    SKY = RGBColor(0x4F, 0x86, 0x9C)
    SERIF, SANS = "Georgia", "Arial"

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.left_margin = sec.right_margin = Inches(1)
    sec.top_margin = sec.bottom_margin = Inches(0.9)

    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size, normal.font.color.rgb = SERIF, Pt(11), CHAR
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), SERIF)
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.line_spacing = 1.25

    h1 = doc.styles["Heading 1"]
    h1.font.name, h1.font.size, h1.font.bold, h1.font.color.rgb = SANS, Pt(13), True, CHAR
    h1.font.all_caps = True
    h1.paragraph_format.space_before, h1.paragraph_format.space_after = Pt(18), Pt(0)
    h1.paragraph_format.keep_with_next = True

    def add(par, text, size=None, color=None):
        for t, b, i, c in runs(text):
            r = par.add_run(t)
            r.bold, r.italic = b or None, i or None
            if c:
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW
            if size:
                r.font.size = size
            if color:
                r.font.color.rgb = color
        return par

    def rule(par, sz=18):
        pPr = par._p.get_or_add_pPr()
        bdr = OxmlElement("w:pBdr")
        b = OxmlElement("w:bottom")
        for k, v in (("val", "single"), ("sz", str(sz)), ("space", "6"), ("color", "282924")):
            b.set(qn("w:" + k), v)
        bdr.append(b)
        pPr.append(bdr)

    logo = io.BytesIO(cairosvg.svg2png(url=str(LOGO), output_height=300))
    doc.add_picture(logo, height=Inches(0.6))

    p = doc.add_paragraph()
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(14), Pt(2)
    r = p.add_run(LABEL.upper())
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = SANS, Pt(8.5), True, SAGE

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(TITLE)
    r.font.size, r.font.bold = Pt(24), True

    p = doc.add_paragraph()
    rule(p)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run(DATE)
    r.font.name, r.font.size, r.font.color.rgb = SANS, Pt(10), MUTED

    add(doc.add_paragraph(), LEDE, size=Pt(12.5)).paragraph_format.space_after = Pt(6)

    for title, era, paras in SECTIONS:
        doc.add_heading(title, level=1)
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(era.upper())
        r.font.name, r.font.size, r.font.bold, r.font.color.rgb = SANS, Pt(8.5), True, SKY
        for para in paras:
            add(doc.add_paragraph(), para)

    doc.add_heading("Timeline at a Glance", level=1)
    t = doc.add_table(rows=0, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for year, what in TIMELINE:
        cells = t.add_row().cells
        cells[0].width, cells[1].width = Inches(0.8), Inches(5.7)
        for cell, text, bold in ((cells[0], year, True), (cells[1], what, False)):
            par = cell.paragraphs[0]
            par.paragraph_format.space_after = Pt(3)
            for run in add(par, text, size=Pt(10)).runs:
                run.font.name = SANS
                run.bold = run.bold or bold or None

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(20)
    add(p, SOURCE, size=Pt(9), color=MUTED)

    props = doc.core_properties
    props.title, props.author = TITLE, "Lutheran Indian Ministries"
    doc.save(DOCX)


if __name__ == "__main__":
    build_html()
    build_docx()
    print("wrote", PAGE.name, "and", DOCX.name)
