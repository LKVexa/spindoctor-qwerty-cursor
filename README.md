# SpinDoctor Qwerty for Cursor

**Cursor plugin for the SpinDoctor 3.1.2 quantum-circuit simulator.** It adds a skill, a rule, a helper agent, four commands and
a local MCP server with six tools to [Cursor](https://cursor.com/docs/plugins) (IDE agent and CLI): build and run `q.*` circuits
(1-298 logical qubits), run the 241 built-in presets, process folders of command files with `q.folder`, test theories from files,
pasted text or the conversation itself, and get TXT, PDF, JSON and CSV reports. Everything runs locally in a bundled,
standard-library-only Python engine.

> **Honest limits:** SpinDoctor is a **classical** FP64 simulator running on your computer. It is not a quantum computer, does not
> connect to quantum hardware and gives no quantum speed-up or advantage. Registers hold 1-298 logical qubits, but one entangled
> group (factor) is limited to 59 qubits and dense factors to the memory budget (2^n x 16 bytes); registers wider than 29 qubits
> sample in basis Z only. Histograms come from seeded Born sampling. Requires **Python 3.8+** (no packages).

Version **1.1.0** (engine 1.1.0, "SpinDoctor 3.1.2 parity"). Author: RUSSELL PHILIP SMITHSON. License: GPL-3.0-or-later.

## What's in the plugin

The repo root is a **Cursor Plugin** (`.cursor-plugin/plugin.json`), the format that carries rules, agents and commands as well
as skills and MCP servers ([plugins reference](https://cursor.com/docs/reference/plugins)). Components are found by Cursor's
folder-based discovery.

| Part | File | What it does |
|---|---|---|
| Manifest | `.cursor-plugin/plugin.json` | Name, version, description, author, homepage, repository, license, keywords |
| MCP server | `mcp.json` | Starts `python3 ${CURSOR_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py` (Cursor expands `${CURSOR_PLUGIN_ROOT}`, not the standard `${PLUGIN_ROOT}`) |
| Skill | `skills/spindoctor-qwerty/` | Instructions, honesty rules, the engine and its CLI |
| Rule | `rules/spindoctor-qwerty.mdc` | Honesty rules, q.* grammar, function table and theory-testing steps; `alwaysApply: false` (the agent pulls it in when relevant) |
| Agent | `agents/qwerty-helper.md` | Runs scripts, presets, folders and theory tests and explains them |
| Commands | `commands/*.md` | `/qwerty-run`, `/qwerty-preset`, `/qwerty-functions`, `/qwerty-theory` |
| Local installer | `tools/install_local.py` | Copies the plugin into `~/.cursor/plugins/local/spindoctor-qwerty`; `--python` for Windows; `--uninstall` |

No hooks, no variables or secrets, no network access, no telemetry. Nothing runs until you use a command or the agent calls a tool.
Reports go to `~/spindoctor-workspace` (set `SPINDOCTOR_WORKSPACE` in `mcp.json` `env` to change it).

## Install

You need Cursor and Python 3.8+ (as `python3` on macOS/Linux; see Windows below).

**Local plugin (works today, any plan that allows local plugins):**

```sh
git clone https://github.com/LKVexa/spindoctor-qwerty-cursor
cd spindoctor-qwerty-cursor
python3 tools/install_local.py
```

Restart Cursor (or run **Developer: Reload Window**), open **Customize**, check that *spindoctor-qwerty* is listed with its skill,
rule, agent, commands and MCP server, and approve the MCP server when Cursor asks. Then ask the agent *"show the SpinDoctor
functions"*. The installer copies the files because Cursor skips symlinks in `~/.cursor/plugins/local` that point elsewhere. Run it
again after `git pull` to update; `python3 tools/install_local.py --uninstall` removes it. On Teams/Enterprise, local plugins need
the admin setting *Allow Local Plugin Imports*.

**Windows:** the python.org installer provides `python` and `py`, not `python3`: run `python tools/install_local.py --python python`
(or `--python py`, or a full path to `python.exe`). Only the installed copy is changed.

**Cursor CLI:** after the local install the CLI sees the same plugin; for a one-off session use
`cursor-agent --plugin-dir ~/.cursor/plugins/local/spindoctor-qwerty`.

**Team marketplace / Cursor Marketplace:** the repo is a single plugin with `.cursor-plugin/plugin.json` at the root, so a team admin
can add it to a team marketplace, or it can be submitted at cursor.com/marketplace/publish. It isn't listed there yet.

## Commands

| Command | What it does |
|---|---|
| `/qwerty-run <q.* commands>` | Runs q.* commands and summarises probabilities, counts and report paths |
| `/qwerty-preset <qc-NNN> [name=value ...]` | Runs one of the 241 presets |
| `/qwerty-functions [section] [filter]` | Shows the function table |
| `/qwerty-theory <file \| text \| "we discussed">` | Tests a theory and writes a theory test report |

Each command uses the `spindoctor_*` MCP tools. If the server is unavailable, it falls back to the skill's CLI,
`skills/spindoctor-qwerty/scripts/spindoctor_cli.py`.

## SpinDoctor Qwerty - plugin tools

| Function | What it does | Command to type |
|---|---|---|
| Function table (spindoctor_functions) | Show this table in chat | Ask: "show the SpinDoctor functions" or `/qwerty-functions` |
| Run a script (spindoctor_run_script) | Run any q.* lines above; returns results + TXT/JSON/CSV/PDF report paths | Ask: "run q.circuit new bell 2 / q.circuit add h 0 / ..." |
| Run a preset (spindoctor_run_preset) | Run qc-001..qc-241 with overrides | Ask: "run preset qc-067 with shots=64" |
| List presets (spindoctor_list_presets) | Search the 241 presets | Ask: "list presets about Grover" |
| Read a report (spindoctor_report) | List/read TXT reports (PDF/JSON paths alongside) | Ask: "show the newest SpinDoctor report" |
| Test a theory from a file (spindoctor_test_theory source=file) | Read a .txt/.md/.pdf/.py/.json/.csv/.q attachment, then hypothesis -> prediction -> q.* script -> run -> verdict + TXT/PDF theory report | Ask: "test the theory in C:/notes/theory.md" (the host must pass the file path/content) |
| Test a theory from text (spindoctor_test_theory source=text) | Same pipeline for pasted text | Ask: "test this theory: a Hadamard on \|0> gives 50/50" |
| Test the theory we discussed (spindoctor_test_theory source=chat) | The AI summarises the theory from the conversation (claims, assumptions, variables, prediction), you confirm, then it is tested; quoted excerpts go in the report under 'Source: chat history'. An exported chat transcript (.txt/.md/.json/.html) also works | Ask: "test the theory we discussed" or "test the theory in my exported chat C:/chats/conversation.json" |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)** (the exact table the tool shows):
circuits (`q.circuit`, including 298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register
(`q.tranche`), the procedural grid, presets and sequences, resource planning, math calculators, physics models, lessons, noise, error
correction, compilation, algorithms, inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

`spindoctor_test_theory` turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. In Cursor, @-mention the file or give its path on your computer.
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The plugin cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `skills/spindoctor-qwerty/examples/theory/`. The two sample
PDFs are stored as text; run `python3 skills/spindoctor-qwerty/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Testing

| Test | Command | Result for 1.1.0 |
|---|---|---|
| Host check (stand-in Cursor loader) | `python3 tests/cursor_host_check.py` | 12/12 checks, end-to-end 12/12 |

**host-simulated.** The real Cursor CLI (`cursor-agent` 2026.10.01, from the official installer) was installed on a Linux test
machine without signing in. It loads plugins only inside a signed-in session: `cursor-agent -p --plugin-dir <plugin>` answers
*"Authentication required"*, `cursor-agent mcp list` doesn't see plugin servers, and the Cursor IDE needs an account. No sign-in or
API key was used. So `tests/cursor_host_check.py` stands in for Cursor: it checks the manifest, component discovery and front matter
against the plugins reference, installs with `tools/install_local.py` into a throw-away home, discovers the installed copy the way
the reference describes, expands `${CURSOR_PLUGIN_ROOT}`, starts the MCP server and runs the full end-to-end suite through it.
Whether Cursor's agent picks the tools, rule and commands as intended isn't tested. Details in [E2E_RESULTS.md](E2E_RESULTS.md).

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). `.cursor-plugin/plugin.json` carries the license and author.
Cursor is a trademark of Anysphere, Inc.; this project is not affiliated with Anysphere.
