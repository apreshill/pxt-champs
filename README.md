# pxt-champs

Pixeltable Cloud for beta testers. Pixeltable is an OLTP database for multimodal AI: your media, its
AI outputs, and app state live in one hosted database, addressed as `pxt://<your-org>:<db>`.

## Setup

```bash
uv sync                       # or, without cloning: pip install 'pixeltable[serve]'
```

Put your Cloud API key (dashboard → API Keys) in `~/.pixeltable/config.toml`:

```toml
[pixeltable]
api_key = 'your-api-key'
```

## Two ways in

- **Step by step:** run `01_setup.ipynb` then `02_cloud_tables.ipynb`. Creates a hosted database and
  builds a multimodal table you can see in `pxt dashboard`.
- **On your own, with an agent:** fill in and hand `AGENT_PROMPT.md` to your coding agent. It builds
  and deploys a real app, following `CLOUD_QUICKSTART.md`.

## Links

- Docs: https://docs.pixeltable.com (any page takes a `.md` suffix)
- CLI: https://docs.pixeltable.com/platform/cli.md · Dashboard: https://docs.pixeltable.com/platform/dashboard.md
- Agent skill: `npx skills add pixeltable/pixeltable-skill`
