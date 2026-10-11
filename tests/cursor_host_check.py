# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for Cursor
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Cursor host check (stand-in host). Standard library only (Python 3.8+); no Cursor account, no sign-in, no network.

Cursor's plugin loader only runs inside a signed-in Cursor session (IDE or CLI), so this check is HOST-SIMULATED:
1. Static checks against the Cursor plugins reference (cursor.com/docs/reference/plugins): .cursor-plugin/plugin.json fields,
   folder-based component discovery (skills/*/SKILL.md, rules/*.mdc, agents/*.md, commands/*.md) and their front matter, mcp.json
   (stdio inferred from `command`, only ${CURSOR_PLUGIN_ROOT}, which Cursor expands; not the standard ${PLUGIN_ROOT}/${PLUGIN_DATA},
   which it does not), relative paths only, no hooks, text only.
2. tools/install_local.py into a throw-away HOME: copies (not symlinks) into ~/.cursor/plugins/local/spindoctor-qwerty, --python
   rewrites only the installed mcp.json, update in place, refuses a folder it didn't create, uninstall.
3. Stand-in loader: discovers the installed plugin exactly as the reference describes, expands ${CURSOR_PLUGIN_ROOT} in
   command/args/env/cwd, starts the MCP server and runs tests/e2e_mcp.py through it.
4. If the real Cursor CLI is given (CURSOR_AGENT=/path/to/cursor-agent), it records its version and confirms that loading plugins
   needs a sign-in (INFO lines; nothing is signed in).

usage: python3 tests/cursor_host_check.py [REPO_DIR]"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT = (".py", ".md", ".mdc", ".json", ".txt", ".csv", ".html", ".q", "")
MKEYS = {"name", "description", "version", "author", "homepage", "repository", "license", "keywords", "logo", "rules", "agents", "skills",
         "commands", "hooks", "mcpServers", "variables"}


def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---\n", open(path, encoding="utf-8").read(), re.S)
    return dict(re.findall(r"^([A-Za-z_-]+):\s*(.+)$", m.group(1), re.M)) if m else None


def discover(root):
    """Cursor Plugin component discovery (no manifest paths -> default folders)."""
    ls = lambda d, exts: sorted(f for f in os.listdir(os.path.join(root, d)) if f.endswith(exts)) if os.path.isdir(os.path.join(root, d)) else []
    return {"skills": sorted(d for d in os.listdir(os.path.join(root, "skills")) if os.path.isfile(os.path.join(root, "skills", d, "SKILL.md"))),
            "rules": ls("rules", (".md", ".mdc", ".markdown")), "agents": ls("agents", (".md", ".mdc", ".markdown")),
            "commands": ls("commands", (".md", ".mdc", ".markdown", ".txt")), "hooks": os.path.isfile(os.path.join(root, "hooks", "hooks.json")),
            "mcp": json.load(open(os.path.join(root, "mcp.json"), encoding="utf-8"))["mcpServers"]}


def snapshot(root):
    return {os.path.relpath(os.path.join(r, f), root): open(os.path.join(r, f), "rb").read() for r, ds, fs in os.walk(root) if "__pycache__" not in r for f in fs}


def main():
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    repo = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
    ok = True

    def T(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond); print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)[:700])); sys.stdout.flush()

    pj = json.load(open(os.path.join(repo, ".cursor-plugin", "plugin.json"), encoding="utf-8"))
    T(".cursor-plugin/plugin.json: kebab-case name, known fields only, author.name, version 1.1.0, GPL-3.0-or-later, no custom paths",
      re.match(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$", pj.get("name", "")) and set(pj) <= MKEYS and pj["author"]["name"] == "RUSSELL PHILIP SMITHSON"
      and pj["version"] == "1.1.0" and pj["license"] == "GPL-3.0-or-later" and not set(pj) & {"rules", "agents", "skills", "commands", "hooks", "mcpServers"}, pj)
    T("Cursor Plugin format only (no root plugin.json, so Cursor doesn't treat it as a skills+MCP-only Agent Plugin)", not os.path.exists(os.path.join(repo, "plugin.json")))
    d = discover(repo)
    T("discovery: 1 skill, 1 rule, 1 agent, 4 commands, no hooks, 1 MCP server",
      d["skills"] == ["spindoctor-qwerty"] and d["rules"] == ["spindoctor-qwerty.mdc"] and d["agents"] == ["qwerty-helper.md"] and len(d["commands"]) == 4
      and not d["hooks"] and not os.path.isdir(os.path.join(repo, "hooks")) and list(d["mcp"]) == ["spindoctor-qwerty"], d)
    sk = frontmatter(os.path.join(repo, "skills", "spindoctor-qwerty", "SKILL.md")); ru = frontmatter(os.path.join(repo, "rules", "spindoctor-qwerty.mdc"))
    ag = frontmatter(os.path.join(repo, "agents", "qwerty-helper.md")); cm = {f: frontmatter(os.path.join(repo, "commands", f)) for f in d["commands"]}
    kebab = lambda s: bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", s or ""))
    T("front matter: skill/agent/commands have kebab-case name + description; rule has description + boolean alwaysApply",
      sk and sk.get("name") == "spindoctor-qwerty" and sk.get("description") and ru and ru.get("description") and ru.get("alwaysApply") in ("true", "false")
      and ag and kebab(ag.get("name")) and ag.get("description") and all(m and kebab(m.get("name")) and m.get("description") and m["name"] + ".md" == f for f, m in cm.items()), (sk, ru, ag, cm))
    s = d["mcp"]["spindoctor-qwerty"]; vars_ = set(re.findall(r"\$\{([^}]+)\}", json.dumps(s)))
    T("mcp.json: stdio (command), runs a plugin file via ${CURSOR_PLUGIN_ROOT}; no ${PLUGIN_ROOT}/${PLUGIN_DATA} (Cursor doesn't expand them)",
      s.get("command") == "python3" and "url" not in s and vars_ == {"CURSOR_PLUGIN_ROOT"} and s["args"] == ["${CURSOR_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py"]
      and os.path.isfile(s["args"][0].replace("${CURSOR_PLUGIN_ROOT}", repo)), s)
    md = "".join(open(os.path.join(repo, p), encoding="utf-8").read() for p in ["skills/spindoctor-qwerty/SKILL.md", "rules/spindoctor-qwerty.mdc", "agents/qwerty-helper.md"] + ["commands/" + f for f in d["commands"]])
    T("no other host's variables or placeholders ($ARGUMENTS, CLAUDE_/CODEBUDDY_); honest limits (not a quantum computer, 298, 59); chat-theory confirmation",
      not re.search(r"\$ARGUMENTS|CLAUDE_|CODEBUDDY|\$\{PLUGIN_", md) and "not a quantum computer" in md.replace("\n", " ") and "298" in md and "59" in md and "confirm" in md)
    bad = [os.path.relpath(os.path.join(r, f), repo) for r, ds, fs in os.walk(repo) if ".git" not in r.split(os.sep) and "__pycache__" not in r
           for f in fs if os.path.splitext(f)[1].lower() not in TEXT and not (f.endswith(".pdf") and r.endswith(os.path.join("examples", "theory")))]
    T("only text files (sample PDFs are generated by make_sample_pdfs.py and git-ignored)", not bad, bad)

    tmp = tempfile.mkdtemp(prefix="sdq_cur_"); home = os.path.join(tmp, "home"); os.makedirs(home)
    dest = os.path.join(home, ".cursor", "plugins", "local"); inst = os.path.join(dest, "spindoctor-qwerty"); ins = os.path.join(repo, "tools", "install_local.py")
    before = snapshot(repo)
    env = dict(os.environ, HOME=home, USERPROFILE=home)
    run = lambda *a: subprocess.run([sys.executable, ins] + list(a), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    r1 = run()
    T("install_local.py: real copy (not a symlink) in ~/.cursor/plugins/local/spindoctor-qwerty with manifest, mcp.json and all components; no tests/tools",
      r1.returncode == 0 and os.path.isdir(inst) and not os.path.islink(inst) and discover(inst) == d and not os.path.exists(os.path.join(inst, "tests"))
      and json.load(open(os.path.join(inst, ".cursor-plugin", "plugin.json"))) == pj, r1.stdout)
    r2 = run("--python", "python"); im = json.load(open(os.path.join(inst, "mcp.json")))
    r3 = run("--python", "py; rm -rf /")
    T("--python python rewrites only the installed mcp.json (repo unchanged); update in place; shell metacharacters refused",
      r2.returncode == 0 and im["mcpServers"]["spindoctor-qwerty"]["command"] == "python" and snapshot(repo) == before and r3.returncode == 2, (r2.stdout, r3.stdout))
    run()
    other = os.path.join(tmp, "o"); os.makedirs(os.path.join(other, "spindoctor-qwerty")); r4 = run("--dest", other)
    T("refuses to overwrite a spindoctor-qwerty folder it didn't create", r4.returncode == 2 and os.listdir(os.path.join(other, "spindoctor-qwerty")) == [], r4.stdout)

    cur = os.environ.get("CURSOR_AGENT")
    if cur:
        cenv = dict(env, DBUS_SESSION_BUS_ADDRESS="disabled:"); [cenv.pop(k, None) for k in ("CURSOR_API_KEY", "CURSOR_AUTH_TOKEN")]
        v = subprocess.run([cur, "--version"], env=cenv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120).stdout.strip()
        p = subprocess.run([cur, "-p", "hi", "--plugin-dir", inst], env=cenv, cwd=home, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
        print("INFO real Cursor CLI %s installed (no sign-in): `cursor-agent -p --plugin-dir <installed copy>` answers: %s" % (v, (p.stdout.strip().splitlines() or ["?"])[-1][:160]), flush=True)

    # stand-in loader: what Cursor does with the installed copy, per the reference
    root = inst; sub = lambda x: x.replace("${CURSOR_PLUGIN_ROOT}", root)
    sv = discover(root)["mcp"]["spindoctor-qwerty"]
    cmd = [os.environ.get("SPINDOCTOR_PYTHON") or sys.executable if sv["command"] in ("python", "py") else os.environ.get("SPINDOCTOR_PYTHON") or sv["command"]] + [sub(a) for a in sv.get("args", [])]
    env2 = dict(os.environ, **{k: sub(v) for k, v in sv.get("env", {}).items()}); env2["SPINDOCTOR_WORKSPACE"] = os.path.join(tmp, "spindoctor-workspace")
    ex = os.path.join(root, "skills", "spindoctor-qwerty", "examples", "theory")
    r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server"] + cmd + ["--examples", ex, "--out", os.path.join(tmp, "e2e_results.json")],
                       env=env2, cwd=sub(sv["cwd"]) if sv.get("cwd") else home)
    T("stand-in host: end-to-end through the MCP server of the installed copy, ${CURSOR_PLUGIN_ROOT} expanded", r.returncode == 0)
    r5 = run("--uninstall")
    T("install_local.py --uninstall removes the folder", r5.returncode == 0 and not os.path.exists(inst), r5.stdout)
    shutil.rmtree(tmp, ignore_errors=True)
    print("HOST-CHECK (host-simulated: Cursor stand-in loader)", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
