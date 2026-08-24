#!/usr/bin/env python3
"""Generate all custom SVG assets for the readme-variants profile redesign.

Usage:
    python scripts/generate_assets.py

Pure standard library. Every asset is a standalone .svg file that GitHub can
serve as an image. Animation uses CSS keyframes / SMIL embedded *inside* each
SVG file (no external CSS, no JS, no external fonts), which GitHub's camo
image proxy preserves.

All editable text/data lives in the CONFIG section below.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# CONFIG — edit text, colors and timings here
# ---------------------------------------------------------------------------

NAME = "Phong Cao"
HANDLE = "PhongCT1105"
ROLE_LINE = "Software Engineer • ML/AI Systems • On-Device & Distributed AI"
EDU_LINE = "B.S. Computer Science + M.S. Artificial Intelligence @ WPI · 2027"
STATUS_LINE = "OPEN TO 2027 NEW-GRAD SWE / ML / AI ROLES"

TERMINAL_SEQUENCE = [
    ("cmd", "whoami"),
    ("out", "Phong Cao — CS + MS AI @ WPI '27"),
    ("cmd", "cat focus.txt"),
    ("out", "AI systems · ML infrastructure · on-device inference"),
    ("cmd", "ls projects/ --featured"),
    ("out", "flashml/   harbor/   on-device-assistant/   hallucination-study/"),
    ("cmd", "status"),
    ("dots", "building · learning · shipping"),
]

MINIMAL_CHIPS = ["Python", "PyTorch", "TypeScript", "Distributed ML", "On-Device AI"]
MINIMAL_FOCUS = ["ML Infrastructure", "AI Engineering", "Full-Stack Systems"]

NEON_CHIPS = [("LLM Systems", "#c084fc"), ("ML Infra", "#22d3ee"), ("Agents", "#4ade80")]

CLEAN_ROLE = "SOFTWARE ENGINEER · ML / AI SYSTEMS"

OUT_DIRS = {
    "terminal": "assets/terminal",
    "minimal": "assets/minimal-dark",
    "neon": "assets/neon",
    "clean": "assets/clean",
    "shared": "assets/shared",
}

MONO = "ui-monospace,'Cascadia Code','SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
SERIF = "Georgia,'Times New Roman',serif"


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    size = os.path.getsize(path)
    print(f"  wrote {path}  ({size/1024:.1f} KB)")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pct(t: float, total: float) -> str:
    return f"{100.0 * t / total:.3f}%"


# ---------------------------------------------------------------------------
# 1. Terminal hero — typed command sequence, blinking cursor, pulsing status
# ---------------------------------------------------------------------------

def terminal_hero() -> str:
    W, H = 920, 430
    LOOP = 14.0           # seconds for the full loop
    CW = 9.05             # monospace advance width @15px
    FS = 15
    LH = 30
    X0, Y0 = 36, 96
    TYPE_CPS = 28         # typing speed, chars per second
    GAP_AFTER_CMD = 0.35
    GAP_AFTER_OUT = 0.55

    green = "#3fdc84"
    cyan = "#67e8f9"
    text = "#e6edf3"
    dim = "#9aa4b2"
    amber = "#fbbf24"

    css: list[str] = []
    body: list[str] = []
    t = 0.9  # initial pause
    line_idx = 0
    char_uid = 0

    for kind, raw in TERMINAL_SEQUENCE:
        y = Y0 + line_idx * LH
        if kind == "cmd":
            dur = len(raw) / TYPE_CPS
            # prompt appears when the line starts
            pid = f"p{line_idx}"
            css.append(
                f".{pid}{{opacity:0;animation:{pid} {LOOP}s linear infinite}}"
                f"@keyframes {pid}{{0%,{pct(t-0.01, LOOP)}{{opacity:0}}"
                f"{pct(t, LOOP)},96%{{opacity:1}}100%{{opacity:0}}}}"
            )
            body.append(
                f'<text class="{pid}" x="{X0}" y="{y}" font-family="{MONO}" '
                f'font-size="{FS}" fill="{green}">❯</text>'
            )
            # each character reveals on its own keyframe
            for i, ch in enumerate(raw):
                ct = t + (i + 1) / TYPE_CPS
                cid = f"c{char_uid}"
                char_uid += 1
                css.append(
                    f".{cid}{{opacity:0;animation:{cid} {LOOP}s linear infinite}}"
                    f"@keyframes {cid}{{0%,{pct(ct-0.01, LOOP)}{{opacity:0}}"
                    f"{pct(ct, LOOP)},96%{{opacity:1}}100%{{opacity:0}}}}"
                )
                x = X0 + 22 + i * CW
                body.append(
                    f'<text class="{cid}" x="{x:.1f}" y="{y}" font-family="{MONO}" '
                    f'font-size="{FS}" fill="{text}">{esc(ch)}</text>'
                )
            # cursor gated to this line's typing window, blinking inside it
            cur_id = f"cur{line_idx}"
            cur_end = t + dur + GAP_AFTER_CMD
            css.append(
                f".{cur_id}{{opacity:0;animation:{cur_id} {LOOP}s linear infinite}}"
                f"@keyframes {cur_id}{{0%,{pct(t-0.01, LOOP)}{{opacity:0}}"
                f"{pct(t, LOOP)},{pct(cur_end, LOOP)}{{opacity:1}}"
                f"{pct(cur_end+0.01, LOOP)},100%{{opacity:0}}}}"
            )
            cx = X0 + 22 + len(raw) * CW + 3
            body.append(
                f'<g class="{cur_id}"><rect class="blink" x="{cx:.1f}" y="{y-12}" '
                f'width="8" height="16" fill="{green}"/></g>'
            )
            t += dur + GAP_AFTER_CMD
        elif kind == "out":
            oid = f"o{line_idx}"
            css.append(
                f".{oid}{{opacity:0;animation:{oid} {LOOP}s linear infinite}}"
                f"@keyframes {oid}{{0%,{pct(t, LOOP)}{{opacity:0}}"
                f"{pct(t+0.3, LOOP)},96%{{opacity:1}}100%{{opacity:0}}}}"
            )
            body.append(
                f'<text class="{oid}" x="{X0}" y="{y}" font-family="{MONO}" '
                f'font-size="{FS}" fill="{dim}">{esc(raw)}</text>'
            )
            t += GAP_AFTER_OUT
        elif kind == "dots":
            oid = f"o{line_idx}"
            css.append(
                f".{oid}{{opacity:0;animation:{oid} {LOOP}s linear infinite}}"
                f"@keyframes {oid}{{0%,{pct(t, LOOP)}{{opacity:0}}"
                f"{pct(t+0.3, LOOP)},96%{{opacity:1}}100%{{opacity:0}}}}"
            )
            parts = raw.split(" · ")
            x = X0
            chunks = []
            for j, p in enumerate(parts):
                color = [green, cyan, amber][j % 3]
                chunks.append(
                    f'<circle class="pulse" cx="{x+5}" cy="{y-5}" r="4.5" fill="{color}"/>'
                    f'<text x="{x+16}" y="{y}" font-family="{MONO}" font-size="{FS}" '
                    f'fill="{text}">{esc(p)}</text>'
                )
                x += 16 + len(p) * CW + 30
            body.append(f'<g class="{oid}">{"".join(chunks)}</g>')
            t += GAP_AFTER_OUT
        line_idx += 1

    # final resting cursor after the sequence completes
    y = Y0 + line_idx * LH
    fid = "curend"
    css.append(
        f".{fid}{{opacity:0;animation:{fid} {LOOP}s linear infinite}}"
        f"@keyframes {fid}{{0%,{pct(t, LOOP)}{{opacity:0}}"
        f"{pct(t+0.2, LOOP)},96%{{opacity:1}}100%{{opacity:0}}}}"
    )
    body.append(
        f'<g class="{fid}"><text x="{X0}" y="{y}" font-family="{MONO}" font-size="{FS}" '
        f'fill="{green}">❯</text>'
        f'<rect class="blink" x="{X0+22}" y="{y-12}" width="8" height="16" fill="{green}"/></g>'
    )

    shared_css = (
        ".blink{animation:blink 1.1s steps(2,start) infinite}"
        "@keyframes blink{to{visibility:hidden}}"
        ".pulse{animation:pulse 2.4s ease-in-out infinite}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}"
        ".lamp{animation:pulse 3s ease-in-out infinite}"
        ".scan{animation:scan 9s linear infinite}"
        "@keyframes scan{0%{transform:translateY(0)}100%{transform:translateY(390px)}}"
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated terminal introducing Phong Cao: software engineer focused on AI systems, ML infrastructure and on-device inference. Featured projects: FlashML, Harbor, On-Device Assistant, Hallucination Study.">
<style>{shared_css}{''.join(css)}</style>
<rect width="{W}" height="{H}" rx="14" fill="#0a0e14"/>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="13.5" fill="none" stroke="#1f2937"/>
<rect width="{W}" height="40" rx="14" fill="#111825"/>
<rect y="26" width="{W}" height="14" fill="#111825"/>
<circle cx="24" cy="20" r="6" fill="#ff5f57"/>
<circle cx="46" cy="20" r="6" fill="#febc2e"/>
<circle class="lamp" cx="68" cy="20" r="6" fill="#28c840"/>
<text x="{W//2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#8b949e">phong@wpi — ~/portfolio</text>
<g class="scan" opacity=".04"><rect x="1" y="44" width="{W-2}" height="3" fill="#3fdc84"/></g>
{''.join(body)}
</svg>
"""


def terminal_divider() -> str:
    return sweep_divider("#3fdc84", "#67e8f9")


# ---------------------------------------------------------------------------
# 2. Minimal-dark dashboard hero — calm, recruiter-first, low motion
# ---------------------------------------------------------------------------

def minimal_hero() -> str:
    W, H = 920, 312
    bg = "#0d1117"
    border = "#21262d"
    fg = "#f0f6fc"
    dim = "#8d96a0"
    accent = "#4493f8"
    green = "#3fb950"

    chips = []
    x = 40
    for label in MINIMAL_CHIPS:
        w = 24 + len(label) * 7.6
        chips.append(
            f'<rect x="{x}" y="196" width="{w:.0f}" height="30" rx="15" fill="#161b22" stroke="{border}"/>'
            f'<text x="{x + w/2:.0f}" y="215" text-anchor="middle" font-family="{SANS}" '
            f'font-size="12.5" fill="#c9d1d9">{esc(label)}</text>'
        )
        x += w + 10

    bars = []
    for i, label in enumerate(MINIMAL_FOCUS):
        y = 84 + i * 52
        delay = 0.4 + i * 0.35
        bars.append(
            f'<text x="640" y="{y}" font-family="{SANS}" font-size="12.5" fill="{dim}">{esc(label)}</text>'
            f'<rect x="640" y="{y+10}" width="220" height="6" rx="3" fill="#161b22"/>'
            f'<rect class="fill" style="animation-delay:{delay}s" x="640" y="{y+10}" width="220" height="6" rx="3" fill="url(#barGrad)"/>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Phong Cao — {esc(ROLE_LINE)}. {esc(STATUS_LINE)}.">
<style>
.fill{{transform:scaleX(0);transform-origin:640px 0;animation:fill 2.2s cubic-bezier(.2,.7,.3,1) forwards}}
@keyframes fill{{to{{transform:scaleX(1)}}}}
.dot{{animation:dot 2.6s ease-in-out infinite}}
@keyframes dot{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
</style>
<defs>
<linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{green}"/>
</linearGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{accent}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{accent}"/>
  <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
  <animateTransform attributeName="gradientTransform" type="translate" from="-1 0" to="1 0" dur="5s" repeatCount="indefinite"/>
</linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="16" fill="{bg}"/>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="15.5" fill="none" stroke="{border}"/>
<circle class="dot" cx="48" cy="52" r="5" fill="{green}"/>
<text x="62" y="57" font-family="{MONO}" font-size="12" letter-spacing="1.5" fill="{green}">{esc(STATUS_LINE)}</text>
<text x="40" y="118" font-family="{SANS}" font-size="46" font-weight="700" fill="{fg}">{esc(NAME)}</text>
<rect x="42" y="134" width="300" height="3" rx="1.5" fill="#21262d"/>
<rect x="42" y="134" width="300" height="3" rx="1.5" fill="url(#sweep)"/>
<text x="40" y="166" font-family="{SANS}" font-size="16.5" fill="#c9d1d9">{esc(ROLE_LINE)}</text>
{''.join(chips)}
<text x="40" y="266" font-family="{SANS}" font-size="13" fill="{dim}">{esc(EDU_LINE)}</text>
<line x1="600" y1="48" x2="600" y2="264" stroke="{border}"/>
<text x="640" y="58" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{dim}">FOCUS</text>
{''.join(bars)}
</svg>
"""


def minimal_divider() -> str:
    return sweep_divider("#4493f8", "#3fb950")


# ---------------------------------------------------------------------------
# 3. Neon hero — rotating gradient border, glow pulse, drifting network
# ---------------------------------------------------------------------------

def neon_hero() -> str:
    W, H = 920, 390
    violet, cyan, green = "#c084fc", "#22d3ee", "#4ade80"

    # deterministic pseudo-network (hand-placed, right panel)
    nodes = [
        (700, 90), (780, 140), (856, 96), (734, 200), (820, 236),
        (688, 282), (776, 318), (860, 286), (738, 120), (852, 180),
    ]
    edges = [(0, 1), (1, 2), (1, 3), (3, 4), (4, 7), (3, 5), (5, 6), (6, 7), (0, 8), (2, 9), (4, 9), (8, 3)]
    net = []
    for a, b in edges:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        net.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#2b3350" stroke-width="1"/>')
    for i, (x, y) in enumerate(nodes):
        color = [violet, cyan, green][i % 3]
        dur = 6 + (i % 5)
        dx = 6 - (i % 4) * 3
        dy = 4 - (i % 3) * 4
        net.append(
            f'<circle cx="{x}" cy="{y}" r="{3.5 + (i%3)}" fill="{color}" opacity=".85">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0; {dx} {dy}; 0 0" dur="{dur}s" repeatCount="indefinite"/></circle>'
        )
    # signal pulse traveling across the network
    net.append(
        f'<circle r="3" fill="#ffffff" opacity=".9">'
        f'<animateMotion path="M700,90 L780,140 L734,200 L820,236 L860,286 L776,318 L688,282 L734,200 L700,90" '
        f'dur="9s" repeatCount="indefinite"/></circle>'
    )

    chips = []
    x = 46
    for label, color in NEON_CHIPS:
        w = 30 + len(label) * 8.2
        chips.append(
            f'<rect x="{x}" y="238" width="{w:.0f}" height="32" rx="16" fill="none" stroke="{color}" stroke-opacity=".65"/>'
            f'<circle class="pulse" cx="{x+16}" cy="254" r="4" fill="{color}"/>'
            f'<text x="{x+26}" y="259" font-family="{SANS}" font-size="13" fill="{color}">{esc(label)}</text>'
        )
        x += w + 12

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Neon banner: Phong Cao, AI builder — LLM systems, ML infrastructure and agents. {esc(EDU_LINE)}.">
<style>
.glow{{animation:glow 4.5s ease-in-out infinite}}
@keyframes glow{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
.pulse{{animation:pulse 2.2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
</style>
<defs>
<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{violet}"/><stop offset=".5" stop-color="{cyan}"/><stop offset="1" stop-color="{green}"/>
  <animateTransform attributeName="gradientTransform" type="rotate" from="0 .5 .5" to="360 .5 .5" dur="9s" repeatCount="indefinite"/>
</linearGradient>
<filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="7"/>
</filter>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="#0b0d17"/>
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="16" fill="none" stroke="url(#ring)" stroke-width="2.5"/>
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="16" fill="none" stroke="url(#ring)" stroke-width="5" opacity=".28" filter="url(#soft)"/>
<text class="glow" x="44" y="118" font-family="{SANS}" font-size="56" font-weight="800" fill="{violet}" filter="url(#soft)">{esc(NAME.upper())}</text>
<text x="44" y="118" font-family="{SANS}" font-size="56" font-weight="800" fill="#f5f3ff">{esc(NAME.upper())}</text>
<text x="46" y="156" font-family="{MONO}" font-size="15" fill="{cyan}">@{HANDLE} — I build AI systems that ship.</text>
<text x="46" y="196" font-family="{SANS}" font-size="15" fill="#a5b4fc">{esc(EDU_LINE)}</text>
{''.join(chips)}
<text x="46" y="330" font-family="{MONO}" font-size="12.5" fill="#6b7394">distributed training · on-device inference · LLM evaluation · agent infrastructure</text>
<g>{''.join(net)}</g>
</svg>
"""


def neon_divider() -> str:
    return sweep_divider("#c084fc", "#22d3ee")


# ---------------------------------------------------------------------------
# 4. Clean professional hero — light-first, dark counterpart, minimal motion
# ---------------------------------------------------------------------------

def clean_hero(dark: bool) -> str:
    W, H = 920, 236
    if dark:
        bg, fg, sub, accent, hair = "#0d1117", "#f0f6fc", "#9aa4b2", "#58a6ff", "#21262d"
    else:
        bg, fg, sub, accent, hair = "#ffffff", "#111827", "#4b5563", "#2563eb", "#e5e7eb"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Phong Cao — {esc(CLEAN_ROLE)}. {esc(EDU_LINE)}.">
<style>
.draw{{stroke-dasharray:120;stroke-dashoffset:120;animation:draw 2.4s cubic-bezier(.2,.7,.3,1) forwards .4s}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.dot{{animation:dot 3.2s ease-in-out infinite}}
@keyframes dot{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
</style>
<rect width="{W}" height="{H}" fill="{bg}"/>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" fill="none" stroke="{hair}"/>
<text x="60" y="102" font-family="{SERIF}" font-size="46" fill="{fg}">{esc(NAME)}</text>
<line class="draw" x1="62" y1="120" x2="182" y2="120" stroke="{accent}" stroke-width="3"/>
<text x="60" y="152" font-family="{SANS}" font-size="14" letter-spacing="2.5" fill="{sub}">{esc(CLEAN_ROLE)}</text>
<text x="60" y="182" font-family="{SANS}" font-size="13.5" fill="{sub}">{esc(EDU_LINE)}</text>
<circle class="dot" cx="66" cy="205" r="4" fill="{accent}"/>
<text x="78" y="209" font-family="{SANS}" font-size="12.5" fill="{sub}">Currently building distributed ML tooling and on-device inference systems</text>
<line x1="700" y1="40" x2="700" y2="196" stroke="{hair}"/>
<text x="730" y="76" font-family="{SANS}" font-size="12" letter-spacing="2" fill="{sub}">FOCUS</text>
<text x="730" y="106" font-family="{SANS}" font-size="13.5" fill="{fg}">ML Infrastructure</text>
<text x="730" y="132" font-family="{SANS}" font-size="13.5" fill="{fg}">On-Device AI</text>
<text x="730" y="158" font-family="{SANS}" font-size="13.5" fill="{fg}">LLM Evaluation</text>
<text x="730" y="184" font-family="{SANS}" font-size="13.5" fill="{fg}">Agent Systems</text>
</svg>
"""


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------

def sweep_divider(c1: str, c2: str) -> str:
    W, H = 920, 6
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{c1}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{c2}"/>
  <stop offset="1" stop-color="{c1}" stop-opacity="0"/>
  <animateTransform attributeName="gradientTransform" type="translate" from="-1 0" to="1 0" dur="6s" repeatCount="indefinite"/>
</linearGradient>
</defs>
<rect width="{W}" height="2" y="2" rx="1" fill="#30363d" opacity=".5"/>
<rect width="{W}" height="2" y="2" rx="1" fill="url(#g)"/>
</svg>
"""


def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    print("Generating assets...")
    write(f"{OUT_DIRS['terminal']}/hero-terminal.svg", terminal_hero())
    write(f"{OUT_DIRS['terminal']}/divider.svg", terminal_divider())
    write(f"{OUT_DIRS['minimal']}/hero-dashboard.svg", minimal_hero())
    write(f"{OUT_DIRS['minimal']}/divider.svg", minimal_divider())
    write(f"{OUT_DIRS['neon']}/hero-neon.svg", neon_hero())
    write(f"{OUT_DIRS['neon']}/divider.svg", neon_divider())
    write(f"{OUT_DIRS['clean']}/hero-light.svg", clean_hero(dark=False))
    write(f"{OUT_DIRS['clean']}/hero-dark.svg", clean_hero(dark=True))
    print("Done.")


if __name__ == "__main__":
    main()
