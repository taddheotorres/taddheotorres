"""Builds card.svg: ASCII spider + profile info + contribution grid. Stdlib only."""
import json, os, re, urllib.request
from datetime import date
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "taddheotorres")
TOKEN = os.environ["GH_TOKEN"]

BRAND = """
                        :--=--:.
                       *%+-:.  .:                   .:==--:.
                      -%:      ..                 -*%##+----:.::
                     :%=       =             .-+**=:.        --
                    :%#       ==        :--*#*+:          .--
                    =@*      :*.      .*@%+-..          .==.
                    .*#+.   .*-      :%%=   .         .==:
                   . .%%....++    ...#%.    .       :==.
                  .  .-@=..=#-...  .#%.    .      .==.
              ===.   . #%.:*+    ..+@-     .    :+#***+=--::.
             .#+%#-  . -@*=+:...  :@+..    :-+*****=:     ..
              - :+@=. ..%@-:      #%: :-+*%#*=...       ...
              :.. -**:  +%++= .  :@=.*%%#+.   .      .-:.
         =-.#%#-:. .*@*=#@@%**#:-%+-%#=:.   ..    .-+=.
       .#@*@@++#@@%@@@@@@@@@@@%@#*##-.  .  .   :-++-.
      .%%=+-.:+@@@*=+%@@@@@@@@%#%*:..  .  ::-=++-.
      +*:-.. :@@%+++#@@@@@@@@@@@@%-....:-++=-:
    .#*.:   .#@@@@@@@@@@@@@%@@%++##+=-:::.
   :*#  ....-@@@@@@@@@@@@%#@@@#===*#=. :
  .#*.     .:%@@@@@@@@@@%%@@@+=-:. +#= .
  *#..      .+@@@@@@@@@@@@@%+=-    .:*=
  #-    ... :=#@@@@@@@@@@@#**+=....   --
  #........:==+*%%%@@@@@%#++=-:::.     :-
 .+      .--:--==++++#@%*+-     .:::.   .:
 .:    :-:    ......+*#*+.          ......
 :  .:-.        .  -%=++.
 :..:            ..#:-=.
  .              .+::-
                 -:::
                ::-.
               .-:
               :
""".strip("\n").split("\n")

INFO = [
    ("user", USER), ("role", "Full Stack Java Developer"), ("focus", "Backend, Ciberseguridad"),
    ("base", "La Paz, BCS, MX"), ("school", "Software Eng. @ UABCS"), ("os", "Debian, Nobara, Windows"),
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

C = dict(bg="#050203", frame="#2a0a0c", dim="#3a0d10", dot="#5c1216", key="#ff3b3b", val="#f2c4c4",
         head="#d11a1a", brand=("#7a0a0e", "#c0121a", "#ff2a2a", "#ff8a8a"))
GRID = ["#1a0608", "#5c0a0e", "#9b0f15", "#d8141c", "#ff5a5a"]


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
text(RX, y, [("taddheo@eclipse", C["key"], True), (":~$ ", C["val"], False)])
out.append(f'<rect x="{RX + 19 * CW:.1f}" y="{y - 11}" width="8" height="14" fill="{C["key"]}">'
           '<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></rect>')
panel_bottom = y

# spider, vertically centred against the panel; denser chars get brighter reds
BX, bcols, BLH = 30, max(map(len, BRAND)), 11
TIER = {c: i for i, cs in enumerate([" .:-", "=+*", "#%", "@"]) for c in cs}
by = 60 + (panel_bottom - 60 - (len(BRAND) - 1) * BLH) / 2
for i, line in enumerate(BRAND):
    runs = [(m.group(), C["brand"][TIER[m.group()[0]]], True)
            for m in re.finditer(r"[ .:-]+|[=+*]+|[#%]+|@+", line.ljust(bcols))]
    text(BX, by + i * BLH, runs, bcols * 5.5 / CW, 9.2)

# contribution grid, stretched to the same margins as the panel above
RIGHT = RX + COLS * CW
y = panel_bottom + LH * 3
gcols = (RIGHT - 30) / CW
text(30, y, [("- contributions ", C["head"], True), ("─" * (round(gcols) - 16), C["dim"], False)], gcols)
weeks, peak = cal["weeks"], max([d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]] + [1])
GX, GY = 30, y + 22
S = (RIGHT - GX - 8) / (len(weeks) - 1)  # 8 = glyph width, so the last column ends on RIGHT
for wi, w in enumerate(weeks):
    for d in w["contributionDays"]:
        n = d["contributionCount"]
        lvl = 0 if n == 0 else min(4, 1 + int(4 * n / (peak + 1)))
        ch = "·" if lvl == 0 else "█"
        out.append(f'<text x="{GX + wi * S:.1f}" y="{GY + d["weekday"] * 15}" font-size="14" fill="{GRID[lvl]}">{ch}</text>')
y = GY + 7 * 15 + 12
text(GX, y, [(f'{cal["totalContributions"]} contributions in the last year', C["val"], False)])
out.append(f'<text x="{RIGHT:.1f}" y="{y}" font-size="13" text-anchor="end" fill="{C["key"]}">more</text>')
lx = RIGHT - 4 * CW - 6 - 5 * 14
for i, c in enumerate(GRID):
    out.append(f'<text x="{lx + i * 14:.1f}" y="{y}" font-size="14" fill="{c}">{"·" if i == 0 else "█"}</text>')
out.append(f'<text x="{lx - 6:.1f}" y="{y}" font-size="13" text-anchor="end" fill="{C["key"]}">less</text>')

H, W = y + 30, 900
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'DejaVu Sans Mono\',monospace">'
       f'<rect width="{W}" height="{H}" rx="10" fill="{C["bg"]}" stroke="{C["frame"]}"/>'
       f'<text x="30" y="32" font-size="12" fill="{C["dot"]}">{USER} / card.svg · updated {date.today()}</text>'
       + "".join(out) + "</svg>")
open("card.svg", "w").write(svg)
print("card.svg", H, "px tall")
