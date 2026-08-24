# README Redesign — Four Variants

Four complete, GitHub-renderable profile README candidates for `PhongCT1105`, built on the `readme-redesign` branch. The root `README.md` is untouched. Open each folder to see the variant exactly as GitHub renders it.

| # | Variant | Preview | Summary | Audience | Motion |
|---|---------|---------|---------|----------|--------|
| 01 | **Terminal / Systems** | [`01-terminal/`](./01-terminal) | Animated terminal hero that types `whoami` → focus → featured projects; command/output project cards | AI systems, infra, on-device & distributed roles | Medium |
| 02 | **Minimal Dark / Recruiter Dashboard** | [`02-minimal-dark/`](./02-minimal-dark) | Premium dark dashboard: hero with sweeping accent + focus meters, six scannable project cards | Default job-search profile; recruiters | Low |
| 03 | **Neon Glow / AI Builder** | [`03-neon-glow/`](./03-neon-glow) | Rotating neon gradient border, glow-pulse name, drifting network signal, flagship-project storytelling | Startups, AI community, personal brand | Medium-high |
| 04 | **Clean Professional / Research + Engineering** | [`04-clean-professional/`](./04-clean-professional) | Light-first (with dark counterpart via `<picture>`), journal-style project entries, one drawing accent line | Established companies, research groups | Very low |

## Trade-offs

**01 Terminal** — most memorable for systems/infra reviewers; the typing hero carries real content (identity, focus, project list). Slightly slower to scan than 02 for a non-technical recruiter.

**02 Minimal Dark** — fastest 5-second read: name, role, status, six projects with one-line value props. The safest default. Least distinctive of the four.

**03 Neon Glow** — strongest visual identity; risks feeling loud for conservative companies. Motion is layered (border, glow, particles) but each layer is slow.

**04 Clean Professional** — only variant designed light-first with a true dark counterpart; reads like a research portfolio. Minimal wow-factor by design.

## Structure

```text
readme-variants/   the four candidate READMEs (this folder)
assets/            generated SVG assets (per-variant + shared)
scripts/           generate_assets.py · validate_readmes.py
```

Regenerate assets with `python scripts/generate_assets.py`; validate everything with `python scripts/validate_readmes.py`.
