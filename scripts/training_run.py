#!/usr/bin/env python3
"""TRAINING RUN — renders this profile's contribution history as a live
FlashML-style training job (training-run.svg).

Every number in the card is real:
  epoch     days since the GitHub account was created
  samples   contributions in the last 365 days
  acc       % of the last 52 weeks with at least one contribution
  loss      1 / (1 + avg daily contributions over the last 30 days)
  curve     weekly loss over the last 26 weeks
  restarts  gaps in the contribution year the "job" recovered from

Stdlib only. Animations are SMIL, and every element is fully visible at
t=0 — if a renderer ignores animation, the card still reads completely.
"""

import json
import os
import sys
import urllib.request
from datetime import date, datetime, timezone

LOGIN = os.environ.get("GH_LOGIN", "PhongCT1105")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "..", "training-run.svg")

# ---------------------------------------------------------------- data

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def metrics(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    counts = [d["contributionCount"] for d in days]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]

    created = datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    epoch = (datetime.now(timezone.utc) - created).days

    active_weeks = sum(1 for w in weekly[-52:] if w > 0)
    acc = round(100 * active_weeks / min(52, len(weekly)), 1)

    avg30 = sum(counts[-30:]) / 30
    loss = round(1 / (1 + avg30), 2)

    # current streak, tolerating an empty "today" (UTC morning)
    streak, run = 0, counts[:-1] if counts and counts[-1] == 0 else counts
    for c in reversed(run):
        if c == 0:
            break
        streak += 1

    # every maximal zero-run followed by activity = one survived restart
    restarts, in_gap = 0, False
    for c in counts:
        if c == 0:
            in_gap = True
        elif in_gap:
            restarts += 1
            in_gap = False

    return {
        "epoch": epoch,
        "samples": cal["totalContributions"],
        "acc": acc,
        "loss": loss,
        "streak": streak,
        "restarts": restarts,
        "last14": counts[-14:],
        "weekly26": weekly[-26:],
    }


# ----------------------------------------------------------------- svg

BG, EDGE, DIM, SLATE, TEXT = "#0b0d17", "#1e293b", "#334155", "#94a3b8", "#e2e8f0"
PURPLE, CYAN, GREEN, PINK = "#c084fc", "#22d3ee", "#4ade80", "#f472b6"
MONO = "ui-monospace, 'Cascadia Code', 'Fira Code', Menlo, monospace"


def text(x, y, s, fill=TEXT, size=13, anchor="start", weight="400", extra=""):
    return (f"<text x='{x}' y='{y}' fill='{fill}' font-size='{size}' font-weight='{weight}' "
            f"text-anchor='{anchor}' font-family=\"{MONO}\" {extra}>{s}</text>")


def bar(x, y, w, frac, color, label, value, note):
    fill_w = round(w * min(frac, 1.0), 1)
    return "".join([
        text(x, y + 9, label, SLATE, 12),
        f"<rect x='{x + 52}' y='{y}' width='{w}' height='10' rx='5' fill='{EDGE}'/>",
        f"<rect x='{x + 52}' y='{y}' width='{fill_w}' height='10' rx='5' fill='{color}'>"
        f"<animate attributeName='opacity' values='1;0.75;1' dur='3s' repeatCount='indefinite'/></rect>",
        text(x + 52 + w + 12, y + 10, value, TEXT, 13, weight="700"),
        text(x + 52 + w + 78, y + 10, note, DIM, 10),
    ])


def render(m):
    W, H = 920, 300
    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}' "
        f"role='img' aria-label='Live training-run card generated from real GitHub contribution data'>",
        f"<rect x='1' y='1' width='{W-2}' height='{H-2}' rx='12' fill='{BG}' stroke='{EDGE}'/>",
        # header
        text(28, 34, "⚡ zolli-labs/flashml", PURPLE, 14, weight="700"),
        text(218, 34, "· job: phong-profile", SLATE, 13),
        text(W - 28, 34, f"node: github-actions · epoch {m['epoch']}", CYAN, 13, anchor="end"),
        f"<line x1='24' y1='48' x2='{W-24}' y2='48' stroke='{EDGE}'/>",
        # sample lane: last 14 days of real contributions
        text(28, 74, "samples in · last 14 days", DIM, 10),
    ]

    lane_y, model_x = 100, 600
    peak = max(m["last14"] + [1])
    for i, c in enumerate(m["last14"]):
        cx = 40 + i * 34
        if c == 0:
            parts.append(f"<circle cx='{cx}' cy='{lane_y}' r='2' fill='{DIM}'/>")
        else:
            r = 3 + round(4 * c / peak, 1)
            parts.append(f"<circle cx='{cx}' cy='{lane_y}' r='{r}' fill='{GREEN}' opacity='0.9'/>")
    parts.append(text(40 + 14 * 34, lane_y + 5, "→  →", SLATE, 14))

    # dots flowing into the model (decorative; extra dots idle at the lane if SMIL is off)
    for i, delay in enumerate((0, 1.1, 2.2)):
        start_x = 60 + i * 120
        parts.append(
            f"<circle r='4' fill='{GREEN}'><animateMotion dur='3.3s' begin='{delay}s' repeatCount='indefinite' "
            f"path='M {start_x} {lane_y} L {model_x - 12} {lane_y}'/></circle>")

    # the model
    parts += [
        f"<rect x='{model_x}' y='{lane_y - 34}' width='104' height='68' rx='10' fill='#1a1030' stroke='{PURPLE}' stroke-width='1.5'>"
        f"<animate attributeName='stroke-opacity' values='1;0.45;1' dur='2.4s' repeatCount='indefinite'/></rect>",
        text(model_x + 52, lane_y - 8, "MODEL", PURPLE, 14, anchor="middle", weight="700"),
        text(model_x + 52, lane_y + 12, "FlashML", SLATE, 10, anchor="middle"),
        text(model_x + 124, lane_y - 2, "TRAINING", CYAN, 13, weight="700"),
    ]
    for i in range(3):  # ellipsis pulses, but is fully visible when static
        parts.append(
            f"<text x='{model_x + 196 + i * 9}' y='{lane_y - 2}' fill='{CYAN}' font-size='13' font-weight='700' "
            f"font-family=\"{MONO}\">.<animate attributeName='opacity' values='1;0.15;1' dur='1.8s' "
            f"begin='{i * 0.3}s' repeatCount='indefinite'/></text>")

    # metric bars (left) — real values, statically sized
    parts.append(bar(28, 168, 240, m["acc"] / 100, GREEN, "acc", f"{m['acc']}%", "weeks active, last 52"))
    parts.append(bar(28, 196, 240, m["loss"], PINK, "loss", f"{m['loss']}", "∝ 1 / daily activity, 30d"))

    # loss curve (right) — last 26 weeks, inverted, min-max normalized
    cx0, cy0, cw, ch = 560, 160, 320, 64
    losses = [1 / (1 + w) for w in m["weekly26"]] or [1.0]
    lo, hi = min(losses), max(losses)
    span = (hi - lo) or 1.0
    pts = [(cx0 + i * cw / max(len(losses) - 1, 1), cy0 + ch - ch * (1 - (l - lo) / span) * 0.9 - ch * 0.05)
           for i, l in enumerate(losses)]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    path_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    parts += [
        text(cx0, cy0 - 10, "loss // last 26 weeks (real data)", DIM, 10),
        f"<path d='{path_d} L {pts[-1][0]:.1f} {cy0 + ch} L {pts[0][0]:.1f} {cy0 + ch} Z' fill='{PURPLE}' opacity='0.12'/>",
        f"<polyline points='{poly}' fill='none' stroke='{PURPLE}' stroke-width='2'/>",
        f"<circle r='4' fill='{CYAN}'><animateMotion dur='6s' repeatCount='indefinite' path='{path_d}'/></circle>",
        # footer
        f"<line x1='24' y1='252' x2='{W-24}' y2='252' stroke='{EDGE}'/>",
        text(28, 276, f"samples: {m['samples']:,} contributions · uptime: {m['streak']}d streak", SLATE, 12),
        text(452, 276, f"✓ job survived {m['restarts']} machine restarts", GREEN, 12, weight="700"),
        f"<rect x='{W - 180}' y='266' width='7' height='13' fill='{CYAN}'>"
        f"<animate attributeName='opacity' values='1;0;1' dur='1.2s' repeatCount='indefinite'/></rect>",
        text(W - 28, 276, f"regenerated {date.today().isoformat()}", DIM, 10, anchor="end"),
        "</svg>",
    ]
    return "".join(parts)


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("GITHUB_TOKEN is required")
    m = metrics(fetch())
    svg = render(m)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"training-run.svg written · {json.dumps({k: v for k, v in m.items() if k not in ('last14', 'weekly26')})}")
