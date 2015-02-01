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
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
        elif key == ENTER:
            if self.select == Title.START:
                global game, player
                game = Event(Event.EVENT_OPENING)
                player = create_player()
            elif self.select == Title.CONTINUE:
                pass
            elif self.select == Title.EXIT:
                sys.exit()

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
                return True
            elif self.event_state == Event.EVENT_TOWN_TALK:
                game = game_stack.pop()
            elif self.event_state == Event.EVENT_MAOU_BEGIN:
                boss = create_boss()
                print u"%s が現れた" % (boss.name)
                game = Battle(boss)
                game_stack.append(Town())
                return True
            elif self.event_state == Event.EVENT_MAOU_END:
                game = Ending()
        return False
    def changed(self, key):
        if key == ENTER:
            self.turn += 1

class Town(GameBase):
    TALK, SLEEP, STATUS, NEXT = range(4)
    def __init__(self):
        GameBase.__init__(self)
        self.game_state = [ GameBase.TOWN ]
        self.select = 0
        self.selects = [u"話す", u"泊まる",u"メニューを開く", u"出発する"]
        self.is_action = False
    def draw(self):
        print u"ここは %s だよ" % (u"町")
        draw_select(self.select, self.selects)
    def update(self):
        if self.is_action:
            is_action = False
            return self.action()
        return False
    def changed(self, key):
        if   key == DOWN:
            self.select = forward_select(self.select, len(self.selects))
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
        elif key == ENTER:
            self.is_action = True
    def action(self):
        global game
        if   self.select == self.TALK:
            game_stack.append(game)
            game = Event(Event.EVENT_TOWN_TALK)
        elif self.select == self.SLEEP:
            player.recover()
            print u"全回復した"
            return True
        elif self.select == self.STATUS:
            game_stack.append(game)
            game = Menu()
        elif self.select == self.NEXT:
            game = Event(Event.EVENT_MAOU_BEGIN)
        return False


class CreateField():
    TYPE, NEXT, ENCOUNTER = range(3)
    def __init__(self):
        self.fields = []
        f = [ Field.GRASSLAND_1, 5 ,0.2 ]
        self.fields.append(f)
        f = [ Field.MOUNTAIN_1, 20 ,0.2 ]
        self.fields.append(f)
    def load_file(self, file_name):
        pass
    def create(self, field_state):
        return self.fields[field_state]

create_field = CreateField()

class Field(GameBase):
    GRASSLAND_1, MOUNTAIN_1 = range(2)
    def __init__(self, field_state):
        self.game_state = [ GameBase.FIELD ]
        self.move = 0
        self.is_move = False
        self.fild_state = fild_state
        self.f = create_field.create(self.fild_state)
    def draw(self):
        print u"元の町 -- %2d -- 次の町(%2d)" % (self.move, self.f[CreateField.NEXT])
    def update(self):
        if self.is_move:
            self.is_move = False
            return self.encounter(self.f[CreateField.ENCOUNTER])
        return False
    def changed(self, key):
        global game
        if key == RIGHT or key == DOWN:
            if self.move == self.next_town - 1:
                game = Town()
            else:
                self.move += 1
                self.is_move = True
        elif key == LEFT or key == UP:
            if not self.move == 0:
                self.move -= 1
                self.is_move = True
        elif key == ENTER:
            game_stack.append(game)
            game = Menu()
    def encounter(self, encounter_value):
        if random.random() <= encounter_value:
            print u"敵が現れた"
            global game
            game_stack.append(game)
            enemy = create_common()
            game = Battle(enemy)
            return True
        return False

class Menu(GameBase):
    STATUS, EQUIPMENT  = range(2)
    def __init__(self):
        self.game_state = [GameBase.MENU]
        self.subgame = None
        self.subgames = [MenuStatus, MenuEquipment]
        self.select = Menu.STATUS
        self.selects = [u"ステータス", u"装備"]
    def draw(self):
        print u"メニュー"
        draw_select(self.select, self.selects)
        if self.subgame is not None:
            to_none = self.subgame.draw()
    def update(self):
        if self.subgame is not None:
            is_draw = self.subgame.sub_update()
            return is_draw
        False
    def changed(self, key):
        if self.subgame is None:
            if   key == DOWN:
                self.select = forward_select(self.select, len(self.selects))
            elif key == UP:
                self.select = back_select(self.select, len(self.selects))
            elif key == ENTER:
                self.game_state.append(self.select)
                self.subgame = self.subgames[self.select]()
            elif key == CANCEL:
                global game
                game = game_stack.pop()
        else:
            re_draw, to_none = self.subgame.changed(key)
            if to_none == True:
                self.game_state.pop()
                self.subgame = None

class MenuStatus():
    def draw(self):
        print "--------"
        print u"ステータス"
        player.show()
    def sub_update(self):
        return False
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
    def sub_update(self):
        pass
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

class MenuEquipmentChange():
    pass

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
    FIGHT, ESCAPE = range(2)
    FIGHT_ATTACK, FIGHT_MAGIC, FIGHT_DEFFENSE = range(3)
    def __init__(self, enemy):
        self.game_state = [GameBase.BATTLE]
        self.enemy = enemy
        #
        self.subgame = None
        self.subgames = [Fight, Escape]
        self.select = Battle.FIGHT
        self.selects = [u"戦う",u"逃げる"]
    def draw(self):
        # プレイヤー
        player.show()
        # 敵
        self.enemy.show()
        # 選択肢
        draw_select(self.select, self.selects)
        if self.subgame is not None:
            to_none = self.subgame.draw()
    def update(self):
        if self.subgame is not None:
            no_battle, to_none = self.subgame.battle_update()
            if to_none:
                self.subgame = None
                if no_battle:
                    return True
            if no_battle:
                return False
            # 敵から
            if self.enemy.is_living() == True:
                print u"%s の攻撃" % (self.enemy.name)
                damage = calc_damage_from(self.enemy.attack, player)
                print u"%s に %3d" % (player.name, damage)
                player.receive_damage(damage)
            return True
        return False
    def changed(self, key):
        if self.subgame is None:
            if key == DOWN:
                self.select = forward_select(self.select, len(self.selects))
            elif key == UP:
                self.select = back_select(self.select, len(self.selects))
            elif key == ENTER:
                self.subgame = self.subgames[self.select](self.enemy)
        else:
            to_none = self.subgame.changed(key)
            if to_none == True:
                self.subgame = None

class Fight():
    def __init__(self, enemy):
        self.enemy = enemy
        self.selects = [u"攻撃", u"呪文", u"防御"]
        self.select = 0
        self.command  = None
        self.commands = [self.attack, self.magic, self.defense]
    def draw(self):
        draw_select(self.select, self.selects)
    def battle_update(self):
        if self.command is not None:
            self.command()
            self.command  = None
            return False, False
        return True, False
    def changed(self, key):
        if key == DOWN:
            self.select = forward_select(self.select, len(self.selects))
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
        elif key == ENTER:
            self.command = self.commands[self.select]
        elif key == CANCEL:
            return True
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
    pass

class Escape():
    def __init__(self, enemy):
        self.enemy = enemy
    def draw(self):
        pass
    def battle_update(self):
        battle_end = player.escape()
        return battle_end, True
    def changed(self, key):
        pass
#         return True
#         if key == ENTER:
#             player.escape()
#         elif key == CANCEL:
#             return True
#         return False


class Ending(GameBase):
    def __init__(self):
        self.game_state = [ GameBase.ENDING ]
    def draw(self):
        print "Fin"
    def changed(self, key):
        if key == ENTER:
            sys.exit()

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
            if game.game_state[1] == Menu.STATUS:
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
            return True
        else:
            print u"逃げるのに失敗した"
            return False

#--------------------------------------
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
    ''' 文字で返す '''
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
            os.system('cls')
            self.draw()
            self.check_event()
            self.update()

            turn += 1
            if debug_print:
                print "------------- %s %3d" % (GameBase.STATE_NAME[game.game_state[0]], turn)
    def draw(self):
        game.draw()
    def update(self):
        """ゲーム状態の更新
            描画があったら is_draw を True
        """
        is_draw = game.update()
        if is_draw:
            if os.name == "nt":
                raw = get_input()
            else:
                time.sleep(0.3)
    def check_event(self):
        key_dict = { ord("h"):LEFT, ord("j"):DOWN, ord("k"):UP,ord("l"):RIGHT, ord("a"):ENTER, ord("x"):CANCEL, ord("z"):ENTER, ord("c"):CANCEL, 13:ENTER }
        if os.name == "nt":
            raw = ord(get_input())
        else:
            raw = ord(raw_input())
            if raw == "":
                game.changed(self.last_key)
                return
        if raw in key_dict:
            self.last_key = key_dict[raw]
            game.changed(self.last_key)
        elif raw == ord("Q"):
            sys.exit()

#------------------------------------------------------------------------------
game = GameBase()
game_stack = []
player = CharacterBase()
debug_print = False
# debug_print = True

if __name__ == "__main__":
    PyRPG()
