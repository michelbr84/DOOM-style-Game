from sprite_object import *
from npc import *
from random import choices, randrange


class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        add_sprite = self.add_sprite
        add_npc = self.add_npc
        self.npc_positions = {}

        # spawn npc
        self.enemies = 1  # npc count
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.weights = [70, 20, 10]
        self.spawn_npc()

        # spawn exit door visual
        # Using existing candelbra as placeholder or similar if available, or just a specific static sprite
        # For now, let's use a green light or something similar to mark the exit if available
        # logic: self.add_sprite(AnimatedSprite(game, path=... + 'green_light/0.png', pos=self.game.map.exit_pos))
        # But we don't have green_light confirmed. Let's use 'candlebra.png' if it exists in static, or just a distinct sprite.
        # User moved files in previous tasks maybe? I saw 'candlebra.png' in root of 'static_sprites' during list_dir.
        # Wait, the list_dir showed 'candlebra.png' in the root of the search? 
        # No, list_dir g:\Jogos\DOOM-style-Game\resources\sprites\static_sprites result was:
        # {"name":"candlebra.png", "sizeBytes":"248388"}
        # So it is there.
        self.add_sprite(SpriteObject(game, path='resources/sprites/static_sprites/candlebra.png', pos=self.game.map.exit_pos))


        # sprite map
        add_sprite(AnimatedSprite(game))
        add_sprite(AnimatedSprite(game, pos=(1.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 7.5)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 3.25)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 4.75)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 2.5)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 5.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 4.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 5.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(12.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 12.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 20.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(10.5, 20.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 14.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 18.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 24.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 24.5)))

        # npc map
        # add_npc(SoldierNPC(game, pos=(11.0, 19.0)))
        # add_npc(SoldierNPC(game, pos=(11.5, 4.5)))
        # add_npc(SoldierNPC(game, pos=(13.5, 6.5)))
        # add_npc(SoldierNPC(game, pos=(2.0, 20.0)))
        # add_npc(SoldierNPC(game, pos=(4.0, 29.0)))
        # add_npc(CacoDemonNPC(game, pos=(5.5, 14.5)))
        # add_npc(CacoDemonNPC(game, pos=(5.5, 16.5)))
        # add_npc(CyberDemonNPC(game, pos=(14.5, 25.5)))

    def spawn_npc(self):
        for i in range(self.enemies):
                npc = choices(self.npc_types, self.weights)[0]
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                # Check valid position (not in wall, not on player, not too close)
                while (pos in self.game.map.world_map) or (pos == self.game.map.player_spawn_pos):
                    pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))

    def check_win(self):
        # Check distance to exit
        px, py = self.game.player.map_pos
        ex, ey = self.game.map.exit_pos
        if int(px) == int(ex) and int(py) == int(ey):
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_win()
        self.check_enemy_spawn()

    def check_enemy_spawn(self):
        # Timer logic could be frame-based or time-based. Let's use simple frame counter or just low prob
        # Or better, use pg.time.get_ticks()
        # Initialize timer if not exists
        if not hasattr(self, 'last_spawn_time'):
            self.last_spawn_time = pg.time.get_ticks()
            self.spawn_interval = 5000 # 5 seconds
            
        now = pg.time.get_ticks()
        if now - self.last_spawn_time > self.spawn_interval:
            self.last_spawn_time = now
            if len([n for n in self.npc_list if n.alive]) < 30: # Max enemies
                self.spawn_single_enemy()

    def spawn_single_enemy(self):
        npc_class = choices(self.npc_types, self.weights)[0]
        # Attempt to find valid spot
        for _ in range(10): 
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            # Check valid: not wall, not player pos
            if (pos not in self.game.map.world_map) and (pos != self.game.map.player_spawn_pos):
                # Also check distance from player so it doesn't spawn on top
                px, py = self.game.player.map_pos
                if (x-px)**2 + (y-py)**2 > 25: # At least 5 units away behaviorally
                    self.add_npc(npc_class(self.game, pos=(x + 0.5, y + 0.5)))
                    break

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)