---
name: qwerty-theory
description: Test a theory with the SpinDoctor simulator (file path, pasted text, or 'the theory we discussed')
---

Test this theory with the `spindoctor_test_theory` tool: the text the user typed after the command (<file path | theory text | 'we discussed'>)

- File path: use source=file (action=extract first). Pasted text: source=text.
- If it refers to our conversation: summarise the theory from the chat (claims, assumptions, variables, measurable
  prediction), show the summary and get my confirmation, then use source=chat with short verbatim excerpts.
- Restate the hypothesis, give a measurable prediction, write the q.* script and checks, run it (action=run), and report
  the verdict, observed vs predicted numbers, and the TXT/PDF theory report paths with the limits (classical simulation;
  1-298 logical qubits, 59 per entangled factor, dense factors limited by memory; shot noise).
- The plugin cannot read the chat or attachments by itself; very long chats may be truncated by the context window.

If those tools are not available (for example when the MCP server is disabled or not approved), follow the spindoctor-qwerty skill and run its CLI, `scripts/spindoctor_cli.py` in the skill's folder, with `python3` (`python` on Windows).
