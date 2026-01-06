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


from pathfinding import *
from score import ScoreManager
import random

class Menu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pg.font.SysFont('arial', 40)
        self.username = ''
        self.seed = ''
        self.active_field = 0 # 0: Username, 1: Seed
        
    def draw(self):
        self.screen.fill('black')
        
        # Labels
        u_label = self.font.render('USERNAME:', True, 'white')
        s_label = self.font.render('SEED:', True, 'white')
        start_label = self.font.render('PRESS ENTER TO START', True, 'green')
        
        # Inputs
        u_color = 'yellow' if self.active_field == 0 else 'gray'
        s_color = 'yellow' if self.active_field == 1 else 'gray'
        
        u_input = self.font.render(self.username + ('_' if self.active_field == 0 else ''), True, u_color)
        s_input = self.font.render(self.seed + ('_' if self.active_field == 1 else ''), True, s_color)
        
        # Stats display if user exists
        stats = self.game.score_manager.get_score(self.username)
        stats_text = self.font.render(f"Wins: {stats['wins']} | Losses: {stats['losses']}", True, 'white')
        
        cx, cy = WIDTH // 2, HEIGHT // 2
        
        self.screen.blit(u_label, (cx - u_label.get_width() // 2, cy - 150))
        self.screen.blit(u_input, (cx - u_input.get_width() // 2, cy - 100))
        
        self.screen.blit(s_label, (cx - s_label.get_width() // 2, cy - 20))
        self.screen.blit(s_input, (cx - s_input.get_width() // 2, cy + 30))
        
        self.screen.blit(stats_text, (cx - stats_text.get_width() // 2, cy + 100))
        self.screen.blit(start_label, (cx - start_label.get_width() // 2, cy + 200))

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
                        # If on seed, start game. If on username, move to seed.
                        if self.active_field == 0:
                            if self.username: # Force username
                                self.active_field = 1
                        else:
                            input_active = False
                    elif event.key == pg.K_TAB:
                        self.active_field = (self.active_field + 1) % 2
                    elif event.key == pg.K_BACKSPACE:
                        if self.active_field == 0:
                            self.username = self.username[:-1]
                        else:
                            self.seed = self.seed[:-1]
                    else:
                        if self.active_field == 0:
                             if len(self.username) < 15:
                                self.username += event.unicode
                        else:
                             if len(self.seed) < 10:
                                self.seed += event.unicode
            self.draw()
        return self.username, self.seed

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
        self.score_manager = ScoreManager()
        self.username = "Player"
        
        self.paused = False
        self.show_stats = False
        
        self.run_menu_and_game()

    def run_menu_and_game(self):
        while True:
            # Show Menu
            self.menu = Menu(self)
            pg.mouse.set_visible(True)
            pg.event.set_grab(False)
            self.username, seed_val = self.menu.run()
            
            # Use default seed if empty
            if not seed_val:
                seed_val = str(random.randint(0, 10000))
            
            try:
                 # Standardize seed to string for hashing/consistency, or int if intended
                 # Original code used int(seed_val)
                 seed_int = int(seed_val)
            except ValueError:
                 # If string, simple hash to int for random.seed
                 import zlib
                 seed_int = zlib.adler32(seed_val.encode())
                 
            random.seed(seed_int)
            self.seed_val = seed_int
            print(f"Game starting. User: {self.username}, Seed: {seed_int}")
            
            # Start Game Loop
            pg.mouse.set_visible(False)
            pg.event.set_grab(True)
            
            self.new_game()
            self.run() # This runs the game loop. If it returns, we loop back to menu.

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
        
    def draw_stats(self):
        font = pg.font.SysFont('arial', 20)
        fps_text = font.render(f"FPS: {int(self.clock.get_fps())}", True, 'green')
        seed_text = font.render(f"SEED: {self.seed_val}", True, 'green')
        name_text = font.render(f"USER: {self.username}", True, 'green')
        
        self.screen.blit(fps_text, (10, 10))
        self.screen.blit(seed_text, (10, 30))
        self.screen.blit(name_text, (10, 50))

    def update(self):
        if not self.paused:
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
        
        if self.show_stats:
            self.draw_stats()
            
        if self.paused:
            self.draw_pause()

    def draw_pause(self):
        # Simple pause overlay
        surf = pg.Surface(RES)
        surf.set_alpha(150)
        surf.fill((0, 0, 0))
        self.screen.blit(surf, (0, 0))
        font = pg.font.SysFont('arial', 50)
        text = font.render('PAUSED (Press P to Resume)', True, 'white')
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

    def run(self):
        while True:
            res = self.check_events()
            if res == "restart":
                break
            self.update()
            self.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    # Logic for In-Game Menu (ESC)
                    # For now, return "restart" as per old logic? 
                    # No, user wants a menu with options: Resume, Exit, Stats, Change Config.
                    # This implies calling a sub-menu loop here.
                    action = self.run_in_game_menu()
                    if action == "restart":
                        return "restart"
                    elif action == "quit":
                        pg.quit()
                        sys.exit()
                elif event.key == pg.K_p:
                    self.paused = not self.paused
                elif event.key == pg.K_t:
                    self.show_stats = not self.show_stats
                    
            elif event.type == self.global_event and not self.paused:
                self.global_trigger = True
            
            if not self.paused:
                self.player.single_fire_event(event)

    def run_in_game_menu(self):
        # Small menu loop
        self.paused = True
        menu_active = True
        font = pg.font.SysFont('arial', 40)
        options = ["RESUME", "TOGGLE STATS", "CHANGE CONFIG", "EXIT GAME"]
        selected = 0
        
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        
        while menu_active:
            self.screen.fill('black')
            
            title = font.render("PAUSE MENU", True, 'red')
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            mx, my = pg.mouse.get_pos()
            
            for i, opt in enumerate(options):
                color = 'yellow' if i == selected else 'white'
                text = font.render(opt, True, color)
                rect = text.get_rect(center=(WIDTH//2, 250 + i * 60))
                
                # Mouse hover
                if rect.collidepoint(mx, my):
                    selected = i
                    color = 'yellow'
                    text = font.render(opt, True, color)
                
                self.screen.blit(text, rect)
            
            pg.display.flip()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return "quit"
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        menu_active = False # Resume
                    elif event.key == pg.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pg.K_RETURN:
                        # Handle selection
                        if selected == 0: # Resume
                            menu_active = False
                        elif selected == 1: # Stats
                            self.show_stats = not self.show_stats
                        elif selected == 2: # Change Config
                            # Confirmation
                            return "restart"
                        elif selected == 3: # Exit
                            return "quit"
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    # Click handling
                    if selected == 0: menu_active = False
                    elif selected == 1: self.show_stats = not self.show_stats
                    elif selected == 2: return "restart"
                    elif selected == 3: return "quit"
                    
        self.paused = False
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        return "resume"


if __name__ == '__main__':
    game = Game()
    game.run()
