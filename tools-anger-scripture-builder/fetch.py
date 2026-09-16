import json, os, re, sys, time, urllib.request, urllib.parse
SP=os.path.join(os.path.dirname(os.path.abspath(__file__)),"cache"); os.makedirs(SP,exist_ok=True)
BOOKS=["Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi","Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"]
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    for i in range(3):
        try: return json.load(urllib.request.urlopen(req,timeout=40))
        except Exception as e:
            time.sleep(2)
    raise SystemExit("fetch failed "+url)
def chapter(b,c):
    p=f"{SP}/ch_{b}_{c}.json"
    if os.path.exists(p): return json.load(open(p))
    d=get(f"https://bolls.life/get-text/ESV/{b}/{c}/"); json.dump(d,open(p,"w")); time.sleep(0.4); return d
def search(word):
    p=f"{SP}/find_{word}.json"
    if os.path.exists(p): return json.load(open(p))
    d=get("https://bolls.life/v2/find/ESV?"+urllib.parse.urlencode({"search":word,"match_case":"false","match_whole":"true","limit":3000}))
    json.dump(d,open(p,"w")); time.sleep(0.6); return d
if __name__=="__main__":
    words=sys.argv[1:]
    for w in words: print(w, search(w)["total"])
