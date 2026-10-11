# Changelog

## 1.1.0 - 2026-10-10

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics (.qasm2/.circuit, skipped-file listing, compact status, 128 files /
  4 MiB / 128 commands / 4096 characters), CSV report copies and measurement-CSV fitting equations. All 241 presets replayed.
- New tools `spindoctor_functions` (in-chat function table) and `spindoctor_test_theory` (theory testing from a file, pasted text or
  the chat history, with TXT+JSON+PDF theory reports).
- The repo root is now the plugin (`.cursor-plugin/plugin.json`), ready for a team marketplace or Marketplace submission.
- New `tools/install_local.py`: copies the plugin into `~/.cursor/plugins/local/spindoctor-qwerty` (Cursor skips outside
  symlinks), `--python` for Windows (installed copy only), `--uninstall`, refuses folders it didn't create.
- New `/qwerty-preset` command; the commands' text no longer uses `$ARGUMENTS` (not part of Cursor's command format).
- Rule, skill, agent and commands updated for 3.1.2 (298-qubit limit, q.folder, theory testing with user confirmation); the rule
  now carries the q.* grammar and theory-testing steps.
- `mcp.json` keeps `${CURSOR_PLUGIN_ROOT}` (Cursor doesn't expand `${PLUGIN_ROOT}`) and sets UTF-8 and no-bytecode.
- Author, homepage and repository added to the manifest.
- Tests: Cursor stand-in host check (discovery, front matter, installer, end-to-end through the installed copy).
- License changed from MIT to GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `spindoctor-qwerty/` folder with `.cursor-plugin/plugin.json`, skill, rule, agent, 3 commands and `mcp.json`.
