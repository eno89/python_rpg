#!/usr/bin/env python
# vim: fileencoding=utf-8
# ver 1.05
import random
import sys, os, traceback
import time
# Windows

if os.name == "nt":
    import msvcrt
    class GameInput(object):
        def clear(self):
            CLEAR_SCREEN = 'cls'
            os.system(CLEAR_SCREEN)
        def get_input(self):
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
        def get_key(self):
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
            raw = get_input()
        def finish(self):
            pass
elif False:
# elif True:
    class GameInput(object):
        def __init__(self):
            self.last_key = NONE
        def clear(self):
            CLEAR_SCREEN = 'clear'
            os.system(CLEAR_SCREEN)
        def print_buffer(self, buff):
            for e in buff:
                print e
        def get_key(self):
            key = -1
            key_dict = { ord("h"):LEFT, ord("j"):DOWN, ord("k"):UP,ord("l"):RIGHT, ord("a"):ENTER, ord("x"):CANCEL, ord("z"):ENTER, ord("c"):CANCEL, 13:ENTER }
            raw_ch = raw_input()
            if raw_ch == "":
                return self.last_key
            if len(raw_ch) == 1:
                raw_ord = ord(raw_ch)
                if raw_ord in key_dict:
                    key = key_dict[raw_ord]
                    self.last_key = key
                elif raw_ord == ord("Q"):
                    key = FINISH
            return key
        def wait(self):
            time.sleep(0.5)
        def finish(self):
            pass
else:
    import curses
    class GameInput(object):
        def __init__(self):
            self.last_key = NONE
            self.screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.screen.keypad(1)
        def clear(self):
            self.screen.clear()
        def get_input_ord(self):
            corsors = {curses.KEY_UP:"k", curses.KEY_RIGHT:"l", curses.KEY_DOWN:"j", curses.KEY_LEFT:"h"}
            raw = self.screen.getch()
            if raw in corsors:
                ch = corsors[raw]
                return ord(ch)
            return raw
        def print_buffer(self, buff):
            for e in buff:
                self.screen.addstr(e+"\n")
        def get_key(self):
            key = -1
            key_dict = { ord("h"):LEFT, ord("j"):DOWN, ord("k"):UP,ord("l"):RIGHT, ord("a"):ENTER, ord("x"):CANCEL, ord("z"):ENTER, ord("c"):CANCEL, 13:ENTER }
            raw_ord = self.get_input_ord()
            if raw_ord in key_dict:
                key = key_dict[raw_ord]
            elif raw_ord == ord("Q"):
                key = FINISH
            return key
        def wait(self):
            time.sleep(0.5)
        def finish(self):
            curses.nocbreak()
            self.screen.keypad(0)
            curses.echo()
            curses.endwin()
# else:
#     class GameInput(object):
#         def __init__(self):
#             self.last_key = NONE
#         def clear(self):
#             CLEAR_SCREEN = 'clear'
#             os.system(CLEAR_SCREEN)
#         def get_input(self):
#             raw = raw_input()
#             ''' 文字で返す '''
#             corsors = {72:"k", 77:"l", 80:"j", 75:"h"}
#             while True:
#                 if msvcrt.kbhit():
#                     ch = msvcrt.getch()
#                     if ch == '\000' or ch == '\xe0':
#                         ch = msvcrt.getch()
#                         c = ord(ch)
#                         if c in corsors:
#                             ch = corsors[c]
#                     return ch
#         def wait(self):
#             time.sleep(0.5)
#         def finish(self):
#             pass

NONE, UP, DOWN, LEFT, RIGHT, ENTER, CANCEL, FINISH = range(8)
#------------------------------------------------------------------------------
# Game System
class GameBase:
    TITLE, EVENT, TOWN, FIELD, MENU, BATTLE, ENDING = range(7)
    STATE_NAME = ["TITLE", "EVENT", "TOWN", "FIELD", "MENU", "BATTLE", "ENDING" ]
    def __init__(self):
        self.game_state = []
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
        #
        self.is_action = False
    def draw(self):
        draw_select(self.select, self.selects)
    def update(self):
        if self.is_action:
            global game, party
            game_stack.append(Town(Town.KINGDOM))
            game = Event(Event.EVENT_OPENING)
            party = Party( create_player() )
    def changed(self, key):
        if key == DOWN:
            self.select = forward_select(self.select, len(self.selects))
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
        elif key == ENTER:
            if self.select == Title.START:
                self.is_action = True
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
                    party.add_item(item)
                game = game_stack.pop()
            elif self.event_state == Event.EVENT_TOWN_TALK:
                game = game_stack.pop()
            elif self.event_state == Event.EVENT_MAOU_BEGIN:
                boss = GroupEnemy(create_boss())
                boss.set_event(Event.EVENT_MAOU_END)
                update_buffer.append( u"%s が現れた" % (boss.get_name()) )
                game_stack.append(Town(Town.MAOU))
                game = Battle(boss)
            elif self.event_state == Event.EVENT_MAOU_END:
                game = Ending()
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
            self.action(self.select)
    def changed(self, key):
        if   key == DOWN:
            self.select = forward_select(self.select, len(self.selects))
        elif key == UP:
            self.select = back_select(self.select, len(self.selects))
        elif key == ENTER:
            self.is_action = True

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
            self.random_enemys.check_encounter()
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
            self.subgame.sub_update()
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
        party.show(self.depth)
    def sub_update(self):
        pass
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
        # x
        self.player = party.group[party.select]
        self.subgames_arg = [self.player.wepon, self.player.armor]
    def draw(self):
        head = " " * self.depth * 2
        draw_buffer.append( head + "--------" )
        draw_buffer.append( head + u"装備" )
        #
        selects2 = []
        for i in range(len(self.selects)):
            selects2.append(self.selects[i] + " " + self.player.str_equipment(i))
        draw_select(self.select, selects2,self.depth)
        #
        if self.subgame is not None:
            self.subgame.draw()
    def sub_update(self):
        if self.subgame is not None:
            self.subgame.sub_update()
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
        # 装備の交換，交換できたなら選択を更新
        if self.is_action:
            self.is_action = False
            is_change = party.change_item(0, self.sub_select)
            if is_change:
                self.sub_selects = create_sub_selects(self.equipment)
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
        party.show(0)
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
                return
            # 敵の行動の更新
            if self.enemys.is_living() == True:
                self.enemys.do_attack()
                party.battle_update()
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
            update_buffer.append( u"%s を倒した" % (self.enemys.get_name()) )
            party.add_exp(self.enemys.get_exp())
            party.add_money(self.enemys.get_money())
            global game
            if self.enemys.event is None:
                game = game_stack.pop()
            else:
                game = Event(self.enemys.event)
    def magic(self):
        pass
    def defense(self):
        party.do_defense()
        update_buffer.append( u"%s は 防御した" % (party.get_name()) )
    pass

class BattleEscape():
    def __init__(self, enemys, depth):
        self.enemys = enemys
        self.depth = depth
    def draw(self):
        head = " " * self.depth * 2
        draw_buffer.append( head + "--------" )
    def sub_battle_update(self):
        battle_end = party.escape()
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
            global is_loop
            is_loop = False

#------------------------------------------------------------------------------
# Character
class CharacterBase:
    def __init__ (self):
        pass

class Group:
    def __init__ (self, *characters):
        self.group = []
        for e in characters:
            self.group.append(e)
    def append(self, e):
        self.group.append(e)
    def show(self):
        for e in self.group:
            if e.is_living():
                e.show()
            else:
                draw_buffer.append("")
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
        return lives

class GroupEnemy(Group):
    def __init__ (self, *enemys):
        Group.__init__(self, *enemys)
        #
        self.event = None
    def do_attack(self):
        for e in self.group:
            if e.is_living():
                update_buffer.append( u"%s の攻撃" % (e.name) )
                select = party.rand_select()
                damage = calc_damage_def(e, party.group[select])
                update_buffer.append( u"%s に %3d" % (party.get_name(), damage) )
                party.group[select].receive_damage(damage)
    def receive(self):
        for player in party.group:
            llist = self.livinglist()
            r = sum(llist) - 1
            e = self.group[r]
            update_buffer.append( u"%s の攻撃" % (player.name) )
            damage = calc_damage_atk(player, e)
            update_buffer.append( u"%s に %3d" % (e.name, damage) )
            e.receive_damage(damage)
            if not self.is_living():
                return
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

class Party(Group):
    def __init__ (self, *players):
        Group.__init__(self, *players)
        #
        self.money = 0
        self.select = 0
    def show(self, depth):
        head = " " * depth * 2
        if game.game_state[0] == GameBase.MENU:
            if game.game_state[1] == Menu.STATUS:
                draw_buffer.append( head + u"お金 %5d" % ( self.money) )
        for e in self.group:
            if e.is_living():
                e.show(depth)
            else:
                e.show_death(depth)
    def battle_update(self):
        for e in self.group:
            e.battle_update()
    def change_item(self, select_type, select_num):
        return self.group[self.select].change_item(select_type, select_num)
    def add_money(self, money):
        st = u"お金 +%3d" % (money)
        update_buffer.append(st)
        self.money += money
    def add_exp(self, exp):
        ex = exp / len(self.group)
        for e in self.group:
            e.add_exp(ex)
    def get_name(self):
        return self.group[self.select].name
    def rand_select(self):
        return 0
    def do_defense(self):
        self.group[self.select].is_defense = True
    def get_escape_value(self):
        s = 0
        for e in self.group:
            s += e.escape_value
        s /= len(self.group)
        return s
    def escape(self):
        if random.random() <= self.get_escape_value():
            global game
            game = game_stack.pop()
            update_buffer.append(u"逃げ出した")
            return True
        else:
            update_buffer.append(u"逃げるのに失敗した")
            return False
    def add_item(self, item):
        self.group[self.select].add_item(item)
    def recover(self):
        for e in self.group:
            e.recover()
#     def receive_damage(self, damage):
#         self.hp  -= damage
#         if self.is_living():
#             st = u"%s たちは 倒れた" % (self.group[0].name)
#             update_buffer.append(st)
#             global game
#             global game_stack
#             del game_stack[:]
#             game = Title()
#             self.recover()

#-------
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
        st = "%s" % ( self.name)
        p = self.hp * 5 / self.max_hp
        st += "*" * int(p)
        draw_buffer.append( st )
    def receive_damage(self, damage):
        self.hp -= damage

class Player(Character):
    def __init__ (self, name, hp, attack, defense, inc_hp, inc_attack, inc_defense, inc_exp):
        Character.__init__(self, name, hp, attack, defense)
        self.inc_attack = inc_attack
        self.inc_defense = inc_defense
        self.inc_exp = inc_exp
        self.exp = 0
        self.lv = 1
        self.next_exp = self.lv * self.inc_exp
        self.inc_hp = inc_hp
        self.wepon = [Wepon(u"なし",0, 0)]
        self.armor = [Armor(u"なし",0, 0)]
        self.escape_value = 0.5
        #
        self.is_defense = False
    def show_death(self, depth):
        draw_buffer.append( head +  u"%s Death" % ( self.name ) )
    def show(self, depth):
        head = " " * depth * 2
        if game.game_state[0] == GameBase.MENU:
            if game.game_state[1] == Menu.STATUS:
                draw_buffer.append( head + u"%s Lv:%3d HP %3d/%3d ATK %3d DEF %3d" % ( self.name, self.lv,  self.hp, self.max_hp, self.attack, self.defense) )
                draw_buffer.append( head + u"        %s %+3d %s %+3d" % (self.wepon[0].name, self.wepon[0].value, self.armor[0].name, self.armor[0].value) )
                draw_buffer.append( head + u"        Exp %3d 次のレベルまで あと %-3d" % ( self.exp, (self.next_exp - self.exp)) )
        if game.game_state[0] == GameBase.BATTLE:
            draw_buffer.append( head +  u"%s %3d/%3d" % ( self.name, self.hp, self.max_hp) )
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
        st = item.name + u"を手に入れた"
        update_buffer.append(st)
    def change_item(self, select_type, select_num):
        if select_num != 0:
            if select_type == SMenuEquipment.WEAPON:
                self.wepon[0], self.wepon[select_num] = self.wepon[select_num], self.wepon[0]
                st = self.wepon[0].name  + u"を装備した"
                update_buffer.append(st)
            elif select_type == SMenuEquipment.Armor:
                self.armor[0], self.armor[select_num] = self.armor[select_num], self.armor[0]
                st = self.armor[0].name + u"を装備した"
                update_buffer.append(st)
            return True
        return False
    def add_exp(self, exp):
        st =  u"EXP +%3d" % (exp)
        update_buffer.append(st)
        self.exp += exp
        while self.exp >= self.next_exp:
            # Lv Up
            self.lv += 1
            add_next_exp = self.lv * self.inc_exp
            self.next_exp += add_next_exp
            self.max_hp  += self.inc_hp
            self.attack  += self.inc_attack
            self.defense += self.inc_defense
            st = u"%s は レベル が上がった +MAX_HP %2d +ATK %2d +DEF %3d" % ( self.name, self.inc_hp, self.inc_attack, self.inc_defense)
            update_buffer.append(st)
    def receive_damage(self, damage):
        self.hp  -= damage
        if self.hp <= 0:
            st = u"%s は 倒れた" % (self.name)
            update_buffer.append(st)
            global game
            global game_stack
            del game_stack[:]
            game = Title()
            self.recover()
    def recover(self):
        self.hp = self.max_hp
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
# Data
class CreateTownAction():
    TALK, SLEEP, SLEEP2, MENU, BACK, NEXT, FIGHT = range(7)
    selects_dict = { TALK:u"話す", SLEEP:u"泊まる", SLEEP2:u"回復ポイント", MENU:u"メニューを開く", BACK:u"戻る", NEXT:u"出発する", FIGHT:u"戦う" }
    def action(select, event_state = -1, field_state_back = -1, field_state_next = -1 ):
        global game
        if   select == TALK:
            if event_state != -1:
                game_stack.append(game)
                game = Event(event_state)
        elif select == SLEEP or select == SLEEP2:
            party.recover()
            update_buffer.append(u"全回復した")
        elif select == MENU:
            game_stack.append(game)
            game = Menu()
        elif select == BACK:
            if field_state_back != -1:
                game = Field(field_state_back, True)
        elif select == NEXT:
            if field_state_next != -1:
                game = Field(field_state_next)
        elif select == FIGHT:
            if event_state != -1:
                game = Event(event_state)

def kingdom_action(select):
    SLEEP, MENU, NEXT = range(3)
    global game
    if select == SLEEP:
        party.recover()
        update_buffer.append(u"全回復した")
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
        party.recover()
        update_buffer.append(u"全回復した")
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
        party.recover()
        update_buffer.append(u"全回復した")
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
    TALK, SLEEP, SLEEP2, MENU, BACK, NEXT, FIGHT = range(7)
    selects_dict = { TALK:u"話す", SLEEP:u"泊まる", SLEEP2:u"回復ポイント", MENU:u"メニューを開く", BACK:u"戻る", NEXT:u"出発する", FIGHT:u"戦う" }
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
            update_buffer.append( u"敵が現れた" )
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

def create_player():
    player = Player(u"勇者", 100, 10, 10, 10, 4, 2, 10)
    return player

#------------------------------------------------------------------------------
# Game System

class PyRPG:
    def __init__(self):
        global game
        game = Title()
        self.os_system = GameInput()
        # メインループを起動
        self.main_loop()
    def main_loop(self):
        """メインループ"""
        try:
            while is_loop:
                # 画面クリア，描画，キー入力，イベント処理，イベント処理キー入力
                self.os_system.clear()
                self.draw()
                self.check_event()
                self.os_system.clear()
                self.draw()
                self.update()
                global game_turn
                game_turn += 1
                if debug_print:
                    st = "------------- %s %3d" % (GameBase.STATE_NAME[game.game_state[0]], game_turn)
                    self.os_system.print_buffer([st])
        except:
            self.os_system.finish()
            traceback.print_exc()
        else:
            st = "GAME END"
            self.os_system.print_buffer([st])
    def draw(self):
        game.draw()
        global draw_buffer
        if len(draw_buffer) != 0:
            self.os_system.print_buffer(draw_buffer)
            draw_buffer = []
    def update(self):
        """ゲーム状態の更新
            描画があったら is_draw を True
        """
        game.update()
        global update_buffer
        if len(update_buffer) != 0:
            self.os_system.print_buffer(update_buffer)
            update_buffer = []
            self.os_system.wait()
    def check_event(self):
        key = self.os_system.get_key()
        if key == FINISH:
            global is_loop
            is_loop = False
        elif key != -1:
            game.changed(key)


#--------------------------------------
# game の更新は update
game = None
game_stack = []
game_turn = 0
is_loop = True
party = None

draw_buffer = []
update_buffer = []

# debug_print = False
debug_print = True

random.seed(1)
if __name__ == "__main__":
    PyRPG()

#------------------------------------------------------------------------------
