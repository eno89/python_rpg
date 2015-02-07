# vim:fileencoding=utf-8
import sys, termios, atexit
from select import select
import traceback

class BaseGameInput(object):
    def get_key(self):
        ''' 入力キーの取得 '''
        key = -1
        key_dict = { ord("h"):LEFT, ord("j"):DOWN, ord("k"):UP,ord("l"):RIGHT, ord("a"):ENTER, ord("x"):CANCEL, ord("z"):ENTER, ord("c"):CANCEL, 13:ENTER }
        raw_ch = get_input()
        raw_ord = ord(raw_ch)
        if raw_ord in key_dict:
            key = key_dict[raw_ord]
        elif raw_ord == ord("Q"):
            key = FINISH
        return key
    def wait(self):
        get_input()
    def clear(self):
        os.system(self.CLEAR_SCREEN)
    def print_buffer(self, buff):
        for e in buff:
            print e
    def getch(self):
        return ''
    def kbhit(self):
        return False

class GameInput(BaseGameInput):
    CLEAR_SCREEN = 'cls'
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        atexit.register(self.set_normal_term)
        self.set_curses_term()
    def __del__(self):
        print "end"
        self.set_normal_term()
    def set_normal_term(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)
    def set_curses_term(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
    def getch(self):
        return sys.stdin.read(1)
    def kbhit(self):
        dr,dw,de = select([sys.stdin], [], [], 0)
        return dr <> []
    def getche(self):
        ch = getch()
        putch(ch)
        return ch
    def putch(self, ch):
        sys.stdout.write(ch)
    def get_input(self):
        ''' 矢印は文字で返す '''
        corsors = { 65:"k", 66:"j", 67:"l", 68:"h" }
        while True:
            if self.kbhit():
                ch = self.getch()
                if ch == chr(27):
                    ch = sys.stdin.read(1)
                    if ch == '[':
                        ch = sys.stdin.read(1)
                        c = ord(ch)
                        if c in corsors:
                            ch = corsors[c]
                            return ch
                else:
                    return ch

if __name__ == "__main__":
    try:
        game_input = GameInput()
        while True:
            c = game_input.get_input()
            if c == "q": # ESC
                break
            print(c),  ord(c)
    except:
        traceback.print_exc()
