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

class SystemBase:
    def __init__(self):
        self.state = 0
        pass
    def draw(self):
        pass
    def update(self):
        pass
    def changed(self, input_command):
        pass

class Event(SystemBase):
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

class Battle(SystemBase):
    B_START, B_COMMAND, B_BATTLE = range(3)
    START_FIGHT, START_EXIT = range(2)
    COMMAND_ATTACK, COMMAND_MAGIC, COMMAND_DEFENSE = range(3)
    def __init__(self):
        self.state = BATTLE
        self.enemy = self.enemy_create()
        #
        self.b_state = Battle.B_START
        self.menu = Battle.START_FIGHT
    def enemy_create(self):
        enemy = Enemy(u"スライム", 20,15,5, 10)
        return enemy
    def draw(self):
        #
        player.show(self.state)
        #
        self.enemy.show()
        #
        if self.b_state == Battle.B_START:
            menus = [u"戦う",u"逃げる"]
            if self.menu == Battle.START_FIGHT:
                menus[0] = " * " + menus[0]
                menus[1] = "   " + menus[1]
            elif self.menu == Battle.START_EXIT:
                menus[0] = "   " + menus[0]
                menus[1] = " * " + menus[1]
            for s in menus:
                print(s)
        elif self.b_state == Battle.B_COMMAND:
            menus = [u"攻撃", u"呪文", u"防御"]
#             menus[self.menu][2] = '*'
            if self.menu == Battle.COMMAND_ATTACK:
                menus[0] = " * " + menus[0]
                menus[1] = "   " + menus[1]
                menus[2] = "   " + menus[2]
            elif self.menu == Battle.COMMAND_MAGIC:
                menus[0] = "   " + menus[0]
                menus[1] = " * " + menus[1]
                menus[2] = "   " + menus[2]
            elif self.menu == Battle.COMMAND_DEFENSE:
                menus[0] = "   " + menus[0]
                menus[1] = "   " + menus[1]
                menus[2] = " * " + menus[2]
            for s in menus:
                print(s)
        elif self.b_state == Battle.B_BATTLE:
            pass
    def update(self):
        print u"%s の攻撃" % (self.enemy.name)
        damage = self.enemy.attack - player.defense
        print u"%s に %3d" % (player.name, damage)
        player.hp -= damage
    def escape(self):
        r = random.randint(1,100)
        if r < 50:
            global game
            game = game_stack.pop()
            print "逃げ出した"
        else:
            print "逃げるのに失敗した"
        return True
    def changed(self, input_command):
        if input_command == DOWN:
            if self.b_state == Battle.B_START:
                self.menu += 1
                self.menu %= 2
                return True
            elif self.b_state == Battle.B_COMMAND:
                self.menu += 1
                self.menu %= 3
                return True
        elif input_command == UP:
            if self.b_state == Battle.B_START:
                self.menu += (2 - 1)
                self.menu %= 2
                return True
            elif self.b_state == Battle.B_COMMAND:
                self.menu += (3 - 1)
                self.menu %= 3
                return True
        elif input_command == ENTER:
            if self.b_state == Battle.B_START:
                if self.menu == Battle.START_FIGHT:
                    self.b_state = Battle.B_COMMAND
                    self.menu = 0
                    return True
                elif self.menu == Battle.START_EXIT:
                    return self.escape()
            elif self.b_state == Battle.B_COMMAND:
                if   self.menu == Battle.COMMAND_ATTACK:
                    return self.attack()
                elif self.menu == Battle.COMMAND_MAGIC:
                    return self.magic()
                elif self.menu == Battle.COMMAND_DEFENSE:
                    return self.defense()
        elif input_command == CANCEL:
            pass
        return False
    def attack(self):
        print u"%s の攻撃" % (player.name)
        damage = player.attack - self.enemy.defense
        print u"%s に %3d" % (self.enemy.name, damage)
        self.enemy.hp -= damage
        if self.enemy.hp <= 0:
            print u"%s を倒した" % (self.enemy.name)
            print u"EXP +%3d" % (self.enemy.exp)
            player.add_exp(self.enemy.exp)
            global game
            game = game_stack.pop()
        return True
    def magic(self):
        pass
    def defense(self):
        print u"%s は 防御した" % (player.name)
        return True

class Status(SystemBase):
    def __init__(self):
        self.state = STATUS
        pass
    def draw(self):
        print u"ステータス画面"
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

class Field(SystemBase):
    def __init__(self):
        self.state = FIELD
        self.next_town = 20
        self.move = 0
    def draw(self):
        print "次の町まで %2d/%2d" % (self.move, self.next_town)
    def update(self):
        pass
    def encount(self):
        r = random.randint(1,100)
        if r <= 20:
            print "敵が現れた"
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

class Title(SystemBase):
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
class CharacterBase:
    def __init__ (self):
        pass
class Character:
    def __init__ (self, name, hp, attack, defense):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.lv = 1
    def attackto(self):
        pass
    def show(self):
        pass

class Enemy(Character):
    def __init__ (self, name, hp, attack, defense, exp):
        Character.__init__(self, name, hp, attack, defense)
        self.exp = exp
    def show(self):
        print "%s" % ( self.name)

class Player(Character):
    def __init__ (self, name, hp, attack, defense):
        Character.__init__(self, name, hp, attack, defense)
        self.exp = 0
        self.next_exp = 100
        self.add_attack = 3
        self.add_defense = 2
        self.add_hp = 10
    def add_exp(self, exp):
        self.exp += exp
        if self.exp > self.next_exp:
            # Lv Up
            self.next_exp *= 2
            self.lv += 1
            self.max_hp  += self.add_hp
            self.hp  = self.max_hp
            self.attack  += self.add_attack
            self.defense += self.add_defense
            print "%s は レベル が上がった +HP %2d +ATK %2d +DEF %3d" % ( self.name, self.add_hp, self.add_attack, self.add_defense)
    def show(self, state):
        if state == STATUS:
            print "%s HP %3d/%3d ATK:%3d DEF:%3d" % ( self.name, self.hp, self.max_hp, self.attack, self.defense)
        if state == BATTLE:
            print "%s %3d/%3d" % ( self.name, self.hp, self.max_hp)
    def damage(self, enemy):
        return damage


#------------------------------------------------------------------------------

class PyRPG:
    def __init__(self):
        # Title
        global game
#         game = Title()
#         game = Battle()
        game = Field()
        global player
        player = Player(u"勇者", 100, 20, 10)
        self.last_input = NONE
        # メインループを起動
        self.main_looop()
        # End
    def main_looop(self):
        """メインループ"""
        re_draw = True
        turn = 0
        while True:
            if re_draw == True :
                self.update()
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
#         in_txt = raw_input(key_message)
        in_txt = raw_input()
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
game = SystemBase()
game_stack = []
player = CharacterBase()

if __name__ == "__main__":
    PyRPG()
