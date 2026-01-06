import pygame as pg
import random

_ = False

class Map:
    def __init__(self, game):
        self.game = game
        self.rows = 30
        self.cols = 30
        self.world_map = {}
        self.mini_map = []
        self.player_spawn_pos = (1.5, 1.5)
        self.exit_pos = (1, 1)
        self.generate_map()

    def generate_map(self):
        # Initialize full walls
        self.mini_map = [[1] * self.cols for _ in range(self.rows)]
        
        # Random walker setup
        # Start in the middle
        cx, cy = self.cols // 2, self.rows // 2
        self.mini_map[cy][cx] = _ # Start is empty
        
        floor_tiles = {(cx, cy)}
        walkers = [(cx, cy)]
        max_floors = int(self.rows * self.cols * 0.4) # Target 40% empty space
        
        iterations = 0
        while len(floor_tiles) < max_floors and iterations < 5000:
            iterations += 1
            # Pick a random walker
            wx, wy = random.choice(walkers)
            
            # Move random direction
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            nx, ny = wx + dx, wy + dy
            
            # Check bounds (leave 1 tile border)
            if 1 < nx < self.cols - 2 and 1 < ny < self.rows - 2:
                if self.mini_map[ny][nx] == 1:
                    self.mini_map[ny][nx] = _
                    floor_tiles.add((nx, ny))
                    walkers.append((nx, ny))
                    # Occasionally remove old walkers to keep it growing outward
                    if len(walkers) > 10 and random.random() < 0.2:
                       walkers.pop(0) 
                else:
                    # If already floor, change walker pos
                    pass

        # Populate world_map
        self.world_map = {}
        floor_list = list(floor_tiles)
        
        if not floor_list: # Fallback shouldn't happen but safety
             floor_list = [(cx, cy)]
        
        # Set player spawn at the first floor tile generated (usually center)
        # or just pick a random one
        self.player_spawn_pos = (cx + 0.5, cy + 0.5)
        
        # Find exit position - furthest from player would be nice, but random is okay for now
        # Let's pick a random floor tile that is far from center
        possible_exits = [pos for pos in floor_list if ((pos[0]-cx)**2 + (pos[1]-cy)**2) > 50]
        if not possible_exits:
            possible_exits = floor_list
        exit_tile = random.choice(possible_exits)
        self.exit_pos = exit_tile
        
        # Generate walls dict
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i, j)] = value

    def draw(self):
        [pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 100, pos[1] * 100, 100, 100), 2)
         for pos in self.world_map]
