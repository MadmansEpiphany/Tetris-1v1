import pygame, os
pygame.font.init() #why does this increase boot time so much lol?

#CONSTANTS
PURPLE = (125, 0, 125)
BLACK = (0, 0, 0)
GRAY = (105, 105, 105)
LIGHT_GRAY = (211, 211, 211)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GARBAGE_COLOR = (36, 36, 36)
color = {
    0: GRAY,
    1: "light blue",
    2: "yellow",
    3: "pink",
    4: "dark blue",
    5: "orange",
    6: "green",
    7: "red",
    8: GARBAGE_COLOR
}
block_size = 30 #Should eventually become a variable size based on resolution*
mini_size = 15
SCORE_FONT = pygame.font.SysFont('Arial', 30)
INFO_FONT = pygame.font.SysFont('Arial', 30)
LOBBY_FONT = pygame.font.SysFont('Arial', 50)
BIG_FONT = pygame.font.SysFont('Arial', 80)
GAME_OVER_FONT = pygame.font.SysFont('Arial', 140)

#FUNCTIONS:
def create_window(w=900, h=500):
    global WIN, WIDTH, HEIGHT
    WIDTH, HEIGHT = w, h
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris 1v1")

#Game Screen Functions
def draw_window(p1, p2, ghost_root, time_left):
    line_text = SCORE_FONT.render("Lines sent: " + str(p1.lines), 1, WHITE)
    lives_text = SCORE_FONT.render("Lives: " + str(p1.lives), 1, WHITE)
    opponent_text = SCORE_FONT.render("Opponent Lines sent: " + str(p2.lines), 1, WHITE)
    opp_lives_text = SCORE_FONT.render("Opponent Lives: " + str(p2.lives), 1, WHITE)
    held_text = INFO_FONT.render("Held: ", 1, WHITE)
    next_text = INFO_FONT.render("Next: ", 1, WHITE)
    time_text = INFO_FONT.render(str(time_left[0]) + ":" + str(time_left[1]), 1, WHITE)

    WIN.fill(PURPLE) #Set background to purple

    #draw p1 side
    try:
        draw_grid(p1, (100, 80))
        draw_ghost(p1.active, ghost_root, (100, 80))
        draw_tetrimino(p1.active, (100, 80))
        draw_text(line_text, (100, 30))
        draw_text(lives_text, (100, 5))
        draw_text(time_text, (WIDTH//2-time_text.get_width()//2, 20))
        draw_held(p1, (100-held_text.get_width() - 10, 70), held_text)
        draw_next(p1, (415, 70), next_text)
    except Exception as e:
        print(e)
        return

    #draw p2 side
    try:
        draw_grid(p2, (800,80))
        draw_tetrimino(p2.active, (800,80))
        draw_text(opponent_text, (800,30))
        draw_text(opp_lives_text, (800,5))
        draw_next(p2, (1115, 70), next_text)
    except Exception as e:
        print(e)
        return

    pygame.display.update()

def draw_grid(player, offset):
    for y in range(0, 20):
        for x in range (0, 10):
            square = pygame.Rect(offset[0]+block_size*x, offset[1]+block_size*y, block_size, block_size)
            square_color = color[player.grid[y][x]]
            pygame.draw.rect(WIN, square_color, square)

def draw_tetrimino(tet, offset):
    vect = tet.get_vector()
    root = tet.root
    for i in vect:
        square = pygame.Rect(offset[0]+block_size*(i[0]+root[0]), offset[1]+block_size*(i[1]+root[1]), block_size, block_size)
        square_color = tet.color
        pygame.draw.rect(WIN, square_color, square)

def draw_ghost(tet, ghost_root, offset):
    vect = tet.get_vector()
    root = tet.root
    for i in vect:
        ghost_square = pygame.Rect(offset[0]+block_size*(i[0]+ghost_root[0]), offset[1]+block_size*(i[1]+ghost_root[1]), block_size, block_size)
        pygame.draw.rect(WIN, LIGHT_GRAY, ghost_square)

def draw_text(text, location):
    WIN.blit(text, location)

def draw_held(player, location, text): #NEEDS SOME WORK, but rudamentary prototype ok
    WIN.blit(text, location)
    held = player.held
    if (type(held) is bool):
        return
    else:
        offset = (location[0] + 1.5*mini_size, location[1] + 5*mini_size)
        for i in held.get_vector():
            square = pygame.Rect(offset[0]+mini_size*i[0], offset[1]+mini_size*i[1], mini_size, mini_size)
            square_color = held.color
            pygame.draw.rect(WIN, square_color, square)

def draw_next(player, location, text):
    WIN.blit(text, location)
    queue = player.tetrimino_queue
    offset = [location[0] + 1.5*mini_size, location[1]]
    for tet in queue:
        offset[1] += 5*mini_size
        square_color = tet.color
        for i in tet.get_vector():
            square = pygame.Rect(offset[0]+mini_size*i[0], offset[1]+mini_size*i[1], mini_size, mini_size)
            pygame.draw.rect(WIN, square_color, square)

def draw_lost():
    WIN.fill(PURPLE)
    lost_text = GAME_OVER_FONT.render("YOU LOST", 1, WHITE)

    draw_text(lost_text, (350, 300))
    pygame.display.update()

def draw_win():
    WIN.fill(PURPLE)
    lost_text = GAME_OVER_FONT.render("YOU WIN", 1, WHITE)

    draw_text(lost_text, (350, 300))
    pygame.display.update()

def draw_tie():
    WIN.fill(PURPLE)
    lost_text = GAME_OVER_FONT.render("YOU TIED", 1, WHITE)

    draw_text(lost_text, (350, 300))
    pygame.display.update()

#Lobby Screen Functions
def draw_main_screen(button1, button2, mouse_pos):
    button1_text = LOBBY_FONT.render("Create Lobby", 1, WHITE)
    button2_text = LOBBY_FONT.render("Join Lobby", 1, WHITE)
    if button1.collidepoint(mouse_pos):
        color1 = LIGHT_GRAY
    else:
        color1 = GRAY
    if button2.collidepoint(mouse_pos):
        color2 = LIGHT_GRAY
    else:
        color2 = GRAY

    WIN.fill(PURPLE)
    pygame.draw.rect(WIN, color1, button1)
    pygame.draw.rect(WIN, color2, button2)
    WIN.blit(button1_text, (button1.left + ((button1.width-button1_text.get_width()))/2, button1.top + button1_text.get_height()/2))
    WIN.blit(button2_text, (button2.left + ((button2.width-button2_text.get_width()))/2, button2.top + button2_text.get_height()/2))

    pygame.display.update()

def draw_lobby_host(button1, button2, button3, button4, mouse_pos, user_ip, p2_ip, action_text):
    if (isinstance(p2_ip, tuple)):
        give = p2_ip[0]
    else:
        give = p2_ip

    top_text = LOBBY_FONT.render("Creating Lobby", 1, WHITE)
    button1_text = LOBBY_FONT.render("IP: " + user_ip, 1, WHITE)
    button2_text = LOBBY_FONT.render("P2 IP: " + give, 1, WHITE)
    button3_text = LOBBY_FONT.render("Quit Lobby", 1, WHITE)
    button4_text = LOBBY_FONT.render(action_text, 1, WHITE)

    if button1.collidepoint(mouse_pos):
        color1 = LIGHT_GRAY
    else:
        color1 = GRAY
    if button2.collidepoint(mouse_pos):
        color2 = LIGHT_GRAY
    else:
        color2 = GRAY
    if button3.collidepoint(mouse_pos):
        color3 = LIGHT_GRAY
    else:
        color3 = GRAY
    if button4.collidepoint(mouse_pos):
        color4 = LIGHT_GRAY
    else:
        color4 = GRAY

    WIN.fill(PURPLE)
    pygame.draw.rect(WIN, color1, button1)
    pygame.draw.rect(WIN, color2, button2)
    pygame.draw.rect(WIN, color3, button3)
    pygame.draw.rect(WIN, color4, button4)
    WIN.blit(top_text, (WIDTH//2 - top_text.get_width()//2, 70))
    WIN.blit(button1_text, (button1.left + ((button1.width-button1_text.get_width()))/2, button1.top + button1_text.get_height()/2))
    WIN.blit(button2_text, (button2.left + ((button2.width-button2_text.get_width()))/2, button2.top + button2_text.get_height()/2))
    WIN.blit(button3_text, (button3.left + ((button3.width-button3_text.get_width()))/2, button3.top + button3_text.get_height()/2))
    WIN.blit(button4_text, (button4.left + ((button4.width-button4_text.get_width()))/2, button4.top + button4_text.get_height()/2))

    pygame.display.update()    

def draw_lobby_client(button1, button2, button3, button4, mouse_pos, user_ip, p2_ip, active, action_text):
    if (isinstance(p2_ip, tuple)):
        give = p2_ip[0]
    else:
        give = p2_ip
        
    top_text = LOBBY_FONT.render("Joining Lobby", 1, WHITE)
    button1_text = LOBBY_FONT.render("IP: " + user_ip, 1, WHITE)
    button2_text = LOBBY_FONT.render("Host: " + give, 1, WHITE)
    button3_text = LOBBY_FONT.render("Quit Lobby", 1, WHITE)
    button4_text = LOBBY_FONT.render(action_text, 1, WHITE)

    if button1.collidepoint(mouse_pos):
        color1 = LIGHT_GRAY
    else:
        color1 = GRAY
    if button2.collidepoint(mouse_pos):
        color2 = LIGHT_GRAY
    else:
        color2 = GRAY
    if active:
        color2 = (0, 96, 255)
    if button3.collidepoint(mouse_pos):
        color3 = LIGHT_GRAY
    else:
        color3 = GRAY
    if button4.collidepoint(mouse_pos):
        color4 = LIGHT_GRAY
    else:
        color4 = GRAY

    WIN.fill(PURPLE)
    pygame.draw.rect(WIN, color1, button1)
    pygame.draw.rect(WIN, color2, button2)
    pygame.draw.rect(WIN, color3, button3)
    pygame.draw.rect(WIN, color4, button4)
    WIN.blit(top_text, (WIDTH//2 - top_text.get_width()//2, 70))
    WIN.blit(button1_text, (button1.left + ((button1.width-button1_text.get_width()))/2, button1.top + button1_text.get_height()/2))
    WIN.blit(button2_text, (button2.left + ((button2.width-button2_text.get_width()))/2, button2.top + button2_text.get_height()/2))
    WIN.blit(button3_text, (button3.left + ((button3.width-button3_text.get_width()))/2, button3.top + button3_text.get_height()/2))
    WIN.blit(button4_text, (button4.left + ((button4.width-button4_text.get_width()))/2, button4.top + button4_text.get_height()/2))

    pygame.display.update()    

def draw_start_timer(second, microsecond, start_time):
    micro_diff = start_time[2] - microsecond
    if (micro_diff < 0):
        micro_diff += 1000000
        second += 1
    second_diff = start_time[1] - second
    if (second_diff < 0):
        second_diff += 60

    countdown_text = BIG_FONT.render("Starting in: " + str(second_diff) + "." + str(micro_diff) + "s", 1, RED)
    WIN.blit(countdown_text, (WIDTH//2 - countdown_text.get_width()//2, HEIGHT-2*countdown_text.get_height()))
    pygame.display.update()
