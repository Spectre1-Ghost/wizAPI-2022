from wizAPI import *
#from Job import *
import time
import math
import _thread
import os
from pynput import keyboard

"""set main thread as a job"""
#MAIN_THREAD = Job(threading.main_thread())
""" Implement Escape Key"""
def escape_keybind(key):
    if key == keyboard.Key.esc or (hasattr(key, 'char') and key.char == ('c')):
        print('Pressed Escape Button')
        #MAIN_THREAD.stop()
        _thread.interrupt_main()
        time.sleep(1)
        print('interrupt_main failed, os._exit()')
        os._exit(0)
        return False

keyboard.Listener(on_press=escape_keybind).start()  # start to listen on a separate thread
""" Register windows """
try:
    player = wizAPI().register_window()
except IndexError:
    print('You need wizard101 open to run this particular bot. no accounts detected')
    exit()

def print_separator(*args):
    sides = '+'*16
    _str = " ".join([sides, " ".join(args), sides])
    l = len(_str)
    print('='*l)
    print(_str)
    print('='*l)


def print_time(timer,topic):
    minutes = math.floor(timer/60)
    seconds = math.floor(timer % 60)
    print(topic + ' lasted {} minutes and {} seconds.'.format(minutes, seconds))

def team_up():
    """ Open Team Up Page """
    if player.enter_dungeon_dialog():
        player.press_key('x')
    else:
        print('missing kiosk X?')
    """Find Dragonspire world in team up kiosk check"""
    while (not player.teamup_has_world('dragonspire')):
        player.click(562, 177)
    print('Found Dragonspire')
    """ Click on dragonspire, lorechamber"""
    player.click(512, 174)
    PTRYCOUNT = 1
    while not player.tu_lore('lorechamber', p_try_count=PTRYCOUNT):
        player.click(512, 174)
        PTRYCOUNT += 1
        time.sleep(1)

ROUND_COUNT = 0

while True:
    START_TIME = time.time()
    ROUND_COUNT += 1
    print_separator('ROUND', str(ROUND_COUNT))

    """ Attempt to enter the dungeon """
    #time.sleep(1)
    """ player.hold_key('s', .8).wait(1) """

    #player.move_mouse(238, 398, speed=.5)
    #player.print_color_image((354, 342, 79, 23))
    
    #wx, wy = player.get_window_rect()[1::-1] #GetClientRect
    #player.print_color_image((211, 360, 79, 23))
    #print(player.is_health_low(),player.is_health_medium(),player.is_health_high())
    #player.find_spell('feint')
    #exit()

    """ Check Mana and use potion if necessary """
    player.use_potion_if_needed(checkhealth = False)
    """ Check Health and Wait if necessary """
    HEALING_TIMER = time.time()
    if not player.is_health_medium():
        print('Started Healing')
        while not player.is_health_medium():
            if player.is_active():
                player.hold_key('d', 1.5).hold_key('a', 2).wait(1.5)
            player.set_active()
    print_time((time.time() - HEALING_TIMER),'Healing')

    TU_SUCCESS = False

    while (TU_SUCCESS == False):
        team_up()
        TU_SUCCESS = True
        while not player.is_DS_loading():
            time.sleep(.2)
            if player.join_a_team_error():
                while player.join_a_team_error():
                    time.sleep(.1)
                    player.press_key('enter')
                if not player.join_a_team_error():
                    TU_SUCCESS = False
                    break
            if player.team_canceled_error():
                while player.team_canceled_error():
                    time.sleep(.1)
                    player.click(514, 410)
                if not player.team_canceled_error():
                    TU_SUCCESS = False
                    break

    while not player.is_idle():
        time.sleep(.2)
    
    """ Run into battle """
    player.hold_key('w', 3)

    player.wait_for_next_turn()

    boss_pos = False
    find_boss_tries = 0
    while not boss_pos and (not (find_boss_tries >= 5)):
        find_boss_tries += 1
        boss_pos = player.get_enemy_pos('balance')
        time.sleep(.2)
    del find_boss_tries
    print('Boss at pos', boss_pos)

    # death_pos = player.get_ally_pos('death')
    # print('death player at pos', death_pos)

    inFight = True
    battle_round = 0

    while inFight:
        battle_round += 1
        print('-------- Battle round', battle_round, '--------')

        """ Feinter plays """
        # Check to see if deck is crowded with unusable spells
        cn = len(player.find_unusable_spells())
        if cn > 2:
            player.discard_unusable_spells(cn)

        # Play
        """if shadowbar?"""
        """ Life """
        # try:
        #     if (not player.is_health_low() and player.find_spell('satyr', threshold=0.06, max_tries=2)):
        #         player.cast_spell('satyr').at_ally('life')
        #     elif player.find_spell('gear-bladestorm', threshold=0.06, max_tries=2):
        #         player.cast_spell('gear-bladestorm')
        #     elif player.get_enemy_pos('balance') and player.find_spell('feint', threshold=0.06, max_tries=2):
        #         player.cast_spell('feint').at_target(boss_pos)
        #     elif player.get_ally_pos('storm') and player.find_spell('gear-windstorm', threshold=0.06, max_tries=2):
        #         player.cast_spell('gear-windstorm')
        #     elif player.find_spell('life-gear-blade', threshold=0.06, max_tries=2):
        #         player.cast_spell('life-gear-blade').at_ally(player.get_ally_pos('life'))
        #     elif (player.get_ally_pos('life') or player.get_ally_pos('death') or player.get_ally_pos('myth')) and player.find_spell('spirit-blade', threshold=0.06, max_tries=2):
        #         target_ally_pos = player.get_ally_pos('life') or player.get_ally_pos('death') or player.get_ally_pos('myth')
        #         player.cast_spell('spirit-blade').at_ally(target_ally_pos)
        #     elif player.find_spell('leafstorm', threshold=0.06, max_tries=2):
        #         player.cast_spell('leafstorm')
        #     else:
        #         player.pass_turn()
        # except:
        #     print('Error occured while casting spell')
        #     player.pass_turn()

        """ STORM """
        try:
            if (player.find_spell('glowbug-squall', threshold=0.04, max_tries=2) and player.enchant('glowbug-squall', 'epic')):
                player.find_spell('enchanted-glowbug-squall', max_tries=4)
                player.cast_spell('enchanted-glowbug-squall')
            elif (battle_round == 2) and player.get_enemy_pos('balance') and (player.find_spell('lightning-bats', threshold=0.08, max_tries=3) and player.enchant('lightning-bats', 'epic')):
                player.find_spell('enchanted-lightning-bats', max_tries=4)
                player.cast_spell('enchanted-lightning-bats').at_target(boss_pos)
            elif (player.find_spell('tempest', threshold=0.08, max_tries=3) and player.enchant('tempest', 'epic')):
                player.find_spell('enchanted-tempest', max_tries=4)
                player.cast_spell('enchanted-tempest')
            else:
                player.pass_turn()
        except:
            print('Error occured while casting spell')
            player.pass_turn()

        """ DEATH """
        # try:
        #     if (player.find_spell('scarecrow', threshold=0.08, max_tries=3) and player.enchant('scarecrow', 'gargantuan')):
        #         print('sc')
        #         player.find_spell('enchanted-scarecrow', max_tries=4)
        #         player.cast_spell('enchanted-scarecrow')
        #     elif player.find_spell('mass-feint', threshold=0.08, max_tries=3):
        #         print('mf')
        #         player.cast_spell('mass-feint')
        #     elif player.get_enemy_pos('balance') and (not player.is_health_low() and player.find_spell('vampire', threshold=0.08, max_tries=3) and player.enchant('vampire', 'gargantuan', threshold=0.08)):
        #         print('low hp, emergency vampire')
        #         player.find_spell('enchanted-vampire', max_tries=4)
        #         player.cast_spell('enchanted-vampire').at_target(boss_pos)
        #     elif death_pos and (player.find_spell('death-blade', threshold=0.08, max_tries=3) and player.enchant('death-blade', 'pet-sharpen', threshold=0.08)):
        #         print('psdb')
        #         player.find_spell('sharpened-death-blade', max_tries=4)
        #         player.cast_spell('sharpened-death-blade').at_ally(death_pos)
        #     elif death_pos and player.find_spell('death-gear-blade', threshold=0.1, max_tries=3):
        #         print('dgb')
        #         player.cast_spell('death-gear-blade').at_ally(death_pos)
        #     #elif player.find_spell('scarecrow', threshold=0.08):
        #         #print('scare')
        #         #player.cast_spell('scarecrow')
        #     else:
        #         player.pass_turn()
        # except:
        #     print('Error occured while casting spell')
        #     player.pass_turn()

        player.wait_for_end_of_round()
        if player.is_idle():
            inFight = False
    print("Battle has ended")

    print("Exiting...")
    time.sleep(1)
    player.to_commons()
    #player.wait(2).face_arrow().hold_key('w', 3).wait(1)

    while not player.is_DS_loading():
        time.sleep(.2)

    while not player.is_idle():
        time.sleep(.2)

    print('Successfully exited the dungeon')
    print_time((time.time() - START_TIME), 'Round')
