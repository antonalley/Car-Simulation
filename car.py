import random

UP = (0, -1)
DOWN = (0,1)
RIGHT = (1, 0)
LEFT = (-1, 0)

class Car:
    def __init__(self, pos):
        self.pos = pos
        self.prev_pos = pos

    def next_pos(self, world, current, dir):
        p = (current[0] + dir[0], current[1] + dir[1])
        if p[0] < 0 or p[1] < 0 or p[0] > len(world) - 1 or p[1] > len(world[0]) - 1:
            return None
        return p
    
    def next_spot(self, world, current, dir):
        try:
            p = self.next_pos(world, current, dir)
            if p is None: return None
            spot = world[p[0]][p[1]]
        except IndexError:
            return None
        
        return spot

    def move(self, world):
        """
        
        """
        possible_moves = []

        # Check which direction you can go if you are in a lane, else if you are in an intersection randomly choose
        if self.next_spot(world, self.pos, UP) == 0:
            possible_moves.append(LEFT)
        elif self.next_spot(world, self.pos, DOWN) == 0:
            possible_moves.append(RIGHT)
        elif self.next_spot(world, self.pos, RIGHT) == 0:
            possible_moves.append(UP)
        elif self.next_spot(world, self.pos, LEFT) == 0:
            possible_moves.append(DOWN)
        else:
            # Check in the intersection what directions it can go
            # if self.next_spot(world, self.pos, (-1,-1)) == 0:
            #     possible_moves = [DOWN, RIGHT]
            # elif self.next_spot(world, self.pos, (-1, 1)) == 0:
            #     possible_moves = [DOWN, RIGHT]
            # elif self.next_spot(world, self.pos, (1,1)) == 0:
            #     possible_moves = [RIGHT, UP]
            # elif self.next_spot(world, self.pos, (1, -1)) == 0:
            #     possible_moves = [LEFT, UP]
            # else:
            possible_moves = [UP, DOWN, LEFT, RIGHT]
        
        
        done = False
        self.prev_pos = self.pos
        while not done:
            m = random.choice(possible_moves)
            p = self.next_pos(world, self.pos, m)
            if p is not None:
                self.pos = p
                done = True


        return m