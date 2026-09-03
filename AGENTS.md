# AGENTS.md

Pixeltable is an OLTP database for multimodal AI. Media, AI outputs, and app state live in one hosted
database at `pxt://<org>:<db>`. To build and deploy an app, follow `CLOUD_QUICKSTART.md`;
`AGENT_PROMPT.md` has example apps to pick from.

- Add the skill for the API and schema DSL: `npx skills add pixeltable/pixeltable-skill`.
- The CLI is self-documenting: start at `pxt --help`. Docs: https://docs.pixeltable.com (any page
  takes a `.md` suffix).
