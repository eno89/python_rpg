#!/usr/bin/env python
# vim: fileencoding=utf-8
# ver 1.02
import random
import sys, os, traceback
import time
# Windows
if os.name == "nt":
    import msvcrt
    CLEAR_SCREEN = 'cls'
else:
    CLEAR_SCREEN = 'clear'


NONE, UP, DOWN, LEFT, RIGHT, ENTER, CANCEL = range(7)
#------------------------------------------------------------------------------
class GameBase:
    TITLE, EVENT, TOWN, FIELD, MENU, BATTLE, ENDING = range(7)
    STATE_NAME = ["TITLE", "EVENT", "TOWN", "FIELD", "MENU", "BATTLE", "ENDING" ]
    def __init__(self):
        self.game_state = []
        pass
    def draw(self):
        pass
    def update(self):
        pass
    def changed(self, key):
        pass

class SubGame():
    def __init__(self, depth):
        self.depth = depth
        self.sub_select = 0
        self.sub_selects = []
        self.is_action = False
    def draw(self):
        head = " " * self.depth * 2
        draw_buffer.append(head + "--------")
    def sub_update(self):
        if self.is_action:
            self.is_action = False
            is_change = (False)
            return is_change
        return False
    def sub_changed(self, key):
        if   key == RIGHT:
            self.sub_select = forward_select(self.sub_select, len(self.sub_selects))
        elif key == LEFT:
            self.sub_select = back_select(self.sub_select, len(self.sub_selects))
        elif key == ENTER:
            self.is_action = True
        elif key == CANCEL:
            return True
        return False

class SubGameRecursive(SubGame):
    def __init__(self, depth):
        SubGame.__init__(self, depth)
        self.subgame = None
        self.subgames = []
    def draw(self):
        SubGame.draw(self, depth)
    def sub_update(self):
        if self.subgame is not None:
            is_draw = self.subgame.sub_update()
            return is_draw
        return False
    def sub_changed(self, key):
        if self.subgame is None:
            if   key == RIGHT:
                self.sub_select = forward_select(self.sub_select, len(self.sub_selects))
            elif key == LEFT:
                self.sub_select = back_select(self.sub_select, len(self.sub_selects))
            elif key == ENTER:
                self.subgame = self.subgames[self.select](self.depth+1)
            elif key == CANCEL:
                return True
        else:
            to_none = self.subgame.sub_changed(key)
            if to_none == True:
                self.subgame = None
        return False

def draw_select(select, selects, depth = 0):
    '''選択肢の描画 '''
    head = " " * depth * 2
    for i in range(len(selects)):
        st = head
        if  select == i:
            st += " * "
        else:
            st += "   "
        st += selects[i]
        draw_buffer.append(st)

def draw_lr_select(select, selects, depth = 0):
    '''選択肢の描画 左右'''
    head = " " * depth * 2
    st = ""
    for i in range(len(selects)):
        st += head
        if  select == i:
            st += " * "
        else:
            st += "   "
        st += selects[i]
    draw_buffer.append(st)

def forward_select(select, selects_len):
    return (select + 1) % selects_len

def back_select(select, selects_len):
    return (select + selects_len - 1) % selects_len

#--------------------------------------
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
                game_stack.append(Town(Town.KINGDOM))
                game = Event(Event.EVENT_OPENING)
                player = create_player()
            elif self.select == Title.CONTINUE:
                pass
            elif self.select == Title.EXIT:
                sys.exit()

#--------------------------------------
class Event(GameBase):
    EVENT_OPENING, EVENT_TOWN_TALK, EVENT_MAOU_BEGIN, EVENT_MAOU_END, EVENT_ENDING = range(5)
    def __init__(self, event_state):
        self.game_state = [GameBase.EVENT]
        self.event_state = event_state
        self.end_event = False
        self.turn = 0
        storys_list = [ [u"王様「勇者よ」",u"王様「この世界は魔王に侵略されておる」",u"王様「魔王を倒してくれ」",u"王様「武器と防具を与えよう」",u"王様「まずは次の町に向かうのじゃ」"],
                             [u"「次は魔王城だよ」"],
                             [u"魔王「よく来たな勇者よ」", u"魔王「ここがお前の墓場だ」"],
                             [u"魔王「ぐふ」"],
                             [] ]
        self.storys = storys_list[event_state]
    def message(self):
        return self.storys[self.turn]
    def draw(self):
        s = self.message()
        draw_buffer.append(s)
    def update(self):
        self.turn += 1
        if len(self.storys) == self.turn:
            self.end_event = True
        if self.end_event == True:
            global game
            if   self.event_state == Event.EVENT_OPENING:
                items =  [Wepon(u"棍棒", 3, 20),Wepon(u"銅剣", 5, 60)]
                for item in items:
                    player.add_item(item)
                game = game_stack.pop()
                return True
            elif self.event_state == Event.EVENT_TOWN_TALK:
                game = game_stack.pop()
            elif self.event_state == Event.EVENT_MAOU_BEGIN:
                boss = GroupEnemy(create_boss())
                boss.set_event(Event.EVENT_MAOU_END)
                print u"%s が現れた" % (boss.get_name())
                game_stack.append(Town(Town.MAOU))
                game = Battle(boss)
                return True
            elif self.event_state == Event.EVENT_MAOU_END:
                game = Ending()
        return False
    def changed(self, key):
        if key == ENTER:
            pass

#--------------------------------------
class Town(GameBase):
    KINGDOM, TOWN_1, MAOU = range(3)
    def __init__(self, town_state):
        GameBase.__init__(self)
        self.game_state = [ GameBase.TOWN ]
        self.select = 0
        self.is_action = False
        #
        e = create_town.create(town_state)
        self.name = e[CreateTown.NAME]
        self.selects = e[CreateTown.SELECTS]
        self.action = e[CreateTown.ACTION]
    def draw(self):
        draw_buffer.append(u"== %s ==" % (self.name))
        draw_select(self.select, self.selects)
    def update(self):
        if self.is_action:
            self.is_action = False
            return self.action(self.select)
        return False
    def changed(self, key):
        if   key == DOWN:
            self.select = forward_select(self.select, len(self.selects))
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
        elif key == ENTER:
            self.is_action = True

def kingdom_action(select):
    SLEEP, MENU, NEXT = range(3)
    global game
    if select == SLEEP:
        player.recover()
        print u"全回復した"
        return True
    elif select == MENU:
        game_stack.append(game)
        game = Menu()
    elif select == NEXT:
        game = Field(Field.GRASSLAND_1)
    return False

def town_1_action(select):
    TALK, SLEEP, MENU, BACK, NEXT = range(5)
    global game
    if   select == TALK:
        game_stack.append(game)
        game = Event(Event.EVENT_TOWN_TALK)
    elif select == SLEEP:
        player.recover()
        print u"全回復した"
        return True
    elif select == MENU:
        game_stack.append(game)
        game = Menu()
    elif select == BACK:
        game = Field(Field.GRASSLAND_1, True)
    elif select == NEXT:
        game = Field(Field.MOUNTAIN_1)
    return False

def maou_action(select):
    SLEEP, MENU, BACK, FIGHT = range(4)
    global game
    if select == SLEEP:
        player.recover()
        print u"全回復した"
        return True
    elif select == MENU:
        game_stack.append(game)
        game = Menu()
    elif select == BACK:
        game = Field(Field.MOUNTAIN_1, True)
    elif select == FIGHT:
        game = Event(Event.EVENT_MAOU_BEGIN)
    return False

class CreateTown():
    STATE, NAME, SELECTS, ACTION = range(4)
    def __init__(self):
        self.elements = []
        #
        state = Town.KINGDOM
        name = u"王都"
        selects = [ u"泊まる",u"メニューを開く", u"出発する"]
        e = [ state, name, selects, kingdom_action]
        self.elements.append(e)
        #
        state = Town.TOWN_1
        name = u"町"
        selects = [u"話す", u"泊まる",u"メニューを開く", u"戻る", u"出発する"]
        e = [ state, name, selects, town_1_action]
        self.elements.append(e)
        #
        state = Town.MAOU
        name = u"魔王城"
        selects = [u"回復ポイント",u"メニューを開く", u"戻る", u"戦う"]
        e = [ state, name, selects, maou_action]
        self.elements.append(e)
    def load_file(self, file_name):
        pass
    def create(self, state):
        return self.elements[state]

create_town = CreateTown()

#--------------------------------------
class Field(GameBase):
    GRASSLAND_1, MOUNTAIN_1 = range(2)
    def __init__(self, field_state, is_reverse=False):
        self.game_state = [ GameBase.FIELD ]
        self.move = 0
        self.is_move = False
        #
        e = create_field.create(field_state)
        self.distance  = e[CreateField.DISTANCE]
        self.encounter = e[CreateField.ENCOUNTER]
        self.start     = e[CreateField.START]
        self.arrive    = e[CreateField.ARRIVE]
        self.random_enemys = RandomEnemys(self.encounter)
        if is_reverse:
            self.reverse()
    def draw(self):
        st = "="
        for i in range(self.distance+1):
            if i == self.move:
                st += "*"
            else:
                st += " "
        st += "="
        draw_buffer.append(st)
    def update(self):
        if self.is_move:
            self.is_move = False
            return self.random_enemys.check_encounter()
        return False
    def changed(self, key):
        global game
        if key == RIGHT or key == DOWN:
            if self.move == self.distance:
                game = Town(self.arrive)
            else:
                self.move += 1
                self.is_move = True
        elif key == LEFT or key == UP:
            if self.move == 0:
                game = Town(self.start)
            else:
                self.move -= 1
                self.is_move = True
        elif key == ENTER:
            game_stack.append(game)
            game = Menu()
    def reverse(self):
        self.move = self.distance

class CreateField():
    STATE, DISTANCE, ENCOUNTER, START, ARRIVE = range(5)
    def __init__(self):
        self.elements = []
        #
        e = [ Field.GRASSLAND_1, 5 ,0.2, Town.KINGDOM, Town.TOWN_1 ]
        self.elements.append(e)
        e = [ Field.MOUNTAIN_1, 20 ,0.2, Town.TOWN_1, Town.MAOU ]
        self.elements.append(e)
    def load_file(self, file_name):
        pass
    def create(self, field_state):
        return self.elements[field_state]

create_field = CreateField()

#--------------------------------------
class Menu(GameBase):
    STATUS, EQUIPMENT, ITEM  = range(3)
    def __init__(self):
        self.game_state = [GameBase.MENU]
        self.subgame = None
        self.subgames = [SMenuStatus, SMenuEquipment, SMenuItem]
        self.select = Menu.STATUS
        self.selects = [u"ステータス", u"装備", u"アイテム"]
    def draw(self):
        draw_buffer.append(u"メニュー")
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
                self.subgame = self.subgames[self.select](1)
            elif key == CANCEL:
                global game
                game = game_stack.pop()
        else:
            to_none = self.subgame.sub_changed(key)
            if to_none == True:
                self.game_state.pop()
                self.subgame = None

#----------------------------
class SMenuStatus():
    def __init__(self, depth):
        self.depth = depth
    def draw(self):
        head = " " * self.depth * 2
        draw_buffer.append( head + "--------" )
        draw_buffer.append( head + u"ステータス")
        player.show(self.depth)
    def sub_update(self):
        return False
    def sub_changed(self, key):
        if key == ENTER or key == CANCEL:
            return True
        return False

#----------------------------
class SMenuEquipment():
    WEAPON, ARMOR = range(2)
    def __init__(self, depth):
        self.depth = depth
        #
        self.select = SMenuEquipment.WEAPON
        self.selects = [u"武器", u"防具"]
        #
        self.subgame = None
        self.subgames_common = SEquipmentWeponAromor
        self.subgames_arg = [player.wepon, player.armor]
    def draw(self):
        head = " " * self.depth * 2
        draw_buffer.append( head + "--------" )
        draw_buffer.append( head + u"装備" )
        #
        selects2 = []
        for i in range(len(self.selects)):
            selects2.append(self.selects[i] + " " + player.str_equipment(i))
        draw_select(self.select, selects2,self.depth)
        #
        if self.subgame is not None:
            self.subgame.draw()
    def sub_update(self):
        if self.subgame is not None:
            is_draw = self.subgame.sub_update()
            return is_draw
        return False
    def sub_changed(self, key):
        if self.subgame is None:
            if key == DOWN:
                self.select = forward_select(self.select, len(self.selects))
            elif key == UP:
                self.select = back_select(self.select, len(self.selects))
            elif key == ENTER:
                self.subgame = self.subgames_common(self.depth+1, self.subgames_arg[self.select])
            elif key == CANCEL:
                return True
        else:
            to_none = self.subgame.sub_changed(key)
            if to_none == True:
                self.subgame = None
        return False

#------------------
def create_sub_selects(equipment):
    sub_selects = []
    for item in equipment:
        s = item.name + ("%+3d" % (item.value - equipment[0].value))
        sub_selects.append(s)
    return sub_selects

class SEquipmentWeponAromor(SubGame):
    def __init__(self, depth, equipment):
        self.equipment = equipment
        self.sub_select = 0
        self.sub_selects = create_sub_selects(self.equipment)
        self.depth = depth
        self.is_action = False
    def draw(self):
        SubGame.draw(self)
        draw_lr_select(self.sub_select, self.sub_selects, self.depth)
    def sub_update(self):
        if self.is_action:
            self.is_action = False
            is_change = player.change_item(0, self.sub_select)
            if is_change:
                self.sub_selects = create_sub_selects(self.equipment)
            return is_change
        return False
    def sub_changed(self, key):
        if   key == RIGHT:
            self.sub_select = forward_select(self.sub_select, len(self.sub_selects))
        elif key == LEFT:
            self.sub_select = back_select(self.sub_select, len(self.sub_selects))
        elif key == ENTER:
            self.is_action = True
        elif key == CANCEL:
            return True
        return False

#----------------------------
class SMenuItem(SubGame):
    pass

#--------------------------------------
def dice(n, m):
    # nDm  m面の n個振る
    s = 0
    for i in range(n):
        d = random.randint(1,m)
        s += d
    return s

def calc_damage_def(enemy, player):
    damage = enemy.attack ** 1.5 - (player.defense + player.armor[0].value)
    if player.is_defense:
        damage /= 3
    if damage < 0:
        damage = 0
    return damage

def calc_damage_atk(player, enemy):
    atk = player.attack + player.wepon[0].value
    damage = atk  - (enemy.defense)
    if damage < 0:
        damage = 0
    return damage

class Battle(GameBase):
    FIGHT, ESCAPE = range(2)
    def __init__(self, enemys):
        self.game_state = [GameBase.BATTLE]
        self.enemys = enemys
        #
        self.subgame = None
        self.subgames = [BattleFight, BattleEscape]
        self.select = Battle.FIGHT
        self.selects = [u"戦う",u"逃げる"]
    def draw(self):
        # プレイヤー
        player.show(0)
        # 敵
        self.enemys.show()
        # 選択肢
        draw_select(self.select, self.selects)
        if self.subgame is not None:
            self.subgame.draw()
    def update(self):
        if self.subgame is not None:
            no_battle, to_none = self.subgame.sub_battle_update()
            if to_none:
                self.subgame = None
                if no_battle:
                    return True
            if no_battle:
                return False
            # 敵から
            if self.enemys.is_living() == True:
                self.enemys.do_attack()
                player.battle_update()
            return True
        return False
    def changed(self, key):
        if self.subgame is None:
            if key == DOWN:
                self.select = forward_select(self.select, len(self.selects))
            elif key == UP:
                self.select = back_select(self.select, len(self.selects))
            elif key == ENTER:
                self.subgame = self.subgames[self.select](self.enemys, 1)
        else:
            to_none = self.subgame.sub_changed(key)
            if to_none == True:
                self.subgame = None

class BattleFight():
    ATTACK, MAGIC, DEFFENSE = range(3)
    def __init__(self, enemys, depth):
        self.enemys = enemys
        self.depth = depth
        #
        self.selects = [u"攻撃", u"呪文", u"防御"]
        self.select = 0
        self.action = None
        self.actions = [self.attack, self.magic, self.defense]
    def draw(self):
        head = " " * self.depth * 2
        draw_buffer.append( head + "--------" )
        draw_select(self.select, self.selects, self.depth)
    def sub_battle_update(self):
        if self.action is not None:
            self.action()
            self.action  = None
            return False, False
        return True, False
    def sub_changed(self, key):
        if key == DOWN:
            self.select = forward_select(self.select, len(self.selects))
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
        elif key == ENTER:
            self.action = self.actions[self.select]
        elif key == CANCEL:
            return True
        return False
    def attack(self):
        self.enemys.receive()
        if self.enemys.is_living() == False:
            print u"%s を倒した" % (self.enemys.get_name())
            player.add_exp(self.enemys.get_exp())
            player.add_money(self.enemys.get_money())
            global game
            if self.enemys.event is None:
                game = game_stack.pop()
            else:
                game = Event(self.enemys.event)
    def magic(self):
        pass
    def defense(self):
        player.is_defense = True
        print u"%s は 防御した" % (player.name)
    pass

class BattleEscape():
    def __init__(self, enemys, depth):
        self.enemys = enemys
        self.depth = depth
    def draw(self):
        head = " " * self.depth * 2
        draw_buffer.append( head + "--------" )
    def sub_battle_update(self):
        battle_end = player.escape()
        return battle_end, True
    def sub_changed(self, key):
        pass

#--------------------------------------
class Ending(GameBase):
    def __init__(self):
        self.game_state = [ GameBase.ENDING ]
    def draw(self):
        draw_buffer.append("Fin")
    def changed(self, key):
        if key == ENTER:
            sys.exit()

#------------------------------------------------------------------------------
class RandomEnemys():
    def __init__(self, encounter, rmax=3):
        self.encounter = encounter
        self.rmax = rmax
    def create(self):
        r = random.randint(1,self.rmax)
        enemys = GroupEnemy()
        st = ["A","B","C"]
        for i in range(r):
            enemys.append(create_common(st[i]))
        return enemys
    def check_encounter(self):
        if random.random() <= self.encounter:
            print u"敵が現れた"
            global game
            game_stack.append(game)
            enemys = self.create()
            game = Battle(enemys)
            return True
        return False

def create_boss():
    boss = Enemy(u"魔王", 300, 10, 10, 1000, 1000)
    return boss

def create_common(name):
    enemy = Enemy(u"スライム"+name, 30, 5, 5, 10, 5)
    return enemy

# def create_common():
#     enemy = Enemy(u"スライム", 30, 5, 5, 10, 5)
#     return enemy

def create_player():
    player = Player(u"勇者", 100, 10, 10, 10, 4, 2, 10)
    return player

class CharacterBase:
    def __init__ (self):
        pass

class GroupEnemy:
    def __init__ (self, *args):
        self.group = []
        for e in args:
            self.group.append(e)
        #
        self.event = None
    def append(self, e):
        self.group.append(e)
    def show(self):
        for e in self.group:
            if e.is_living():
                e.show()
            else:
                print
    def is_living(self):
        for e in self.group:
            if e.is_living():
                return True
        return False
    def livinglist(self):
        lives = [0] * len(self.group)
        for i in range(len(self.group)):
            if self.group[i].is_living():
                lives[i] = 1
#         return sum(lives)
        return lives
    def do_attack(self):
        for e in self.group:
            if e.is_living():
                print u"%s の攻撃" % (e.name)
                damage = calc_damage_def(e, player)
                print u"%s に %3d" % (player.name, damage)
                player.receive_damage(damage)
    def receive(self):
        llist = self.livinglist()
#         r = random.randint(0, sum(llist) - 1)
        r = sum(llist) - 1
        e = self.group[r]
        print u"%s の攻撃" % (player.name)
        damage = calc_damage_atk(player, e)
        print u"%s に %3d" % (e.name, damage)
        e.receive_damage(damage)
    def get_name(self):
        return self.group[0].name
    def get_exp(self):
        s = 0
        for e in self.group:
            s += e.exp
        return s
    def get_money(self):
        s = 0
        for e in self.group:
            s += e.money
        return s
    def set_event(self, ev):
        self.event = ev

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
    def is_living(self):
        if self.hp <= 0:
            return False
        return True

class Enemy(Character):
    def __init__ (self, name, hp, attack, defense, exp, money):
        Character.__init__(self, name, hp, attack, defense)
        self.exp = exp
        self.money = money
    def show(self):
        print "%s" % ( self.name) ,
        p = self.hp * 5 / self.max_hp
        st = "*" * int(p)
        print st
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
        #
        self.is_defense = False
    def show(self, depth):
        head = " " * depth * 2
        if game.game_state[0] == GameBase.MENU:
            if game.game_state[1] == Menu.STATUS:
                print head + u"お金 %5d" % ( self.money)
                print head + u"%s Lv:%3d HP %3d/%3d ATK %3d DEF %3d" % ( self.name, self.lv,  self.hp, self.max_hp, self.attack, self.defense)
                print head + u"        %s %+3d %s %+3d" % (self.wepon[0].name, self.wepon[0].value, self.armor[0].name, self.armor[0].value)
                print head + u"        Exp %3d 次のレベルまで あと %-3d" % ( self.exp, (self.next_exp - self.exp))
        if game.game_state[0] == GameBase.BATTLE:
            print head +  u"%s %3d/%3d" % ( self.name, self.hp, self.max_hp)
    def str_equipment(self, equipment):
        if equipment == SMenuEquipment.WEAPON:
            return self.wepon[0].name
        elif equipment == SMenuEquipment.ARMOR:
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
            if select_type == SMenuEquipment.WEAPON:
                self.wepon[0], self.wepon[select_num] = self.wepon[select_num], self.wepon[0]
                print self.wepon[0].name, u"を装備した"
            elif select_type == SMenuEquipment.Armor:
                self.armor[0], self.armor[select_num] = self.armor[select_num], self.armor[0]
                print self.armor[0].name, u"を装備した"
            return True
        return False
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
    def battle_update(self):
        self.is_defense = False

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
        self.main_loop()
        # 終了は sys.exit()
    def main_loop(self):
        """メインループ"""
        turn = 0
        try:
            while True:
                # 画面クリア，描画，キー入力，イベント処理，イベント処理キー入力
                os.system(CLEAR_SCREEN)
                self.draw()
                self.check_event()
                os.system(CLEAR_SCREEN)
                self.draw()
                self.update()
                turn += 1
                if debug_print:
                    print "------------- %s %3d" % (GameBase.STATE_NAME[game.game_state[0]], turn)
        except:
            traceback.print_exc()
        else:
            print "END"
    def draw(self):
        game.draw()
        global draw_buffer
        if len(draw_buffer) != 0:
            for s in draw_buffer:
                print s
            draw_buffer = []
    def update(self):
        """ゲーム状態の更新
            描画があったら is_draw を True
        """
        is_draw = game.update()
        if is_draw:
            if os.name == "nt":
                raw = get_input()
            else:
                time.sleep(0.5)
    def check_event(self):
        key_dict = { ord("h"):LEFT, ord("j"):DOWN, ord("k"):UP,ord("l"):RIGHT, ord("a"):ENTER, ord("x"):CANCEL, ord("z"):ENTER, ord("c"):CANCEL, 13:ENTER }
        if os.name == "nt":
            raw = ord(get_input())
        else:
            raw = raw_input()
            if len(raw) == 1:
                raw = ord(raw)
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
random.seed(1)
draw_buffer = []
update_buffer = []

if __name__ == "__main__":
    PyRPG()
