---
name: qwerty-run
description: Run SpinDoctor q.* commands with the bundled classical simulator
---

Run these SpinDoctor q.* commands with the `spindoctor_run_script` tool (one command per line), then summarise the results,
the exact probabilities next to the sampled counts, and the TXT/PDF report paths:

the text the user typed after the command (<q.* commands separated by newlines>)

If those tools are not available (for example when the MCP server is disabled or not approved), follow the spindoctor-qwerty skill and run its CLI, `scripts/spindoctor_cli.py` in the skill's folder, with `python3` (`python` on Windows).

Remind the user that this is a classical FP64 simulation on their computer, not quantum hardware. Registers wider than
29 qubits (up to 298) sample in basis z only.
