---
name: qwerty-preset
description: Run a SpinDoctor preset (qc-001..qc-241)
---

Run SpinDoctor preset the text the user typed after the command (<preset-id> [name=value ...]) with the `spindoctor_run_preset` tool (preset id plus optional name=value overrides; use
`spindoctor_list_presets` to find one). Summarise each step and give the TXT/PDF report paths. Classical simulation only.

If those tools are not available (for example when the MCP server is disabled or not approved), follow the spindoctor-qwerty skill and run its CLI, `scripts/spindoctor_cli.py` in the skill's folder, with `python3` (`python` on Windows).
