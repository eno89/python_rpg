#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import sys


TITLE, EVENT, TOWN, FIELD, DANJON, BOSS, BATTLE, STATUS, TALK, COMMAND = range(10)
STATE_NAME = ["TITLE", "EVENT", "TOWN", "FIELD", "DANJON", "BOSS", "BATTLE", "STATUS", "TALK", "COMMAND"]

NONE, UP, DOWN, LEFT, RIGHT, ENTER, CANCEL = range(7)

EVENT_OPENING, EVENT_MAOU, EVENT_ENDING = range(3)

#------------------------------------------------------------------------------

class BaseSystem:
    def __init__(self):
        self.state = 0
        pass
    def draw(self):
        pass
    def update(self):
        pass
    def changed(self, input_command):
        pass

class Event(BaseSystem):
    FIGHT, EXIT = range(2)
    def __init__(self):
        self.state = EVENT
        self.event_state = EVENT_OPENING
        self.end_event = False
        self.turn = 0
    def message(self):
        storys = [u"勇者よ",u"魔王を倒してくれ"]
        if len(storys) - 1 == self.turn:
            self.end_event = True
        return storys[self.turn]
    def draw(self):
        s = self.message()
        print s
    def update(self):
        if self.end_event == True:
            global game
            game = Field()
    def changed(self, input_command):
        if input_command == DOWN:
            pass
        elif input_command == UP:
            pass
        elif input_command == ENTER:
            self.turn += 1
            return True
        elif input_command == CANCEL:
            pass
        return False

class Battle(BaseSystem):
    FIGHT, EXIT = range(2)
    def __init__(self):
        self.state = BATTLE
        self.enemy = self.enemy_create()
        self.menu = self.FIGHT
    def enemy_create(self):
        enemy = Enemy(u"スライム", 20,10,5)
        return enemy
    def draw(self):
        #
        for player in party.member:
            player.show(self.state)
        #
        enemy.show()
        # カーソルの描画
        menus = [u"戦う",u"逃げる"]
        if self.menu == self.FIGHT:
            menus[0] += " * "
        elif self.menu == self.EXIT:
            menus[1] += " * "
        for s in menus:
            print(s)
    def update(self):
        pass
    def exit():
        pass
    def exit():
        pass
    def changed(self, input_command):
        if input_command == DOWN:
            pass
        elif input_command == UP:
            pass
        elif input_command == ENTER:
            pass
        elif input_command == CANCEL:
            global game
            game = game_stack.pop()
            return True
        return False

class Status(BaseSystem):
    def __init__(self):
        self.state = STATUS
        pass
    def draw(self):
        print u"ステータス画面"
#         global party
        for player in party.member:
            player.show(self.state)
    def update(self):
        pass
    def changed(self, input_command):
        if input_command == DOWN:
            pass
        elif input_command == UP:
            pass
        elif input_command == ENTER:
            pass
        elif input_command == CANCEL:
            global game
            game = game_stack.pop()
            return True
        return False

class Field(BaseSystem):
    def __init__(self):
        self.state = FIELD
        self.next_town = 20
        self.move = 0
    def draw(self):
        print "次の町まで %2d/%2d" % (self.move, self.next_town)
    def update(self):
        pass
    def encount(self):
        r = random.randint(1,10)
        if r > 5:
            print r, "enemy encount"
            global game
            game_stack.append(game)
            game = Battle()
    def changed(self, input_command):
        if input_command == RIGHT:
            if self.move == self.next_town - 1:
                pass
            else:
                self.move += 1
                self.encount()
                return True
        elif input_command == LEFT:
            if not self.move == 0:
                self.move -= 1
                self.encount()
                return True
        elif input_command == ENTER:
            global game
            game_stack.append(game)
            game = Status()
            return True
        return False

class Title(BaseSystem):
    START, CONTINUE, EXIT = 0, 1, 2
    def __init__(self):
        self.menu = self.START
        self.state = TITLE
    def draw(self):
        menus = ["START","CONTINUE", "EXIT"]
        # メニューカーソルの描画
        if self.menu == self.START:
            menus[0] += " * "
        elif self.menu == self.CONTINUE:
            menus[1] += " * "
        elif self.menu == self.EXIT:
            menus[2] += " * "
        for s in menus:
            print(s)
    def changed(self, input_command):
        if input_command == DOWN:
            self.menu += 1
            if self.menu > 2:
                self.menu = 2
                return False
            return True
        elif input_command == UP:
            self.menu -= 1
            flag = True
            if self.menu < 0:
                self.menu = 0
                return False
            return True
        elif input_command == ENTER:
            if self.menu == Title.START:
                global game
                game = Event()
                return True
            elif self.menu == Title.CONTINUE:
                pass
            elif self.menu == Title.EXIT:
                sys.exit()
        return False
    def update(self):
        pass

#------------------------------------------------------------------------------
class Character:
    def __init__ (self, name, hp, attack, deffence):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.deffence = deffence
    def attackto(self):
        pass
    def show(self):
        pass

class Enemy(Character):
#     def __init__ (self, name, hp, attack, deffence):
#         pass
    def show(self):
        print "%s" % ( self.name)

class Player(Character):
    def show(self, state):
        if state == STATUS:
            print "%s HP %3d/%3d ATK:%3d DEF:%3d" % ( self.name, self.hp, self.max_hp, self.attack, self.deffence)
        if state == BATTLE:
            print "%s %3d/%3d" % ( self.name, self.hp, self.max_hp)

class Party:
    def __init__(self):
        # Partyのメンバーリスト
        self.member = []
    def add(self, player):
        """Partyにplayerを追加"""
        self.member.append(player)
    def update(self):
        pass
    def draw(self):
        pass

#------------------------------------------------------------------------------

class PyRPG:
    def __init__(self):
        # Title
        global game
        game = Title()
        global party
        player1 = Player(u"勇者", 100, 20, 10)
        party.add(player1)
        self.last_input = NONE
        # メインループを起動
        self.main_looop()
        # End
    def main_looop(self):
        """メインループ"""
        re_draw = True
        turn = 0
        while True:
            self.update()
            if re_draw == True :
#                 print "------------------------"
                print "------------- %s %3d" % (STATE_NAME[game.state], turn)
                turn += 1
                self.draw()
            re_draw = self.check_event()
    def update(self):
        """ゲーム状態の更新"""
        game.update()
    def draw(self):
        game.draw()
    def check_event(self):
        re_draw = False
        keys = ["h", "j", "k","l", "a", "x"]
        key_message = " %s" % keys[0]
        for k in keys[1:]:
            key_message += " or %s" % k
        key_message += " : "
        if game.state == TITLE:
            keys = ["j", "k", "a"]
            key_message = " %s or %s or %s : " % (keys[0],keys[1],keys[2])
        elif game.state == FIELD:
            keys = ["h", "l", "a"]
            key_message = " %s or %s or %s : " % (keys[0],keys[1],keys[2])
        in_txt = raw_input(key_message)
#         in_txt = raw_input()
        if in_txt == "":
            re_draw = game.changed(self.last_input)
        elif in_txt == "Q":
            sys.exit()
        if in_txt in keys:
            if in_txt == "h":
                re_draw = game.changed(LEFT)
                self.last_input = LEFT
            elif in_txt == "j":
                re_draw = game.changed(DOWN)
                self.last_input = DOWN
            elif in_txt == "k":
                re_draw = game.changed(UP)
                self.last_input = UP
            elif in_txt == "l":
                re_draw = game.changed(RIGHT)
                self.last_input = RIGHT
            elif in_txt == "a":
                re_draw = game.changed(ENTER)
                self.last_input = ENTER
            elif in_txt == "x":
                re_draw = game.changed(CANCEL)
                self.last_input = CANCEL
        return re_draw

#------------------------------------------------------------------------------
game = BaseSystem()
game_stack = []
party = Party()

if __name__ == "__main__":
    PyRPG()
