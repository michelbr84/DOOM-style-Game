import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *


import random

class Menu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pg.font.SysFont('arial', 40)
        self.text_input = ''
        
    def draw(self):
        self.screen.fill('black')
        title_surf = self.font.render('ENTER SEED', True, 'white')
        input_surf = self.font.render(self.text_input + '_', True, 'yellow')
        self.screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 2 - 100))
        self.screen.blit(input_surf, (WIDTH // 2 - input_surf.get_width() // 2, HEIGHT // 2))
        pg.display.flip()
        
    def run(self):
        input_active = True
        while input_active:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        input_active = False
                    elif event.key == pg.K_BACKSPACE:
                        self.text_input = self.text_input[:-1]
                    else:
                        if len(self.text_input) < 10:
                            self.text_input += event.unicode
            self.draw()
        return self.text_input

class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(True)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        
        # Show Menu first
        self.menu = Menu(self)
        pg.mouse.set_visible(True) # Show mouse for menu if needed (not strictly needed but good practice)
        pg.event.set_grab(False)
        seed_val = self.menu.run()
        
        # Determine seed
        if not seed_val:
            seed_val = random.randint(0, 10000) # Default random if empty
        
        try:
             # Try to interpret as int for consistency, else string
             seed_val = int(seed_val)
        except ValueError:
             pass # Keep as string
             
        random.seed(seed_val)
        print(f"Game starting with seed: {seed_val}")
        
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        self.new_game()

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        # self.screen.fill('black')
        self.object_renderer.draw()
        self.weapon.draw()
        # self.map.draw()
        # self.player.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()
