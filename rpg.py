#!/usr/bin/env python
# vim: fileencoding=utf-8
# ver 1.0
import random
import sys

NONE, UP, DOWN, LEFT, RIGHT, ENTER, CANCEL = range(7)

#------------------------------------------------------------------------------
class GameBase:
    GAME_TITLE, GAME_EVENT, GAME_TOWN, GAME_FIELD, GAME_COMMAND, GAME_BATTLE, GAME_ENDING = range(7)
    STATE_NAME = ["GAME_TITLE", "GAME_EVENT", "GAME_TOWN", "GAME_FIELD", "GAME_COMMAND", "GAME_BATTLE", "GAME_ENDING" ]
    def __init__(self):
#         self.game_state = []
        pass
    def draw(self):
        pass
    def update(self):
        pass
    def changed(self, key):
        pass

class Title(GameBase):
    START, CONTINUE, EXIT = range(3)
    def __init__(self):
        self.game_state = [GameBase.GAME_TITLE]
        self.menu = self.START
        self.menus = ["START","CONTINUE", "EXIT"]
    def draw(self):
        # メニューカーソルの描画
        for i in range(len(self.menus)):
            if  self.menu == i:
                print " * " + self.menus[i]
            else:
                print "   " + self.menus[i]
    def changed(self, key):
        if key == DOWN:
            self.menu += 1
            if self.menu > 2:
                self.menu = 2
                return False
            return True
        elif key == UP:
            self.menu -= 1
            flag = True
            if self.menu < 0:
                self.menu = 0
                return False
            return True
        elif key == ENTER:
            if self.menu == Title.START:
                global game
                game = Event(Event.EVENT_OPENING)
                return True
            elif self.menu == Title.CONTINUE:
                pass
            elif self.menu == Title.EXIT:
                sys.exit()
        return False

class Event(GameBase):
    EVENT_OPENING, EVENT_TOWN_TALK, EVENT_MAOU_BEGIN, EVENT_MAOU_END, EVENT_ENDING = range(5)
    def __init__(self, event_state):
        self.game_state = [GameBase.GAME_EVENT]
        self.event_state = event_state
        self.end_event = False
        self.turn = 0
        if   self.event_state == Event.EVENT_OPENING:
            self.storys = [u"王様「勇者よ」",u"王様「この世界は魔王に侵略されておる」",u"王様「魔王を倒してくれ」",u"王様「武器と防具を与えよう」",u"王様「まずは次の町に向かうのじゃ」"]
        elif self.event_state == Event.EVENT_TOWN_TALK:
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
                game_stack.append(Ending())
    def changed(self, key):
        if key == ENTER:
            self.turn += 1
            return True
        return False

class Town(GameBase):
    TALK, SLEEP, STATUS, NEXT = range(4)
    def __init__(self):
        GameBase.__init__(self)
        self.game_state = [ GameBase.GAME_TOWN ]
        self.menu = 0
        self.menus = [u"話す", u"泊まる",u"ステータスを見る", u"出発する"]
        print u"ここは %s だよ" % (u"町")
    def draw(self):
        for i in range(len(self.menus)):
            if  self.menu == i:
                print " * " + self.menus[i]
            else:
                print "   " + self.menus[i]
    def changed(self, key):
        if   key == DOWN:
            self.menu += 1
            self.menu %= len(self.menus)
            return True
        elif key == UP:
            self.menu += (len(self.menus) - 1)
            self.menu %= len(self.menus)
            return True
        elif key == ENTER:
            self.action()
            return True
        return False
    def action(self):
        global game
        if   self.menu == self.TALK:
            game_stack.append(game)
            game = Event(Event.EVENT_TOWN_TALK)
        elif self.menu == self.SLEEP:
            player.recover()
            print u"全回復した"
        elif self.menu == self.STATUS:
            game_stack.append(game)
            game = Command()
        elif self.menu == self.NEXT:
            game = Event(Event.EVENT_MAOU_BEGIN)

class Field(GameBase):
    def __init__(self):
        self.game_state = [ GameBase.GAME_FIELD ]
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
            enemy = create_enemy()
            game = Battle(enemy)
    def changed(self, key):
        global game
        if key == RIGHT or key == UP:
            if self.move == self.next_town - 1:
                game = Town()
                return True
            else:
                self.move += 1
                self.encount()
                return True
        elif key == LEFT or key == DOWN:
            if not self.move == 0:
                self.move -= 1
                self.encount()
                return True
        elif key == ENTER:
            game_stack.append(game)
            game = Command()
            return True
        return False

class Command(GameBase):
    COMMAND_STATUS, COMMAND_EQUIPMENT  = range(2)
    def __init__(self):
        self.game_state = [GameBase.GAME_COMMAND]
        self.subgame = None
        self.menu = Command.COMMAND_STATUS
        self.menus = [u"ステータス", u"装備"]
    def draw(self):
        print u"メニュー"
        for i in range(len(self.menus)):
            if  self.menu == i:
                print " * " + self.menus[i]
            else:
                print "   " + self.menus[i]
        if self.subgame is not None:
            to_none = self.subgame.draw()
    def update(self):
        pass
    def changed(self, key):
        if self.subgame is None:
            if   key == DOWN:
                self.menu = (self.menu + 1) % len(self.menus)
                return True
            elif key == UP:
                self.menu = (self.menu + len(self.menus) - 1) % len(self.menus)
                return True
            elif key == ENTER:
                self.game_state.append(self.menu)
                if self.menu == self.COMMAND_STATUS:
                    self.subgame = CommandStatus()
                elif self.menu == self.COMMAND_EQUIPMENT:
                    self.subgame = CommandEquipment()
                return True
            elif key == CANCEL:
                global game
                game = game_stack.pop()
                return True
            return False
        else:
            re_draw, to_none = self.subgame.changed(key)
            if to_none == True:
                self.subgame = None
            return re_draw
        return False

class CommandStatus():
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

class CommandEquipment():
    WEAPON, ARMOR = range(2)
    SELECT_TYPE, SELECT_ITEM = range(2)
    def __init__(self):
        self.menu = CommandEquipment.WEAPON
        self.menus = [u"武器", u"防具"]
        self.mode = CommandEquipment.SELECT_TYPE
        self.sub_menu = 0
        self.sub_menus = [u"そのまま"]
    def draw(self):
        print "--------"
        print u"装備"
        if self.mode == CommandEquipment.SELECT_TYPE:
            for i in range(len(self.menus)):
                if  self.menu == i:
                    print " * " + self.menus[i] + " " + player.str_equipment(i)
                else:
                    print "   " + self.menus[i] + " " + player.str_equipment(i)
        elif self.mode == CommandEquipment.SELECT_ITEM:
            for i in range(len(self.menus)):
                if  self.menu == i:
                    print "   " + self.menus[i], player.str_equipment(i) + "  ",
                    for j in range(len(self.sub_menus)):
                        if  self.sub_menu == j:
                            print " *",
                        else:
                            print "  ",
                        print self.sub_menus[j],
                    print
                else:
                    print "   " + self.menus[i] + " " + player.str_equipment(i)
    def changed(self, key):
        if self.mode == CommandEquipment.SELECT_TYPE:
            if   key == DOWN:
                self.menu = (self.menu + 1) % len(self.menus)
                return True, False
            elif key == UP:
                self.menu = (self.menu + len(self.menus) - 1) % len(self.menus)
                return True, False
            elif key == ENTER:
                self.mode = CommandEquipment.SELECT_ITEM
                if self.menu == CommandEquipment.WEAPON:
                    for item in player.wepon[1:]:
                        s = item.name + ("%+3d" % (item.value - player.wepon[0].value))
                        self.sub_menus.append(s)
                elif self.menu == CommandEquipment.ARMOR:
                    for item in player.armor[1:]:
                        s = item.name + ("%+3d" % (item.value - player.armor[0].value))
                        self.sub_menus.append(s)
                return True, False
            elif key == CANCEL:
                return True, True
            return False, False
        elif self.mode == CommandEquipment.SELECT_ITEM:
            if   key == RIGHT:
                self.sub_menu = (self.sub_menu + 1) % len(self.sub_menus)
                return True, False
            elif key == LEFT:
                self.sub_menu = (self.sub_menu + len(self.sub_menus) - 1) % len(self.sub_menus)
                return True, False
            elif key == ENTER:
                player.change_item(self.menu, self.sub_menu)
                return True, False
            elif key == CANCEL:
                self.mode = CommandEquipment.SELECT_TYPE
                self.sub_menu = 0
                self.sub_menus = [u"そのまま"]
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
    START_FIGHT, START_EXIT = range(2)
    FIGHT_ATTACK, FIGHT_MAGIC, FIGHT_DEFFENSE = range(3)
    def __init__(self, enemy):
        self.game_state = [GameBase.GAME_BATTLE]
        self.enemy = enemy
        #
        self.b_state = Battle.B_START
        self.menu = Battle.START_FIGHT
        self.is_battle = False
        self.command = self.attack
    def draw(self):
        # プレイヤー
        player.show()
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
            if self.menu == Battle.FIGHT_ATTACK:
                menus[0] = " * " + menus[0]
                menus[1] = "   " + menus[1]
                menus[2] = "   " + menus[2]
            elif self.menu == Battle.FIGHT_MAGIC:
                menus[0] = "   " + menus[0]
                menus[1] = " * " + menus[1]
                menus[2] = "   " + menus[2]
            elif self.menu == Battle.FIGHT_DEFFENSE:
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
                damage = calc_damage_from(self.enemy.attack, player)
                print u"%s に %3d" % (player.name, damage)
                player.receive_damage(damage)
    def changed(self, key):
        self.is_battle = False
        if key == DOWN:
            if self.b_state == Battle.B_START:
                self.menu += 1
                self.menu %= 2
                return True
            elif self.b_state == Battle.B_COMMAND:
                self.menu += 1
                self.menu %= 3
                return True
        elif key == UP:
            if self.b_state == Battle.B_START:
                self.menu += (2 - 1)
                self.menu %= 2
                return True
            elif self.b_state == Battle.B_COMMAND:
                self.menu += (3 - 1)
                self.menu %= 3
                return True
        elif key == ENTER:
            if self.b_state == Battle.B_START:
                if self.menu == Battle.START_FIGHT:
                    self.b_state = Battle.B_COMMAND
                    self.menu = 0
                    return True
                elif self.menu == Battle.START_EXIT:
                    return self.escape()
            elif self.b_state == Battle.B_COMMAND:
                self.is_battle = True
                if   self.menu == Battle.FIGHT_ATTACK:
                    self.command = self.attack
                    return True
                elif self.menu == Battle.FIGHT_MAGIC:
                    self.command = self.magic
                elif self.menu == Battle.FIGHT_DEFFENSE:
                    self.command = self.defense
                    return True
        elif key == CANCEL:
            pass
        return False
    def escape(self):
        r = random.randint(1,100)
        if r < 50:
            global game
            game = game_stack.pop()
            print u"逃げ出した"
        else:
            print u"逃げるのに失敗した"
        return True
    def attack(self):
        print u"%s の攻撃" % (player.name)
        damage = calc_damage_to(self.enemy.defense, player)
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

class Ending(GameBase):
    def __init__(self):
        self.game_state = [ GameBase.GAME_ENDING ]
    def draw(self):
        print "Fin"
    def changed(self, key):
        if key == ENTER:
            sys.exit()
        return True

#------------------------------------------------------------------------------
def create_boss():
    boss = Enemy(u"魔王", 300, 10, 0, 1000, 1000)
    return boss

def create_enemy():
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
    def show(self):
        print "%s" % ( self.name)
    def is_living(self):
        if self.hp <= 0:
            return False
        return True

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
    def show(self):
        if game.game_state[0] == GameBase.GAME_COMMAND:
            if game.game_state[1] == Command.COMMAND_STATUS:
                print u"%s Lv:%3d HP %3d/%3d ATK %3d DEF %3d" % ( self.name, self.lv,  self.hp, self.max_hp, self.attack, self.defense)
                print u"        %s %+3d %s %+3d" % (self.wepon[0].name, self.wepon[0].value, self.armor[0].name, self.armor[0].value)
                print u"        Exp %3d 次のレベルまで あと %-3d" % ( self.exp, (self.next_exp - self.exp))
        if game.game_state[0] == GameBase.GAME_BATTLE:
            print u"%s %3d/%3d" % ( self.name, self.hp, self.max_hp)
    def str_equipment(self, equip):
        if equip == CommandEquipment.WEAPON:
            return self.wepon[0].name
        elif equip == CommandEquipment.ARMOR:
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
        if select_type == CommandEquipment.WEAPON:
            self.wepon[0], self.wepon[select_num] = self.wepon[select_num], self.wepon[0]
            print self.wepon[0].name, u"を装備した"
        elif select_type == CommandEquipment.Armor:
            self.armor[0], self.armor[select_num] = self.armor[select_num], self.armor[0]
            print self.armor[0].name, u"を装備した"
    def add_exp(self, exp):
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
class PyRPG:
    def __init__(self):
        global game
        game = Title()
#         game = Field()
        global player
        player = create_player()
        self.last_key = NONE
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
                    print "------------- %s %3d" % (GameBase.STATE_NAME[game.game_state[0]], turn)
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
            raw = raw_input(key_message)
        else:
            raw = raw_input()
        if raw == "":
            re_draw = game.changed(self.last_key)
        elif raw == "Q":
            sys.exit()
        if raw in keys:
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
            elif raw == "a":
                re_draw = game.changed(ENTER)
                self.last_key = ENTER
            elif raw == "x":
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
