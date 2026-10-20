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
    ("forging", "prismgit, crystalctl"), ("forged", "livestate, no-swipe-overview"),
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
  public: repositories(ownerAffiliations: OWNER, first: 100, isFork: false, privacy: PUBLIC) {{ nodes {{
    languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{ edges {{ size node {{ name }} }} }} }} }}
  contributionsCollection {{ contributionCalendar {{ totalContributions
    weeks {{ contributionDays {{ contributionCount weekday }} }} }} }} }} }}""")
cal = u["contributionsCollection"]["contributionCalendar"]
STATS = [("repos", str(u["repositories"]["totalCount"])),
         ("stars", str(sum(r["stargazerCount"] for r in u["repositories"]["nodes"]))),
         ("contributions", str(cal["totalContributions"])),
         ("followers", str(u["followers"]["totalCount"]))]

# bytes per language over public repos only, so the card never reveals what private repos contain
LANGS = {}
for repo in u["public"]["nodes"]:
    for e in repo["languages"]["edges"]:
        LANGS[e["node"]["name"]] = LANGS.get(e["node"]["name"], 0) + e["size"]
TOP = sorted(LANGS.items(), key=lambda kv: -kv[1])[:8]

out, y = [], 0


def text(x, y, spans, cols=None, size=13, into=None):
    """One line; textLength pins it to `cols` chars so leaders line up in any monospace font."""
    fit = f' textLength="{cols * CW:.1f}" lengthAdjust="spacingAndGlyphs"' if cols else ""
    body = "".join(f'<tspan fill="{c}"{" font-weight=\"bold\"" if b else ""}>{escape(s)}</tspan>' for s, c, b in spans)
    (out if into is None else into).append(f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve"{fit}>{body}</text>')


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

# full-width sections share the panel's right edge
RIGHT = RX + COLS * CW
gcols = (RIGHT - 30) / CW


def wide_rule(y, label):
    head = f"- {label} "
    text(30, y, [(head, C["head"], True), ("─" * (round(gcols) - len(head)), C["dim"], False)], gcols)


# languages: two columns of ASCII bars, longest bar = most used
y = panel_bottom + LH * 3
wide_rule(y, "languages")
total = sum(LANGS.values()) or 1
LC, BAR = 51, 30  # chars per column, bar cells
col_w = (RIGHT - 30 - 30) / 2
half = (len(TOP) + 1) // 2
for i, (name, size) in enumerate(TOP):
    pct = 100 * size / total
    filled = max(1, round(BAR * size / TOP[0][1]))
    x = 30 + (i // half) * (col_w + 30)
    ly = y + LH * (1 + i % half) + 4
    text(x, ly, [(name.lower().ljust(14), C["key"], True), ("█" * filled, C["head"], False),
                 ("░" * (BAR - filled), C["dim"], False), (f"{pct:.1f}%".rjust(LC - 14 - BAR), C["val"], False)], LC)
y += LH * (half + 1) + 4

# contribution grid, stretched to the same margins as the panel above
y += LH * 2
wide_rule(y, "contributions")
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

def save(path, body, height, caption=None, width=900):
    caption = (f'<text x="30" y="32" font-size="12" fill="{C["dot"]}">{escape(caption)}</text>' if caption else "")
    with open(path, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
                f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'DejaVu Sans Mono\',monospace">'
                f'<rect width="{width}" height="{height}" rx="10" fill="{C["bg"]}" stroke="{C["frame"]}"/>'
                + caption + "".join(body) + "</svg>")
    print(path, height, "px tall")


save("card.svg", out, y + 30, f"{USER} / card.svg · updated {date.today()}")

# project cards for the README: same look as the main card, one SVG per repo so each can link to it
PROJECTS = [
    ("livestate", "demo: plataforma de bienes raíces con pagos y chat en tiempo real", [
        ("stack", "Java 17 · Spring Boot · Angular · MySQL 8 · Stripe · JWT · WebSockets · Docker"),
        ("backend/", "Spring Boot + JPA + JWT + Stripe + WebSockets"),
        ("frontend/", "Angular + TypeScript + RxJS"),
        ("docker/", "MySQL 8 + Docker Compose"),
        ("ci/", "GitHub Actions + Testcontainers")]),
    ("prismgit", "dashboard que narra la historia visual de un repo Git", [
        ("stack", "Java 21 · Spring Boot 3.4 · Angular 19 · JGit · Flyway · PostgreSQL · Swagger · Docker"),
        ("api", "14 endpoints REST: repos, commits, analytics, stories"),
        ("dashboard", "stats, timelines, heatmaps, story viewer"),
        ("sync", "JGit + GitHub API, repos locales o remotos"),
        ("tests", "100+ con JUnit/Mockito y Jasmine")]),
    ("crystalctl", "gestor local de tu stack: CLI + panel estilo terminal ASCII", [
        ("stack", "Python · systemd · HTML/CSS · apt / dnf / pacman / zypper"),
        ("web", "Apache · Nginx · PHP-FPM"),
        ("sql", "MariaDB · MySQL · PostgreSQL"),
        ("nosql", "MongoDB · Redis / Valkey · Memcached"),
        ("panel", "127.0.0.1 + token por arranque, acciones root vía pkexec")]),
    ("no-swipe-overview", "extensión de GNOME Shell que bloquea el swipe al overview", [
        ("stack", "JavaScript · GJS · GNOME 48")]),
]
PCOLS = round((900 - 60) / CW)
os.makedirs("projects", exist_ok=True)
head = []
text(30, 30, [("- projects ", C["head"], True), ("─" * (PCOLS - 11), C["dim"], False)], PCOLS, into=head)
save("projects/header.svg", head, 46)
for name, desc, rows in PROJECTS:
    body = []
    # a "demo:" description gets its own red tag, so client demos read differently from tools
    tag, _, rest = desc.partition(": ") if desc.startswith("demo") else ("", "", desc)
    text(30, 36, [("[ ", C["dot"], False), (name, C["key"], True), (" ]", C["dot"], False)]
         + ([("  [", C["dot"], False), (tag.upper(), C["head"], True), ("]", C["dot"], False)] if tag else [])
         + [("  " + rest, C["val"], False)], into=body)
    text(30, 56, [("─" * PCOLS, C["dim"], False)], PCOLS, into=body)
    py = 56
    for k, v in rows:
        py += LH
        dots = PCOLS - len(k) - len(v) - 4
        assert dots > 0, (name, k)
        text(30, py, [(k, C["key"], True), (": ", C["dot"], False), ("." * dots, C["dot"], False),
                      ("  " + v, C["val"], False)], PCOLS, into=body)
    save(f"projects/{name}.svg", body, py + 24)
