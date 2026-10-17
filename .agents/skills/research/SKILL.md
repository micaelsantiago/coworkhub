---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up the **`agente-pesquisa` background agent** to do the research, so you keep working while it reads. Give it the exact question, the relevant repository context, and any known primary sources. It writes the result under `docs/research/`.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it under `docs/research/`, using a descriptive kebab-case filename, and say where.
