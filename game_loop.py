import rendering, pygame, random, copy, sys, time
import game_classes as gc
import p2p_client as network
from datetime import datetime,timezone

def handle_player_input(key, player): #UP = ROTATE CLOCKWISE, CTRL(either one) = ROTATE COUNTERCLOCKWISE, SPACE = HARDDROP, SHIFT = HOLD
    root = copy.deepcopy(player.active.root) #copy of root
    
    if (key == pygame.K_UP):
        player.active.rotate_clockwise() #try to rotate first
        vect = player.active.get_vector()
        for i in vect:
            coord = (i[0]+root[0], i[1]+root[1])
            if (coord[0] < 0) or (coord[0] >= 10) or (coord[1] >= 20) or (player.check_collision(coord)):
                player.active.rotate_counter_clockwise()
                break
    elif (key == pygame.K_LCTRL) or (key == pygame.K_RCTRL):
        player.active.rotate_counter_clockwise() #same as above
        vect = player.active.get_vector()
        for i in vect:
            coord = (i[0]+root[0], i[1]+root[1])
            if (coord[0] < 0) or (coord[0] >= 10) or (coord[1] >= 20) or (player.check_collision(coord)):
                player.active.rotate_clockwise()
                break
    elif (key == pygame.K_LEFT):
        vect = player.active.get_vector()
        for i in vect:
            coord = (i[0]+root[0] - 1, i[1]+root[1])
            if (coord[0] < 0) or (player.check_collision(coord)): #checking that no square in the tetrimino is over the left or colliding
                return
        player.active.root[0] -= 1
    elif (key == pygame.K_RIGHT):
        vect = player.active.get_vector()
        for i in vect:
            coord = (i[0]+root[0] + 1, i[1]+root[1])
            if (coord[0] >= 10) or (player.check_collision(coord)): #same as above
                return
        player.active.root[0] += 1
    elif (key == pygame.K_DOWN):
        vect = player.active.get_vector()
        for i in vect:
            coord = (i[0]+root[0], i[1]+root[1] + 1)
            if (coord[1] >= 20) or (player.check_collision(coord)):
                place_on_grid(player, vect, root)
                return
        player.active.root[1] += 1
    elif (key == pygame.K_SPACE):
        hard_drop(player)
    elif (key == pygame.K_LSHIFT) or (key == pygame.K_RSHIFT):
        player.hold()

def ghost_piece_root(player):
    root = copy.deepcopy(player.active.root)
    vect = player.active.get_vector()
    ghost_root = root
    for j in range(root[1], 20):
        done = False
        for i in vect:
            x = i[0] + root[0]
            if (j == 19):
                ghost_root = [x-i[0], j]
                done = True
                break
            if (player.grid[j][x] != 0):
                ghost_root = [x-i[0], j-i[1]-1]
                done = True
                break
        if (done == True):
            break

    collision = True
    while (collision == True):
        collision = False
        for i in vect:
            coord = (ghost_root[0]+i[0], ghost_root[1]+i[1])
            if (coord[1] > 19) or (player.check_collision(coord)):
                collision = True
                ghost_root[1] -= 1
                break
    
    return ghost_root

def hard_drop(player):
    ghost_root = ghost_piece_root(player)
    player.active.root = copy.deepcopy(ghost_root) #copy
    vect = player.active.get_vector()
    root = copy.deepcopy(player.active.root) #extra safe lol
    place_on_grid(player, vect, root) #subject to change

def handle_drop(player):
    root = copy.deepcopy(player.active.root)
    vect = player.active.get_vector()
    for i in vect:
        coord = (i[0]+root[0], i[1]+root[1] + 1)
        if (coord[1] >= 20) or (player.check_collision(coord)):
            place_on_grid(player, vect, root)
            return
    player.active.root[1] += 1

def handle_ko(p1, p2p):
    if(p1.lives - 1 == 0):
        p1.lives = 0              
        pygame.time.set_timer(LOSE, 1000, True)
        return

    if(p1.garbage == 0):
        p1.lives = 0                
        pygame.time.set_timer(LOSE, 1000, True)
        return

    p1.lives -= 1
    delete_garbage = []
    for i in range(20-p1.garbage, 20):
        delete_garbage.append(i)
    p1.clear_lines(delete_garbage)
    
    p1.garbage = 0
    p1.garbage_queue.clear()

def game_lost(p2p):
    rendering.draw_lost()
    time.sleep(5)
    pygame.quit()
    p2p.close_sockets()
    sys.exit()

def game_win(p2p):
    rendering.draw_win()
    time.sleep(5)
    pygame.quit()
    p2p.close_sockets()
    sys.exit()

def game_tie(p2p):
    rendering.draw_tie()
    time.sleep(5)
    pygame.quit()
    p2p.close_sockets()
    sys.exit()

def place_on_grid(player, vect, root):
    color = player.active.color
    num = player.grid_number[color]
    high = 0
    low = 19
    for i in vect: #add the tetrimino's blocks to the grid
        x = i[0]+root[0]
        y = i[1]+root[1]
        player.grid[y][x] = num
        if (y <= low):
            low = copy.copy(y)
        if (y >= high):
            high = copy.copy(y)
    
    if(low < 0):
        pygame.time.set_timer(KO, 10, True)
    check_lines(player, low, high) #check if placing tetrimino cleared lines
    player.new_active() #Get and set a new active tetrimino


def check_lines(player, low, high):
    lines = []
    for y in range(low, high+1):
        line = copy.deepcopy(player.grid[y])
        tba = True
        for num in line:
            if num == 0:
                tba = False
                break
        if (tba == True):
            lines.append(y)
    
    if (lines): #if there are lines to clear
        player.clear_lines(lines)
        player.send_lines(len(lines))
    else:
        player.combo = 0

def get_end_time(st):
    end = copy.deepcopy(st)
    end[0] += 2
    return end

def endgame(p1, p2, p2p):
    time.sleep(1) #wait 1 sec just in case any last-second packets come in

    if (p1.lives > p2.lives):
        game_win(p2p)
    elif (p1.lives < p2.lives):
        game_lost(p2p)
    else:
        if (p1.lines > p2.lines):
            game_win(p2p)
        elif (p1.lines < p2.lines):
            game_lost(p2p)
        else:
            game_tie(p2p)

def main(p2_ip, seed, start):
    #Initialize variables and game objects
    clock = pygame.time.Clock()
    end_time = get_end_time(start)
    p1 = gc.Gamestate(seed)
    p2 = gc.Gamestate(seed)
    p2p = network.P2p_client(p2_ip, p1, p2)
    
    DROP = pygame.USEREVENT + 1 #Natural dropping event
    global KO 
    KO = pygame.USEREVENT + 3 #Player losing live event
    global LOSE
    LOSE = pygame.USEREVENT + 4#Player losing game event

    pygame.time.set_timer(DROP, 1000) #Neutral drop rate
    p2p.start_recv_thread()

    running = True
    while running:
        clock.tick()

        time_utc = datetime.now(timezone.utc)
        minute, second, microsecond = int(time_utc.strftime("%M")), int(time_utc.strftime("%S")), int(time_utc.strftime("%f"))        
        if (minute >= end_time[0]) and (second >= end_time[1]) and (microsecond >= end_time[2]):
            endgame(p1, p2, p2p)
        
        remaining_seconds = end_time[1]-second
        remaining_minutes = end_time[0]-minute
        if (remaining_seconds < 0):
            remaining_seconds += 60
            remaining_minutes -= 1
        if (remaining_minutes < 0):
            remaining_minutes += 60
        remaining = [remaining_minutes, remaining_seconds]

        for event in pygame.event.get(): #check and handle events
            if (event.type == pygame.QUIT): #quit event
                running = False
                break
            if (event.type == DROP): #timed drop event
                handle_drop(p1)
            if (event.type == pygame.KEYDOWN): #user input event
                handle_player_input(event.key, p1)        
            if (event.type == network.GARBAGE):
                p1.add_garbage()
            if(event.type == KO):
                handle_ko(p1, p2p)
            if(event.type == LOSE):
                game_lost(p2p)
            if(event.type == network.WIN):
                game_win(p2p)

        ghost_root = ghost_piece_root(p1)
        p2p.send_state(p2p.create_send_package())
        rendering.draw_window(p1, p2, ghost_root, remaining) #render everything onto the screen
            
    pygame.quit()
    p2p.close_sockets()
    sys.exit()

if (__name__ == "__main__"):
    pygame.init()
    rendering.create_window(1280, 720) #create a 1280x720p window
    time_utc = datetime.now(timezone.utc)
    m, s, mus = int(time_utc.strftime("%M")), int(time_utc.strftime("%S")), int(time_utc.strftime("%f"))
    start_time = [m, s, mus]
    main(seed=random.randint(0, 696969), p2_ip="127.0.0.1", start=start_time)
