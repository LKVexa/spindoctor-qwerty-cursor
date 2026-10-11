---
name: qwerty-functions
description: Show every SpinDoctor function as a table (Function | What it does | Command to type)
---

Call the `spindoctor_functions` tool (section and filter from: the text the user typed after the command ("[commands|gates|tools|presets|all] [filter]"); default section commands) and show the returned
Markdown table to the user verbatim.

If those tools are not available (for example when the MCP server is disabled or not approved), follow the spindoctor-qwerty skill and run its CLI, `scripts/spindoctor_cli.py` in the skill's folder, with `python3` (`python` on Windows).
