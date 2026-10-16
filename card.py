"""Builds card.svg: Brand of Sacrifice + profile info + contribution grid. Stdlib only."""
import json, os, urllib.request
from datetime import date
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "taddheotorres")
TOKEN = os.environ["GH_TOKEN"]

BRAND = """

                     --
                     **
                     %%
                :+#%@@@@%#+:
             .+@@@@@@@@@@@@@@+.
            +@@@@@#*@@@@*#@@@@@+
          .%@@%+.   @@@@   .+%@@%.
         .@@@=     .@@@@.     =@@@.
         %@%.       @@@@       .%@%
        *@#         @@@@         #@*
       .@#          %@@%          #@.
       +@.          *@@*          .@+
       %-           +@@+           -%
       #            =@@=            #
       .            :@@:            ..
                    .@@.
                     @@
                     %%
                     ##
                     **
                     ==
                     --
                     ::
""".strip("\n").split("\n")

INFO = [
    ("user", USER), ("role", "Full Stack Java Developer"), ("focus", "Backend, Ciberseguridad"),
    ("base", "La Paz, BCS, MX"), ("school", "Software Eng. @ UABCS"),
    None,
    ("stack.backend", "Java 21, Spring Boot 3.4, JPA"), ("stack.frontend", "Angular 21, TypeScript, RxJS"),
    ("stack.data", "PostgreSQL, MySQL 8, Flyway"), ("stack.infra", "Docker, nginx, Railway"),
    ("stack.security", "Spring Security, JWT, OWASP"), ("stack.testing", "JUnit 5, Mockito, Testcontainers"),
    None,
    ("forging", "honeypot-api, prismgit"), ("forged", "livestate, no-swipe-overview"),
    ("status", "open to Java Trainee / JR roles"),
]
COLS = 58          # chars per right-panel line
CW, LH = 7.9, 17   # char width / line height in px

C = dict(bg="#03050a", frame="#0f1b33", dim="#1b2a4a", dot="#1e3a6b", key="#7cb7ff", val="#c7dcff",
         head="#3b82f6", brand=("#0b1f4d", "#1d4ed8", "#60a5fa", "#bfdbfe"))
GRID = ["#0d1526", "#123a7a", "#1d5fd0", "#4a8ff0", "#a9cdff"]


def gql(query):
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": query}).encode(),
                                 {"Authorization": f"bearer {TOKEN}"})
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


u = gql(f"""{{ user(login: "{USER}") {{
  followers {{ totalCount }}
  repositories(ownerAffiliations: OWNER, first: 100, isFork: false) {{ totalCount nodes {{ stargazerCount }} }}
  contributionsCollection {{ contributionCalendar {{ totalContributions
    weeks {{ contributionDays {{ contributionCount weekday }} }} }} }} }} }}""")
cal = u["contributionsCollection"]["contributionCalendar"]
STATS = [("repos", str(u["repositories"]["totalCount"])),
         ("stars", str(sum(r["stargazerCount"] for r in u["repositories"]["nodes"]))),
         ("contributions", str(cal["totalContributions"])),
         ("followers", str(u["followers"]["totalCount"]))]

out, y = [], 0


def text(x, y, spans, cols=None, size=13):
    """One line; textLength pins it to `cols` chars so leaders line up in any monospace font."""
    fit = f' textLength="{cols * CW:.1f}" lengthAdjust="spacingAndGlyphs"' if cols else ""
    body = "".join(f'<tspan fill="{c}"{" font-weight=\"bold\"" if b else ""}>{escape(s)}</tspan>' for s, c, b in spans)
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve"{fit}>{body}</text>')


def rule(x, y, label):
    head = f"{label} "
    text(x, y, [(head, C["head"], True), ("─" * (COLS - len(head)), C["dim"], False)], COLS)


def row(x, y, k, v):
    dots = COLS - len(k) - len(v) - 4
    assert dots > 0, (k, v)
    text(x, y, [(k, C["key"], True), (": ", C["dot"], False), ("." * dots, C["dot"], False),
                ("  " + v, C["val"], False)], COLS)


# right panel
RX, y = 410, 60
rule(RX, y, f"{USER}@github")
for item in INFO:
    y += LH
    if item:
        row(RX, y, *item)
y += LH * 2; rule(RX, y, "- contact")
for k, v in [("mail", "taddheotorrespro@gmail.com"), ("web", "taddheotorres.github.io/portfolio")]:
    y += LH; row(RX, y, k, v)
y += LH * 2; rule(RX, y, "- github stats")
for k, v in STATS:
    y += LH; row(RX, y, k, v)
y += LH * 2
text(RX, y, [("> ", C["head"], False), ("the brand bleeds when danger is near.", C["val"], False)])
y += LH
text(RX, y, [("> ", C["head"], False), ("keep struggling.", C["val"], False)])
y += LH * 2
text(RX, y, [("taddheo@eclipse", C["key"], True), (":~$ ", C["val"], False)])
out.append(f'<rect x="{RX + 19 * CW:.1f}" y="{y - 11}" width="8" height="14" fill="{C["key"]}">'
           '<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></rect>')
panel_bottom = y

# brand, vertically centred against the panel, darker at the tips
BX, bcols = 30, max(map(len, BRAND))
by = 60 + (panel_bottom - 60 - (len(BRAND) - 1) * LH) / 2
for i, line in enumerate(BRAND):
    shade = C["brand"][max(0, 3 - abs(i - 6) // 4)] if line.strip() else C["bg"]
    text(BX, by + i * LH, [(line.ljust(bcols), shade, True)], bcols, 14)

# contribution grid
y = panel_bottom + LH * 3
text(30, y, [("- contributions ", C["head"], True), ("─" * 92, C["dim"], False)], 107)
weeks, peak = cal["weeks"], max([d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]] + [1])
GX, GY, S = 50, y + 22, 15
for wi, w in enumerate(weeks):
    for d in w["contributionDays"]:
        n = d["contributionCount"]
        lvl = 0 if n == 0 else min(4, 1 + int(4 * n / (peak + 1)))
        ch = "·" if lvl == 0 else "█"
        out.append(f'<text x="{GX + wi * S}" y="{GY + d["weekday"] * S}" font-size="14" fill="{GRID[lvl]}">{ch}</text>')
y = GY + 7 * S + 12
text(GX, y, [(f'{cal["totalContributions"]} contributions in the last year', C["val"], False)])
lx = GX + len(weeks) * S - 150
text(lx, y, [("less ", C["key"], False)])
for i, c in enumerate(GRID):
    out.append(f'<text x="{lx + 42 + i * 14}" y="{y}" font-size="14" fill="{c}">{"·" if i == 0 else "█"}</text>')
text(lx + 42 + 5 * 14 + 4, y, [("more", C["key"], False)])

H, W = y + 30, 900
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'DejaVu Sans Mono\',monospace">'
       f'<rect width="{W}" height="{H}" rx="10" fill="{C["bg"]}" stroke="{C["frame"]}"/>'
       f'<text x="30" y="32" font-size="12" fill="{C["dot"]}">{USER} / card.svg · updated {date.today()}</text>'
       + "".join(out) + "</svg>")
open("card.svg", "w").write(svg)
print("card.svg", H, "px tall")
