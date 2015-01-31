#!/usr/bin/env python
# vim: fileencoding=utf-8
# ver 1.01
import random
import sys
import os
import time
# Windows
if os.name == "nt":
    import msvcrt


NONE, UP, DOWN, LEFT, RIGHT, ENTER, CANCEL = range(7)
#------------------------------------------------------------------------------
class GameBase:
    TITLE, EVENT, TOWN, FIELD, MENU, BATTLE, ENDING = range(7)
    STATE_NAME = ["TITLE", "EVENT", "TOWN", "FIELD", "MENU", "BATTLE", "ENDING" ]
    def __init__(self):
#         self.game_state = []
        pass
    def draw(self):
        pass
    def update(self):
        pass
    def changed(self, key):
        pass

def draw_select(select, selects):
    '''選択肢の描画 '''
    for i in range(len(selects)):
        if  select == i:
            print " * " + selects[i]
        else:
            print "   " + selects[i]

def forward_select(select, selects_len):
    return (select + 1) % selects_len

def back_select(select, selects_len):
    return (select + selects_len - 1) % selects_len

class Title(GameBase):
    START, CONTINUE, EXIT = range(3)
    def __init__(self):
        self.game_state = [GameBase.TITLE]
        self.select = self.START
        self.selects = ["START","CONTINUE", "EXIT"]
    def draw(self):
        draw_select(self.select, self.selects)
    def changed(self, key):
        if key == DOWN:
            self.select = forward_select(self.select, len(self.selects))
            return True
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
            return True
        elif key == ENTER:
            if self.select == Title.START:
                global game, player
                game = Event(Event.EVENT_OPENING)
                player = create_player()
                return True
            elif self.select == Title.CONTINUE:
                pass
            elif self.select == Title.EXIT:
                sys.exit()
        return False

class Event(GameBase):
    EVENT_OPENING, EVENT_TOWN_TALK, EVENT_MAOU_BEGIN, EVENT_MAOU_END, EVENT_ENDING = range(5)
    def __init__(self, event_state):
        self.game_state = [GameBase.EVENT]
        self.event_state = event_state
        self.end_event = False
        self.turn = 0
        if   self.event_state == Event.EVENT_OPENING:
            self.storys = [u"王様「勇者よ」",u"王様「この世界は魔王に侵略されておる」",u"王様「魔王を倒してくれ」",u"王様「武器と防具を与えよう」",u"王様「まずは次の町に向かうのじゃ」"]
        elif self.event_state == Event.EVENT_TOWN_TALK:
            self.storys = [u"「次は魔王城だよ」"]
        elif self.event_state == Event.EVENT_MAOU_BEGIN:
            self.storys = [u"魔王「よく来たな勇者よ」", u"魔王「ここがお前の墓場だ」"]
        elif self.event_state == Event.EVENT_MAOU_END:
            self.storys = [u"魔王「ぐふ」"]
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
            if   self.event_state == Event.EVENT_OPENING:
                items =  [Wepon(u"棍棒", 3, 20),Wepon(u"銅剣", 5, 60)]
                for item in items:
                    player.add_item(item)
                game = Field()
            elif self.event_state == Event.EVENT_TOWN_TALK:
                game = game_stack.pop()
            elif self.event_state == Event.EVENT_MAOU_BEGIN:
                boss = create_boss()
                print u"%s が現れた" % (boss.name)
                game = Battle(boss)
                game_stack.append(Town())
            elif self.event_state == Event.EVENT_MAOU_END:
                game = Ending()
    def changed(self, key):
        if key == ENTER:
            self.turn += 1
            return True
        return False

class Town(GameBase):
    TALK, SLEEP, STATUS, NEXT = range(4)
    def __init__(self):
        GameBase.__init__(self)
        self.game_state = [ GameBase.TOWN ]
        self.select = 0
        self.selects = [u"話す", u"泊まる",u"メニューを開く", u"出発する"]
    def draw(self):
        print u"ここは %s だよ" % (u"町")
        draw_select(self.select, self.selects)
    def changed(self, key):
        if   key == DOWN:
            self.select = forward_select(self.select, len(self.selects))
            return True
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
            return True
        elif key == ENTER:
            self.action()
            return True
        return False
    def action(self):
        global game
        if   self.select == self.TALK:
            game_stack.append(game)
            game = Event(Event.EVENT_TOWN_TALK)
        elif self.select == self.SLEEP:
            player.recover()
            print u"全回復した"
        elif self.select == self.STATUS:
            game_stack.append(game)
            game = Menu()
        elif self.select == self.NEXT:
            game = Event(Event.EVENT_MAOU_BEGIN)

class Field(GameBase):
    def __init__(self):
        self.game_state = [ GameBase.FIELD ]
        self.next_town = 20
        self.move = 0
        self.encounter_value = 0.2
    def draw(self):
        print u"次の町まで %2d/%2d" % (self.move, self.next_town)
    def encounter(self):
        if random.random() <= self.encounter_value:
            print u"敵が現れた"
            global game
            game_stack.append(game)
            enemy = create_common()
            game = Battle(enemy)
    def changed(self, key):
        global game
        if key == RIGHT or key == DOWN:
            if self.move == self.next_town - 1:
                game = Town()
                return True
            else:
                self.move += 1
                self.encounter()
                return True
        elif key == LEFT or key == UP:
            if not self.move == 0:
                self.move -= 1
                self.encounter()
                return True
        elif key == ENTER:
            game_stack.append(game)
            game = Menu()
            return True
        return False

class Menu(GameBase):
    COMMAND_STATUS, COMMAND_EQUIPMENT  = range(2)
    def __init__(self):
        self.game_state = [GameBase.MENU]
        self.subgame = None
        self.select = Menu.COMMAND_STATUS
        self.selects = [u"ステータス", u"装備"]
    def draw(self):
        print u"メニュー"
        draw_select(self.select, self.selects)
        if self.subgame is not None:
            to_none = self.subgame.draw()
    def update(self):
        pass
    def changed(self, key):
        if self.subgame is None:
            if   key == DOWN:
                self.select = forward_select(self.select, len(self.selects))
                return True
            elif key == UP:
                self.select = back_select(self.select, len(self.selects))
                return True
            elif key == ENTER:
                self.game_state.append(self.select)
                if self.select == self.COMMAND_STATUS:
                    self.subgame = MenuStatus()
                elif self.select == self.COMMAND_EQUIPMENT:
                    self.subgame = MenuEquipment()
                return True
            elif key == CANCEL:
                global game
                game = game_stack.pop()
                return True
            return False
        else:
            re_draw, to_none = self.subgame.changed(key)
            if to_none == True:
                self.game_state.pop()
                self.subgame = None
            return re_draw
        return False

class MenuStatus():
    def update(self):
        pass
    def draw(self):
        print "--------"
        print u"ステータス"
        player.show()
    def changed(self, key):
        if key == ENTER or key == CANCEL:
            return True, True
        return False, False

class MenuEquipment():
    WEAPON, ARMOR = range(2)
    SELECT_TYPE, SELECT_ITEM = range(2)
    def __init__(self):
        self.select = MenuEquipment.WEAPON
        self.selects = [u"武器", u"防具"]
        self.mode = MenuEquipment.SELECT_TYPE
        self.sub_select = 0
        self.sub_selects = []
    def draw(self):
        print "--------"
        print u"装備"
        if self.mode == MenuEquipment.SELECT_TYPE:
            for i in range(len(self.selects)):
                if  self.select == i:
                    print " * " + self.selects[i] + " " + player.str_equipment(i)
                else:
                    print "   " + self.selects[i] + " " + player.str_equipment(i)
        elif self.mode == MenuEquipment.SELECT_ITEM:
            for i in range(len(self.selects)):
                if  self.select == i:
                    print "   " + self.selects[i], player.str_equipment(i) + "  ",
                    for j in range(len(self.sub_selects)):
                        if  self.sub_select == j:
                            print " *",
                        else:
                            print "  ",
                        print self.sub_selects[j],
                    print
                else:
                    print "   " + self.selects[i] + " " + player.str_equipment(i)
    def set_sub_select(self):
        self.sub_selects = []
        if self.select == MenuEquipment.WEAPON:
            for item in player.wepon:
                s = item.name + ("%+3d" % (item.value - player.wepon[0].value))
                self.sub_selects.append(s)
        elif self.select == MenuEquipment.ARMOR:
            for item in player.armor:
                s = item.name + ("%+3d" % (item.value - player.armor[0].value))
                self.sub_selects.append(s)
    def changed(self, key):
        if self.mode == MenuEquipment.SELECT_TYPE:
            if   key == DOWN:
                self.select = forward_select(self.select, len(self.selects))
                return True, False
            elif key == UP:
                self.select = back_select(self.select, len(self.selects))
                return True, False
            elif key == ENTER:
                self.mode = MenuEquipment.SELECT_ITEM
                self.set_sub_select()
                return True, False
            elif key == CANCEL:
                return True, True
            return False, False
        elif self.mode == MenuEquipment.SELECT_ITEM:
            if   key == RIGHT:
                self.sub_select = (self.sub_select + 1) % len(self.sub_selects)
                return True, False
            elif key == LEFT:
                self.sub_select = (self.sub_select + len(self.sub_selects) - 1) % len(self.sub_selects)
                return True, False
            elif key == ENTER:
                player.change_item(self.select, self.sub_select)
                self.set_sub_select()
                return True, False
            elif key == CANCEL:
                self.mode = MenuEquipment.SELECT_TYPE
                self.sub_select = 0
                return True, False
        return False, False

def calc_damage_from(attack, pl):
    damage = attack  - (pl.defense + pl.armor[0].value)
    if damage < 0:
        damage = 0
    return damage

def calc_damage_to(defense, pl):
    damage = pl.attack + pl.wepon[0].value - (defense)
    if damage < 0:
        damage = 0
    return damage

class Battle(GameBase):
    B_START, B_COMMAND, B_BATTLE = range(3)
    START_FIGHT, START_ESCAPE = range(2)
    FIGHT_ATTACK, FIGHT_MAGIC, FIGHT_DEFFENSE = range(3)
    def __init__(self, enemy):
        self.game_state = [GameBase.BATTLE]
        self.enemy = enemy
        #
        self.b_state = Battle.B_START
        self.select = Battle.START_FIGHT
        self.selects = [u"戦う",u"逃げる"]
        self.is_battle = False
        self.command  = self.attack
        self.commands = [self.attack, self.magic, self.defense]
    def draw(self):
        # プレイヤー
        player.show()
        # 敵
        self.enemy.show()
        # 選択肢 クラス化するかも
        if self.b_state == Battle.B_START:
            draw_select(self.select, self.selects)
        elif self.b_state == Battle.B_COMMAND:
            draw_select(self.select, self.selects)
        elif self.b_state == Battle.B_BATTLE:
            pass
    def update(self):
        if self.is_battle == True:
            # 選択肢の処理
            self.command()
            # 敵から
            if self.enemy.is_living() == True:
                print u"%s の攻撃" % (self.enemy.name)
                damage = calc_damage_from(self.enemy.attack, player)
                print u"%s に %3d" % (player.name, damage)
                player.receive_damage(damage)
    def changed(self, key):
        self.is_battle = False
        if key == DOWN:
            self.select = forward_select(self.select, len(self.selects))
            return True
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
            return True
        elif key == ENTER:
            if self.b_state == Battle.B_START:
                if self.select == Battle.START_FIGHT:
                    self.selects = [u"攻撃", u"呪文", u"防御"]
                    self.select = 0
                    self.b_state = Battle.B_COMMAND
                    return True
                elif self.select == Battle.START_ESCAPE:
                    return player.escape()
            elif self.b_state == Battle.B_COMMAND:
                self.is_battle = True
                self.command = self.commands[self.select]
                return True
        elif key == CANCEL:
            pass
        return False
    def attack(self):
        print u"%s の攻撃" % (player.name)
        damage = calc_damage_to(self.enemy.defense, player)
        print u"%s に %3d" % (self.enemy.name, damage)
        self.enemy.receive_damage(damage)
        if self.enemy.is_living() == False:
            print u"%s を倒した" % (self.enemy.name)
            player.add_exp(self.enemy.exp)
            player.add_money(self.enemy.money)
            global game
            if self.enemy.event is None:
                game = game_stack.pop()
            else:
                game = Event(self.enemy.event)
    def magic(self):
        pass
    def defense(self):
        print u"%s は 防御した" % (player.name)

class Ending(GameBase):
    def __init__(self):
        self.game_state = [ GameBase.ENDING ]
    def draw(self):
        print "Fin"
    def changed(self, key):
        if key == ENTER:
            sys.exit()
        return True

#------------------------------------------------------------------------------
def create_boss():
    boss = Enemy(u"魔王", 300, 10, 0, 1000, 1000)
    boss.set_event(Event.EVENT_MAOU_END)
    return boss

def create_common():
    enemy = Enemy(u"スライム", 30, 5, 0, 10, 5)
    return enemy

def create_player():
    player = Player(u"勇者", 100, 20, 0, 10, 4, 2, 10)
    return player

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
    def show(self):
        pass

class Enemy(Character):
    def __init__ (self, name, hp, attack, defense, exp, money):
        Character.__init__(self, name, hp, attack, defense)
        self.exp = exp
        self.money = money
        self.event = None
    def show(self):
        print "%s" % ( self.name)
    def is_living(self):
        if self.hp <= 0:
            return False
        return True
    def set_event(self, ev):
        self.event = ev
    def receive_damage(self, damage):
        self.hp -= damage

class Player(Character):
    def __init__ (self, name, hp, attack, defense, inc_hp, inc_attack, inc_defense, inc_exp):
        Character.__init__(self, name, hp, attack, defense)
        self.inc_attack = inc_attack
        self.inc_defense = inc_defense
        self.inc_exp = inc_exp
        self.exp = 0
        self.money = 0
        self.lv = 1
        self.next_exp = self.lv * self.inc_exp
        self.inc_hp = inc_hp
        self.wepon = [Wepon(u"なし",0, 0)]
        self.armor = [Armor(u"なし",0, 0)]
        self.escape_value = 0.5
    def show(self):
        if game.game_state[0] == GameBase.MENU:
            if game.game_state[1] == Menu.COMMAND_STATUS:
                print u"お金 %5d" % ( self.money)
                print u"%s Lv:%3d HP %3d/%3d ATK %3d DEF %3d" % ( self.name, self.lv,  self.hp, self.max_hp, self.attack, self.defense)
                print u"        %s %+3d %s %+3d" % (self.wepon[0].name, self.wepon[0].value, self.armor[0].name, self.armor[0].value)
                print u"        Exp %3d 次のレベルまで あと %-3d" % ( self.exp, (self.next_exp - self.exp))
        if game.game_state[0] == GameBase.BATTLE:
            print u"%s %3d/%3d" % ( self.name, self.hp, self.max_hp)
    def str_equipment(self, equip):
        if equip == MenuEquipment.WEAPON:
            return self.wepon[0].name
        elif equip == MenuEquipment.ARMOR:
            return self.armor[0].name
        return ""
    def add_item(self, item):
        # あとでソートを入れる
        if isinstance(item, Wepon):
            self.wepon.append(item)
        elif isinstance(item, Armor):
            self.armor.append(item)
        print item.name, u"を手に入れた"
    def change_item(self, select_type, select_num):
        if select_num != 0:
            if select_type == MenuEquipment.WEAPON:
                self.wepon[0], self.wepon[select_num] = self.wepon[select_num], self.wepon[0]
                print self.wepon[0].name, u"を装備した"
            elif select_type == MenuEquipment.Armor:
                self.armor[0], self.armor[select_num] = self.armor[select_num], self.armor[0]
                print self.armor[0].name, u"を装備した"
    def add_money(self, money):
        print u"お金 +%3d" % (money)
        self.money += money
    def add_exp(self, exp):
        print u"EXP +%3d" % (exp)
        self.exp += exp
        while self.exp >= self.next_exp:
            # Lv Up
            self.lv += 1
            add_next_exp = self.lv * self.inc_exp
            self.next_exp += add_next_exp
            self.max_hp  += self.inc_hp
            self.attack  += self.inc_attack
            self.defense += self.inc_defense
            print u"%s は レベル が上がった +MAX_HP %2d +ATK %2d +DEF %3d" % ( self.name, self.inc_hp, self.inc_attack, self.inc_defense)
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
    def escape(self):
        if random.random() <= self.escape_value:
            global game
            game = game_stack.pop()
            print u"逃げ出した"
        else:
            print u"逃げるのに失敗した"
        return True

#------------------------------------------------------------------------------
class Item():
    def __init__ (self, name, value, price):
        self.name = name
        self.value = value
        self.price = price
    def show(self):
        pass
    def get_value(self):
        pass

class Wepon(Item):
    def __init__ (self, name, attack, price):
        Item.__init__(self, name, attack, price)

class Armor(Item):
    def __init__ (self, name, defense, price):
        Item.__init__(self, name, defense, price)

#------------------------------------------------------------------------------
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

class PyRPG:
    def __init__(self):
        global game
        game = Title()
        self.last_key = NONE
        # メインループを起動
        self.main_looop()
        # 終了は sys.exit()
    def main_looop(self):
        """メインループ"""
        re_draw = True
        turn = 0
        while True:
            # 画面クリア，描画，キー入力，イベント処理，イベント処理キー入力
            self.update()
            if debug_print:
                print "------------- %s %3d" % (GameBase.STATE_NAME[game.game_state[0]], turn)
            else:
                time.sleep(0.25)
                os.system('cls')
            turn += 1
            self.draw()
            self.check_event()
    def update(self):
        """ゲーム状態の更新"""
        game.update()
    def draw(self):
        game.draw()
    def check_event(self):
        re_draw = False
        if os.name == "nt":
            raw = get_input()
        else:
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
                raw = raw_input(key_message)
            else:
                raw = raw_input()
        if raw == "":
            re_draw = game.changed(self.last_key)
        elif raw == "Q":
            sys.exit()
#         if raw in keys:
        if raw == "h":
            re_draw = game.changed(LEFT)
            self.last_key = LEFT
        elif raw == "j":
            re_draw = game.changed(DOWN)
            self.last_key = DOWN
        elif raw == "k":
            re_draw = game.changed(UP)
            self.last_key = UP
        elif raw == "l":
            re_draw = game.changed(RIGHT)
            self.last_key = RIGHT
        elif raw == "a" or raw == "z":
            re_draw = game.changed(ENTER)
            self.last_key = ENTER
        elif raw == "x" or raw == "c":
            re_draw = game.changed(CANCEL)
            self.last_key = CANCEL
        return re_draw

#------------------------------------------------------------------------------
game = GameBase()
game_stack = []
player = CharacterBase()
debug_print = False
# debug_print = True

if __name__ == "__main__":
    PyRPG()
