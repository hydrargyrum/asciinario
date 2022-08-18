#!/usr/bin/env python3

from pathlib import Path
import re
import subprocess
import sys
import time
from uuid import uuid4


class Play:
    def __init__(self, screen_id):
        self.screen_id = screen_id
        self.status_pos = "top"
        self.type_wait = .2
        self.enter_wait = .5

    def do(self, line):
        for regex, method in self.statements.items():
            match = regex.fullmatch(line)
            if match:
                return method(self, match)
        else:
            raise Exception(f"no pattern matched {line!r}")

    def do_status_change(self, match):
        if match[1] == "hide":
            self.send_screen("hardstatus", "ignore")
        elif match[1] == "show top":
            self.status_pos = "top"
            self.send_screen("hardstatus", "alwaysfirstline")
        elif match[1] == "show bottom":
            self.status_pos = "bottom"
            self.send_screen("hardstatus", "alwayslastline")
        elif match[1] == "show":
            self.do_status_change([None, f"show {self.status_pos}"])

    def do_status_type(self, match):
        flags = match[1]
        message = match[2]
        for n in range(len(message)):
            self.send_screen("hstatus", message[:n + 1])
            if ">" not in flags:
                time.sleep(self.type_wait)

    def do_type(self, match):
        flags = set(match[1])
        message = match[2]
        for c in message:
            self.send_screen("stuff", c)
            if ">" not in flags:
                time.sleep(self.type_wait)

        if "$" in flags:
            self.send_screen("stuff", "\n")
            if ">" not in flags:
                time.sleep(self.enter_wait)

    def do_type_enter(self, match):
        self.send_screen("stuff", "\\n")
        time.sleep(self.enter_wait)

    def do_send_key(self, match):
        if match[1] == "tab":
            self.send_screen("stuff", r"\t")
        elif match[1] == "enter":
            self.send_screen("stuff", r"\n")
        elif match[1].startswith("^") or match[1].startswith("\\"):
            self.send_screen("stuff", match[1])
        else:
            raise Exception("unhandled key %r" % match[1])

    def do_wait(self, match):
        time.sleep(float(match[1]))

    def do_dialog(self, match):
        self.send_screen("exec", "dialog", "--keep-tite", "--msgbox", match[1], "0", "0")

    def do_set(self, match):
        if match[1] in {"type_wait", "enter_wait"}:
            setattr(self, match[1], float(match[2]))
        else:
            raise KeyError("unhandled config %r" % match[1])

    def send_screen(self, *args):
        subprocess.check_output(["screen", "-S", self.screen_id, "-X", *args])

    statements = {
        re.compile(r"(\$?>?)> (.*)"): do_type,
        re.compile("->(>?) (.*)"): do_status_type,
        re.compile(r"key (\^.|\\[nrt]|\\\d{3}|enter|tab)"): do_send_key,
        re.compile("enter"): do_type_enter,
        re.compile("status (show(?: top| bottom)?|hide)"): do_status_change,
        re.compile(r"w(?:ait)? (\d+(?:\.\d*)?|\d*\.\d+)"): do_wait,
        re.compile(r"set (\w+) = (.*)"): do_set,
        re.compile(r"dialog (.*)"): do_dialog,
    }


def play_inscript(text, screen_id):
    player = Play(screen_id)

    lines = text.strip().split("\n")
    for line in lines:
        if not line or line.startswith("#"):
            continue

        player.do(line)


instructions = Path(sys.argv[2]).read_text()

screen_id = str(uuid4())
recorder_proc = subprocess.Popen(["asciinema", "rec", "-c", f"screen -S {screen_id}", sys.argv[1]])

play_inscript(instructions, screen_id)
subprocess.check_output(["screen", "-S", screen_id, "-X", "quit"])
recorder_proc.wait()
