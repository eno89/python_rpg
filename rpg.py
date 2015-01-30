#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import sys


TITLE, EVENT, TOWN, FIELD, STATUS, BATTLE, BOSS, ENDING = range(8)
STATE_NAME = ["TITLE", "EVENT", "TOWN", "FIELD", "STATUS", "BATTLE", "BOSS", "ENDING" ]

NONE, UP, DOWN, LEFT, RIGHT, ENTER, CANCEL = range(7)

EVENT_OPENING, EVENT_TOWN_TALK, EVENT_MAOU_BEGIN, EVENT_MAOU_END, EVENT_ENDING = range(5)

#------------------------------------------------------------------------------

class SystemBase:
    def __init__(self):
        self.game_state = 0
        pass
    def draw(self):
        pass
    def update(self):
        pass
    def changed(self, input_command):
        pass

class Title(SystemBase):
    START, CONTINUE, EXIT = 0, 1, 2
    def __init__(self):
        SystemBase.__init__(self)
        self.menu = self.START
        self.game_state = TITLE
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
                game = Event(EVENT_OPENING)
                return True
            elif self.menu == Title.CONTINUE:
                pass
            elif self.menu == Title.EXIT:
                sys.exit()
        return False

class Event(SystemBase):
    FIGHT, EXIT = range(2)
    def __init__(self, event_state):
        self.game_state = EVENT
        self.event_state = event_state
        self.end_event = False
        self.turn = 0
        if   self.event_state == EVENT_OPENING:
            self.storys = [u"王様「勇者よ」",u"王様「この世界は魔王に侵略されておる」",u"王様「魔王を倒してくれ」",u"王様「まずは次の町に向かうのじゃ」"]
        elif self.event_state == EVENT_TOWN_TALK:
            self.storys = [u"「次は魔王城だよ」"]
        elif self.event_state == EVENT_MAOU_BEGIN:
            self.storys = [u"魔王「よく来たな勇者よ」", u"魔王「ここがお前の墓場だ」"]
    def message(self):
        if len(self.storys) - 1 == self.turn:
            self.end_event = True
        return self.storys[self.turn]
    def draw(self):
        s = self.message()
        print s
    def update(self):
        if self.end_event == True:
            global game
            if   self.event_state == EVENT_OPENING:
                game = Field()
            elif self.event_state == EVENT_TOWN_TALK:
                game = game_stack.pop()
            elif self.event_state == EVENT_MAOU_BEGIN:
                boss = boss_create()
                print u"%s が現れた" % (boss.name)
                game = Battle(boss)
                game_stack.append(Ending())
    def changed(self, input_command):
        if input_command == ENTER:
            self.turn += 1
            return True
        return False

class Town(SystemBase):
    TALK, SLEEP, STATUS, NEXT = range(4)
    def __init__(self):
        SystemBase.__init__(self)
        self.game_state = DOWN
        self.menu = 0
        self.menus = [u"話す", u"泊まる",u"ステータスを見る", u"出発する"]
        self.is_select = True
        print "ここは %s だよ" % ("町")
    def draw(self):
        if self.is_select:
            for i in range(len(self.menus)):
                if  self.menu == i:
                    print " * " + self.menus[i]
                else:
                    print "   " + self.menus[i]
    def changed(self, input_command):
        if   input_command == DOWN:
            self.menu += 1
            self.menu %= len(self.menus)
            return True
        elif input_command == UP:
            self.menu += (len(self.menus) - 1)
            self.menu %= len(self.menus)
            return True
        elif input_command == ENTER:
            self.action()
            return True
        return False
    def action(self):
        global game
        if   self.menu == self.TALK:
            game_stack.append(game)
            game = Event(EVENT_TOWN_TALK)
        elif self.menu == self.SLEEP:
            player.recover()
            print u"全回復した"
        elif self.menu == self.STATUS:
            game_stack.append(game)
            game = Status()
        elif self.menu == self.NEXT:
            game = Event(EVENT_MAOU_BEGIN)

class Field(SystemBase):
    def __init__(self):
        self.game_state = FIELD
        self.next_town = 20
        self.move = 0
    def draw(self):
        print u"次の町まで %2d/%2d" % (self.move, self.next_town)
    def update(self):
        pass
    def encount(self):
        r = random.randint(1,100)
        if r <= 20:
            print u"敵が現れた"
            global game
            game_stack.append(game)
            enemy = enemy_create()
            game = Battle(enemy)
    def changed(self, input_command):
        global game
        if input_command == RIGHT or input_command == UP:
            if self.move == self.next_town - 1:
                game = Town()
                return True
            else:
                self.move += 1
                self.encount()
                return True
        elif input_command == LEFT or input_command == DOWN:
            if not self.move == 0:
                self.move -= 1
                self.encount()
                return True
        elif input_command == ENTER:
            game_stack.append(game)
            game = Status()
            return True
        return False

class Status(SystemBase):
    def __init__(self):
        self.game_state = STATUS
        pass
    def draw(self):
        print u"ステータス画面"
        player.show(self.game_state)
    def update(self):
        pass
    def changed(self, input_command):
        if input_command == ENTER or input_command == CANCEL:
            global game
            game = game_stack.pop()
            return True
        return False

def calc_damage(attack, defense):
    damage = attack - defense
    if damage < 0:
        damage = 0
    return damage

def boss_create():
    enemy = Enemy(u"魔王", 300, 10, 0, 0)
    return enemy

def enemy_create():
    enemy = Enemy(u"スライム", 30, 5, 0, 10)
    return enemy

class Battle(SystemBase):
    B_START, B_COMMAND, B_BATTLE = range(3)
    START_FIGHT, START_EXIT = range(2)
    COMMAND_ATTACK, COMMAND_MAGIC, COMMAND_DEFENSE = range(3)
    def __init__(self, enemy):
        self.game_state = BATTLE
        self.enemy = enemy
        #
        self.b_state = Battle.B_START
        self.menu = Battle.START_FIGHT
        self.is_battle = False
        self.command = self.attack
    def draw(self):
        # プレイヤー
        player.show(self.game_state)
        # 敵
        self.enemy.show()
        # 選択肢 クラス化するかも
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
        if self.is_battle == True:
            # 選択肢の処理
            self.command()
            # 敵から
            if self.enemy.is_living() == True:
                print u"%s の攻撃" % (self.enemy.name)
                damage = calc_damage(self.enemy.attack, player.defense)
                print u"%s に %3d" % (player.name, damage)
                player.receive_damage(damage)
    def changed(self, input_command):
        self.is_battle = False
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
                self.is_battle = True
                if   self.menu == Battle.COMMAND_ATTACK:
                    self.command = self.attack
                    return True
                elif self.menu == Battle.COMMAND_MAGIC:
                    self.command = self.magic
                elif self.menu == Battle.COMMAND_DEFENSE:
                    self.command = self.defense
                    return True
        elif input_command == CANCEL:
            pass
        return False
    def escape(self):
        r = random.randint(1,100)
        if r < 50:
            global game
            game = game_stack.pop()
            print "逃げ出した"
        else:
            print "逃げるのに失敗した"
        return True
    def attack(self):
        print u"%s の攻撃" % (player.name)
        damage = calc_damage(player.attack, self.enemy.defense)
        print u"%s に %3d" % (self.enemy.name, damage)
        self.enemy.hp -= damage
        if self.enemy.hp <= 0:
            print u"%s を倒した" % (self.enemy.name)
            print u"EXP +%3d" % (self.enemy.exp)
            player.add_exp(self.enemy.exp)
            global game
            game = game_stack.pop()
    def magic(self):
        pass
    def defense(self):
        print u"%s は 防御した" % (player.name)

class Ending(SystemBase):
    def __init__(self):
        SystemBase.__init__(self)
        self.game_state = ENDING
    def draw(self):
        print "Fin"
    def changed(self, input_command):
        if input_command == ENTER:
            sys.exit()
        return True


#------------------------------------------------------------------------------
class CharacterBase:
    def __init__ (self):
        pass

class Character:
    """ プレイヤー，敵，味方，NPC """
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
    def is_living(self):
        if self.hp <= 0:
            return False
        return True

class Player(Character):
    def __init__ (self, name, hp, attack, defense):
        Character.__init__(self, name, hp, attack, defense)
        self.exp = 0
        self.next_exp = 0
        self.add_next_exp = 10
        self.next_exp += self.add_next_exp
        self.add_attack = 3
        self.add_defense = 2
        self.add_hp = 10
    def add_exp(self, exp):
        self.exp += exp
        if self.exp >= self.next_exp:
            # Lv Up
            self.add_next_exp *= 2
            self.next_exp += self.add_next_exp
            self.lv += 1
            self.max_hp  += self.add_hp
            self.attack  += self.add_attack
            self.defense += self.add_defense
            print u"%s は レベル が上がった +HP %2d +ATK %2d +DEF %3d" % ( self.name, self.add_hp, self.add_attack, self.add_defense)
            self.hp  += self.add_hp
#             self.recover()
    def show(self, game_state):
        if game_state == STATUS:
            print u"%s Lv:%3d HP %3d/%3d ATK %3d DEF %3d" % ( self.name, self.lv,  self.hp, self.max_hp, self.attack, self.defense)
            print u"        Exp %3d 次のレベルまで あと %-3d" % ( self.exp, (self.next_exp - self.exp))
        if game_state == BATTLE:
            print u"%s %3d/%3d" % ( self.name, self.hp, self.max_hp)
    def receive_damage(self, damage):
        self.hp  -= damage
        if self.hp <= 0:
            print u"%s は 倒れた" % (self.name)
            global game
            global game_stack
            del game_stack[:]
            game = Title()
            self.recover()
    def recover(self):
        self.hp = self.max_hp


#------------------------------------------------------------------------------

class PyRPG:
    def __init__(self):
        # Title
        global game
        game = Title()
        global player
        player = Player(u"勇者", 100, 20, 0)
        self.last_input = NONE
        # メインループを起動
        self.main_looop()
        # 終了は sys.exit()
    def main_looop(self):
        """メインループ"""
        re_draw = True
        turn = 0
        while True:
            if re_draw == True :
                self.update()
                if debug_print:
                    print "------------- %s %3d" % (STATE_NAME[game.game_state], turn)
                else:
                    print "------------------------"
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
        keys_mean = ["Left", "Down", "Up","Right", "Enter", "Cancel"]
        key_message = ""
        for i in range(len(keys)-1):
            key_message += " %s(%s)" % (keys[i],keys_mean[i])
            key_message += " or"
        else:
            key_message += " %s(%s)" % (keys[i+1],keys_mean[i+1])
        key_message += " : "
        if debug_print:
            in_txt = raw_input(key_message)
        else:
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
debug_print = False

if __name__ == "__main__":
    PyRPG()
