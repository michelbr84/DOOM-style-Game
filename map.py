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
        
        rooms = []
        max_rooms = 10
        room_min_size = 3
        room_max_size = 8
        
        for _ in range(30): # Attempt 30 times to place rooms
            w = random.randint(room_min_size, room_max_size)
            h = random.randint(room_min_size, room_max_size)
            x = random.randint(1, self.cols - w - 1)
            y = random.randint(1, self.rows - h - 1)
            
            new_room = pg.Rect(x, y, w, h)
            
            failed = False
            for other_room in rooms:
                if new_room.colliderect(other_room.inflate(2, 2)): # Pad to avoid touching rooms
                    failed = True
                    break
            
            if not failed:
                # Carve room
                for i in range(new_room.x, new_room.x + new_room.w):
                    for j in range(new_room.y, new_room.y + new_room.h):
                        if 0 < i < self.cols and 0 < j < self.rows:
                             self.mini_map[j][i] = _
                
                # Connect to previous room (if any)
                if rooms:
                    prev_room = rooms[-1]
                    new_center = new_room.center
                    prev_center = prev_room.center
                    
                    # Horizontal tunnel
                    x1, x2 = min(prev_center[0], new_center[0]), max(prev_center[0], new_center[0])
                    for i in range(x1, x2 + 1):
                        self.mini_map[prev_center[1]][i] = _
                        
                    # Vertical tunnel
                    y1, y2 = min(prev_center[1], new_center[1]), max(prev_center[1], new_center[1])
                    for j in range(y1, y2 + 1):
                        self.mini_map[j][new_center[0]] = _
                        
                rooms.append(new_room)
                if len(rooms) >= max_rooms:
                    break
                    
        # Populate world_map
        self.world_map = {}
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i, j)] = value
                    
        if rooms:
            # Player in first room center
            self.player_spawn_pos = (rooms[0].centerx + 0.5, rooms[0].centery + 0.5)
            # Exit in last room center
            self.exit_pos = (rooms[-1].centerx, rooms[-1].centery)
        else:
             # Fallback if generation fails completely (unlikely)
             self.player_spawn_pos = (1.5, 1.5)
             self.exit_pos = (2.5, 2.5)

    def draw(self):
        [pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 100, pos[1] * 100, 100, 100), 2)
         for pos in self.world_map]
