#!/usr/bin/env python3
import sys
import subprocess

def run(*args, **kwargs):
    stdin = kwargs.get("stdin")
    redirect = kwargs.get("stdout")
    cwd = kwargs.get("cwd")
    print("[SHELL] " +
        ("(cd " + cwd + "; " if cwd else "") +
        subprocess.list2cmdline(*args) +
        (" < " + stdin.name if stdin else "") +
        (" > " + redirect.name if redirect else "") +
        (")" if cwd else ""))
    sys.stdout.flush()
    return subprocess.check_call(*args, **kwargs)

run(["python", "-m", "pip", "install", "requests"])
