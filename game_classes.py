import random, copy

class Gamestate:
    def __init__(self, seed):
        self.grid = [[0 for i in range(10)] for x in range(20)]
        self.lines = 0
        self.garbage = 0
        self.lives = 3
        self.garbage_queue = []
        self.line_queue = []
        self.garbage_id = 1
        self.combo = 0
        self.convert = {
            0: "i",
            1: "o",
            2: "t",
            3: "j",
            4: "l",
            5: "s",
            6: "z"
        }
        self.grid_number = {
            "light blue": 1,
            "yellow": 2,
            "pink": 3,
            "dark blue": 4,
            "orange": 5,
            "green": 6,
            "red": 7,
            "garbage": 8
        }
        self.c_table = {
            0: {1: 0, 2: 1, 3: 2, 4: 4},
            1: {1: 1, 2: 2, 3: 3, 4: 5},
            2: {1: 2, 2: 4, 3: 6, 4: 10},
            3: {1: 3, 2: 6, 3: 9, 4: 15}
        }
        random.seed(seed)
        print("\n" + str(seed) + "\n")
        self.active = Tetrimino(kind=self.generate_tetrimino())
        self.held = False
        self.hold_limit = False
        self.tetrimino_queue = []
        for k in range(5):
            q = Tetrimino(kind=self.generate_tetrimino())
            self.tetrimino_queue.append(q)

    def next_rand(self):
        next = random.randint(0,6)
        print(str(next))
        return next

    def generate_tetrimino(self): #Generate a random tetrimino and return it (random gen is seeded on init)
        return self.convert[self.next_rand()]
    def check_collision(self, coord):
        x = coord[0]
        y = coord[1]
        if (y < 0):
            return False
        if (self.grid[y][x] != 0):
            return True
        else:
            return False
    def clear_lines(self, lines):
        blank_line = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for y in lines:
            del self.grid[y]
            self.grid.insert(0, copy.deepcopy(blank_line))   
    def send_lines(self, amount):
        sent = self.c_table[self.combo][amount] #calculates how many lines are sent based on the current combo
        self.lines += sent
        if (self.combo < 3): #Increase combo if not maxed out
            self.combo += 1
        if (sent == 0):
            return

        if (self.garbage == 0):
            if (self.garbage_queue):
                remaining = sent
                for i in self.garbage_queue:
                    if (i[1]-remaining < 0):
                        remaining -= i[1]
                        i[1] = 0
                    else:
                        i[1] -= remaining
                        remaining = 0
                        break
                if (remaining > 0):
                    self.line_queue.append((self.garbage_id, remaining))
                    self.garbage_id += 1
            else:
                self.line_queue.append((self.garbage_id, sent))
                self.garbage_id += 1
        else:
            if (self.garbage-sent < 0):
                surplus = sent - self.garbage
                to_clear = self.garbage
                if (self.garbage_queue):
                    remaining = surplus
                    for i in self.garbage_queue:
                        if (i[1]-remaining < 0):
                            remaining -= i[1]
                            i[1] = 0
                        else:
                            i[1] -= remaining
                            remaining = 0
                            break
                    if (remaining > 0):
                        self.line_queue.append((self.garbage_id, remaining))
                        self.garbage_id += 1
                else:
                    self.line_queue.append((self.garbage_id, surplus))
                    self.garbage_id += 1
            else:
                to_clear = sent
            delete_garbage = []
            for i in range(20-to_clear, 20):
                delete_garbage.append(i)
            self.clear_lines(delete_garbage)
    def new_active(self):
        del self.active
        self.active = copy.deepcopy(self.tetrimino_queue[0])
        del self.tetrimino_queue[0]
        q = Tetrimino(kind=self.generate_tetrimino())
        self.tetrimino_queue.append(q)
        self.hold_limit = False
    def hold(self):
        if (self.hold_limit):
            return
        if(self.held):
            temp = copy.deepcopy(self.held)
            self.held = self.active
            self.held.reset()
            self.active = temp
            self.hold_limit = True
        else:
            self.held = self.active
            self.held.reset()
            self.new_active()
            self.hold_limit = True
    def add_garbage(self):
        amount = self.garbage_queue.pop(0)[1]
        self.garbage += amount
        garbage_line = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
        for i in range(amount):
            self.grid.pop(0)
            self.grid.append(garbage_line)
        
        vect = self.active.get_vector()
        root = self.active.root
        active_lowst_y = 0
        for j in vect:
            y_val = j[1] + root[1]
            if y_val >= active_lowst_y:
                active_lowst_y = y_val
        if active_lowst_y >= 20-self.garbage:
            self.active.root[1] -= active_lowst_y - (20-self.garbage) + 1

class Tetrimino:
    def __init__(self, kind):
        self.root = [4, 0]
        self.state = 0
        self.kind = kind
        if(kind == "i"):
            self.color = "light blue"
            self.num_states = 2
            #  2 R 3 4
            self.state0 = [[0,0], [-1, 0], [1, 0], [2, 0]] #(x,y) pairs in relation to root node R
            #  2
            #  R
            #  3
            #  4
            self.state1 = [[0,0], [0, -1], [0, 1], [0, 2]]
            self.vectors = {
                0: self.state0,
                1: self.state1
            }
        elif(kind == "o"):
            self.color = "yellow"
            self.num_states = 1
            #  3 4
            #  2 R
            self.state0 = [[0,0], [-1,0], [-1,-1], [0, -1]]
            self.vectors = {
                0: self.state0
            }
        elif(kind == "t"):
            self.color = "pink"
            self.num_states = 4
            #  4 R 2
            #    3
            self.state2 = [[0,0], [1,0], [0,1], [-1, 0]]
            #    4
            #  3 R
            #    2
            self.state3 = [[0,0], [0,1], [-1,0], [0, -1]]
            #    3
            #  2 R 4
            self.state0 = [[0,0], [-1,0], [0,-1], [1, 0]]
            #  2
            #  R 3
            #  4 
            self.state1 = [[0,0], [0, -1], [1,0], [0, 1]]
            self.vectors = {
                0: self.state0,
                1: self.state1,
                2: self.state2,
                3: self.state3
            }
        elif(kind == "j"):
            self.color = "dark blue"
            self.num_states = 4
            #    4
            #    R
            #  3 2
            self.state3 = [[0,0], [0,1], [-1,1], [0, -1]]
            #  3 
            #  2 R 4
            self.state0 = [[0,0], [-1, 0], [-1,-1], [1, 0]]
            #  2 3
            #  R
            #  4
            self.state1 = [[0,0], [0,-1], [1,-1], [0, 1]]
            #  4 R 2
            #      3
            self.state2 = [[0,0], [1,0], [1,1], [-1, 0]]
            self.vectors = {
                0: self.state0,
                1: self.state1,
                2: self.state2,
                3: self.state3
            }
        elif(kind == "l"):
            self.color = "orange"
            self.num_states = 4
            #  2
            #  R
            #  3 4
            self.state1 = [[0,0], [0,-1], [0,1], [1, 1]]
            #  3 R 2
            #  4
            self.state2 = [[0,0], [1,0], [-1,0], [-1, 1]]
            #  4 3
            #    R
            #    2
            self.state3 = [[0,0], [0,1], [0, -1], [-1, -1]]
            #      4
            #  2 R 3
            self.state0 = [[0,0], [-1,0], [1,0], [1, -1]]
            self.vectors = {
                0: self.state0,
                1: self.state1,
                2: self.state2,
                3: self.state3
            }
        elif(kind == "s"):
            self.color = "green"
            self.num_states = 2
            #    3 4
            #  2 R
            self.state0 = [[0,0], [-1,0], [0,-1], [1, -1]]
            #  2
            #  R 3 
            #    4
            self.state1 = [[0,0], [0,-1], [1,0], [1, 1]]
            self.vectors = {
                0: self.state0,
                1: self.state1
            }
        elif(kind == "z"):
            self.color = "red"
            self.num_states = 2
            #  4 3
            #    R 2
            self.state0 = [[0,0], [1,0], [0,-1], [-1, -1]]
            #    4
            #  R 3 
            #  2
            self.state1 = [[0,0], [0,1], [1,0], [1, -1]]
            self.vectors = {
                0: self.state0,
                1: self.state1
            }
    def rotate_clockwise(self):
        if (self.state+1 >= self.num_states):
            self.state = 0
        else:
            self.state += 1
    def rotate_counter_clockwise(self):
        if (self.state-1 < 0):
            self.state = self.num_states - 1
        else:
            self.state -= 1
    def get_vector(self):
        return self.vectors[self.state]
    def reset(self):
        self.state = 0
        self.root = [4, 0]
