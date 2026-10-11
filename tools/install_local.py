# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for Cursor
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Install this plugin into Cursor's local plugin folder, ~/.cursor/plugins/local/spindoctor-qwerty (Cursor IDE and CLI).

Cursor loads plugins placed there after a restart or "Developer: Reload Window". It skips symlinks that point outside
that folder, so this script COPIES the plugin files (manifest, mcp.json, skills, rules, agents, commands, docs; not tests/
or tools/) and writes a marker file. Standard library only, Python 3.8+.

  python3 tools/install_local.py                    # install or update
  python  tools/install_local.py --python python    # Windows: start the MCP server with `python` (or `py`, or a full path)
  python3 tools/install_local.py --uninstall        # remove it again (only a folder this script created)
  python3 tools/install_local.py --dest DIR         # another plugins/local folder

--python only changes the INSTALLED copy's mcp.json; the repo stays as it is.
"""
import argparse, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "spindoctor-qwerty"
MARKER = ".installed-by-spindoctor-qwerty.json"
PARTS = [".cursor-plugin", "mcp.json", "skills", "rules", "agents", "commands", "README.md", "FUNCTIONS.md", "LICENSE", "NOTICE", "COPYRIGHT", "CHANGELOG.md"]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Install SpinDoctor Qwerty into ~/.cursor/plugins/local")
    ap.add_argument("--dest", default=os.path.join(os.path.expanduser("~"), ".cursor", "plugins", "local"))
    ap.add_argument("--python", default=None, help="command that starts Python 3.8+ (default python3)")
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args(argv)
    target = os.path.join(os.path.abspath(a.dest), NAME)
    if os.path.lexists(target) and not os.path.isfile(os.path.join(target, MARKER)):
        print("refusing: %s exists and was not created by this script; remove or rename it first" % target); return 2
    if a.uninstall:
        if os.path.isdir(target): shutil.rmtree(target); print("removed", target)
        else: print("not installed:", target)
        return 0
    if a.python is not None:
        py = a.python.strip().replace("\\", "/")
        if not py or any(c in py for c in '"\'`$;&|<>\n'): print("refusing: --python must be a plain program name or path"); return 2
    version = json.load(open(os.path.join(ROOT, ".cursor-plugin", "plugin.json"), encoding="utf-8"))["version"]
    tmp = target + ".tmp-install"
    if os.path.lexists(tmp): shutil.rmtree(tmp)
    os.makedirs(tmp)
    for p in PARTS:
        src = os.path.join(ROOT, p)
        if os.path.isdir(src): shutil.copytree(src, os.path.join(tmp, p), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        elif os.path.isfile(src): shutil.copy2(src, os.path.join(tmp, p))
    if a.python is not None:
        mp = os.path.join(tmp, "mcp.json"); m = json.load(open(mp, encoding="utf-8"))
        m["mcpServers"][NAME]["command"] = py
        open(mp, "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=2) + "\n")
    json.dump({"name": NAME, "version": version, "source": ROOT, "python": a.python or "python3"}, open(os.path.join(tmp, MARKER), "w"), indent=2)
    if os.path.isdir(target): shutil.rmtree(target)
    os.replace(tmp, target)
    print("installed %s %s -> %s (MCP server: %s). Restart Cursor or run 'Developer: Reload Window', then approve the MCP server."
          % (NAME, version, target, a.python or "python3"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
