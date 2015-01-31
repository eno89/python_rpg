#!/usr/bin/env python
# vim: fileencoding=utf-8
import os
import sys
# Windows
if os.name == 'nt':
    import msvcrt

def get_input():
    corsors = {72:"k", 77:"l", 80:"j", 75:"h"}
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch == '\000' or ch == '\xe0':
                ch = msvcrt.getch()
                c = ord(ch)
                if c in corsors:
                    ch = corsors[c]
            return ch

while True:
    raw = get_input()
    print raw
    if raw == "Q":
        sys.exit()

enter = 13
print '\000',ord('\000')
print '\xe0',ord('\xe0')
while True:
    if msvcrt.kbhit():
        ch = msvcrt.getch()
        if ch == '\000' or ch == '\xe0':
            print ord(ch)
            ch = msvcrt.getch()
        print ch,ord(ch)
        if ord(ch) == 27:
            sys.exit()
vals = [72, 77, 80, 75]
