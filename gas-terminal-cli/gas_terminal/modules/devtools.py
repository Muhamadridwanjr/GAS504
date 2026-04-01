"""GAS Terminal v3 — Module 7: AI Coding Tools"""
from __future__ import annotations
import subprocess
from gas_terminal.utils import display as D
from gas_terminal import config

MENU = [
    ("1", "🤖", "Launch Claude Code CLI"),
    ("2", "🛠", "Launch Aider (AI Coding Agent)"),
    ("3", "🔍", "AI Code Review"),
    ("4", "🐛", "AI Bug Fix"),
    ("5", "♻ ", "AI Refactor"),
    ("6", "✍ ", "AI Write New Feature"),
    ("7", "📋", "AI Explain Code"),
    ("8", "🧪", "Generate Tests"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "🧰 AI Coding Tools")
        if choice == "b":
            break
        elif choice == "1":
            prompt = D.ask("Prompt for Claude Code (leave blank for interactive)")
            cmd = ["claude"]
            if prompt.strip():
                cmd.extend(["-p", prompt.strip()])
            _run_cmd(cmd)
        elif choice == "2":
            files = D.ask("Files to edit (space-separated, leave blank for interactive)")
            cmd = ["aider"]
            if files.strip():
                cmd.extend(files.strip().split())
            _run_cmd(cmd)
        elif choice == "3":
            path = D.ask("Path to review (default: .)")
            path = path.strip() or "."
            _run_cmd(["claude", "-p",
                f"Review the code in {path}. Identify bugs, security vulnerabilities, performance issues, and top improvements. Be specific."])
        elif choice == "4":
            desc = D.ask("Describe the bug")
            _run_cmd(["claude", "-p", f"Fix this bug: {desc}"])
        elif choice == "5":
            path = D.ask("Path to refactor")
            _run_cmd(["aider", "--message",
                f"Refactor {path} for better readability, maintainability and performance. Apply best practices.", path])
        elif choice == "6":
            feature = D.ask("Describe the feature to build")
            path = D.ask("Target file or directory")
            _run_cmd(["claude", "-p",
                f"Build this feature: {feature}. Target: {path}. Write complete, working code."])
        elif choice == "7":
            path = D.ask("File to explain")
            _run_cmd(["claude", "-p",
                f"Explain this code in detail: {path}. Describe what it does, how it works, and any important patterns used."])
        elif choice == "8":
            path = D.ask("File to generate tests for")
            _run_cmd(["claude", "-p",
                f"Generate comprehensive unit tests for {path}. Cover edge cases, error cases, and main happy paths."])
        D.press_enter()

def _run_cmd(cmd: list):
    D.info(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd)
    except FileNotFoundError:
        D.error(f"Command not found: {cmd[0]}. Make sure it is installed.")
    except KeyboardInterrupt:
        D.info("Command interrupted.")
