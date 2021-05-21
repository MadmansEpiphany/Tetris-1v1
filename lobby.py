import socket, random, rendering, pygame, game_loop, sys, threading
import urllib.request #Used to get NAT IP from a web api
from datetime import datetime,timezone

#CONSTANTS AND GLOBAL VARIABLES
HOST_PORT = ("", 1337)
user_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8') #web api call to get NAT IP
p2_conn = False
p2_addr = ""
shared_seed = ""
start_time = None
ready = False
s = None

WIDTH, HEIGHT = 1280, 720
screen = "main"
create_lobby_button = pygame.Rect(WIDTH/2 - 300, HEIGHT/2 - 200, 600, 100)
join_lobby_button = pygame.Rect(WIDTH/2 - 300, HEIGHT/2, 600, 100)

user_ip_display = pygame.Rect(WIDTH//4 - 300, HEIGHT//4, 600, 100)
p2_ip_display = pygame.Rect(WIDTH//2, HEIGHT//4, 600, 100)
start_button = pygame.Rect(WIDTH//2, HEIGHT//2, 600, 100)
quit_lobby_button = pygame.Rect(WIDTH//4 - 300, HEIGHT//2, 600, 100)
button_text = ""

p2_ip_typeable = False
typing_active = False
start_clickable = True

#FUNCTIONS
def handle_mouse_input(event):
    global screen, button_text, p2_ip_typeable, start_time, ready, s, start_clickable
    if (screen == "main"):
        if (create_lobby_button.collidepoint(event.pos)):
            screen = "host"
            lobby_thread = threading.Thread(target=create, daemon=True)
            lobby_thread.start()
        elif (join_lobby_button.collidepoint(event.pos)):
            screen = "client"
            p2_ip_typeable = True
            button_text = "Connect"
        else:
            screen = "main"
        
    elif (screen == "host"):
        if (user_ip_display.collidepoint(event.pos)):
            pass #Ideally copies user_ip to clipboard, but can't get it to work rn
        elif (p2_ip_display.collidepoint(event.pos)):
            pass
        elif (start_button.collidepoint(event.pos)) and (start_clickable) and (ready):
            utc_now = datetime.now(timezone.utc)
            minute, second, microsecond = int(utc_now.strftime("%M")), int(utc_now.strftime("%S")), int(utc_now.strftime("%f"))
            second += 5 #game starts 10s from when the start button is pressed
            if(second >= 60):
                second -= 60
                minute += 1
                if (minute >= 60):
                    minute -= 60
            start_time = [minute, second, microsecond] #we now have a representation of a starting time(we don't need the hour)
            p2_conn.sendall((str(minute) + " " + str(second) + " " + str(microsecond) + "/E").encode("utf-8"))
            start_clickable = False
        elif (quit_lobby_button.collidepoint(event.pos)):
            screen = "main"
            button_text = ""
            if (s):
                s.close() #This will cause the console to complain that we aborted the connection prematurely, but it works as intended - so I guess it's ok
                s = None
            if (p2_conn):
                p2_conn.close()
            ready = False
        
    elif (screen == "client"):
        global typing_active, p2_addr
        typing_active = False
        if (user_ip_display.collidepoint(event.pos)):
            pass #Ideally copies user_ip to clipboard, but can't get it to work rn
        elif (p2_ip_display.collidepoint(event.pos)):
            typing_active = True
        elif (start_button.collidepoint(event.pos)) and (not p2_conn):
            lobby_thread = threading.Thread(target=join, daemon=True)
            lobby_thread.start()
        elif (quit_lobby_button.collidepoint(event.pos)):
            screen = "main"
            p2_addr = ""
            button_text = ""
            p2_ip_typeable = False
            if (p2_conn):
                p2_conn.close()
            ready = False

def handle_key_input(event):
    global p2_addr
    if (p2_ip_typeable and typing_active): #credit to geeksforgeeks for input box solution
        if (event.key == pygame.K_BACKSPACE):
            p2_addr = p2_addr[:-1]
        else:
            p2_addr += event.unicode

def create():
    global p2_conn, p2_addr, shared_seed, ready, button_text
    global s
    
    button_text = "Waiting for connection"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(HOST_PORT)
    
    while not p2_conn:
        s.listen()
        p2_conn, addr_temp = s.accept()
        p2_addr = addr_temp[0]

    shared_seed = random.randint(0, 696969)
    p2_conn.sendall(("Seed: " + str(shared_seed) + "/E").encode("utf-8")) #send shared_seed

    response = ""
    while not response.endswith("/E"):
        response += p2_conn.recv(4096).decode("utf-8")
    if (not response == "OK/E"):
        p2_conn.close()
        p2_conn = False
        print ("Connection dropped. Listening for new connection")
        create() #calls itself again to listen for a new connection
    else:
        ready = True #Game is ready to begin. Waiting on host to press start - which will generate a utc time object, share it, and start the game on both ends at that time

    button_text = "Start"

def join():
    global p2_conn, shared_seed, ready, start_time, button_text

    button_text = "Connecting"
    p2_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        p2_conn.connect((p2_addr, 1337))
    except:
        print("Invalid Host IP")
        p2_conn = False
        button_text = "Connect"
        return

    data = ""
    while not data.endswith("/E"):
        data += p2_conn.recv(4096).decode("utf-8")
    data = data[:-2]
    data = data.split()
    if (data[0] == "Seed:"):
        shared_seed = data[1].replace("/E", "")
    else:
        print("Invalid Host IP")
        p2_conn = False
        button_text = "Connect"
        return

    p2_conn.sendall(("OK/E").encode("utf-8"))
    ready = True #Both players should have eveything now. Just waiting on host to send a utc time object with the start time
    button_text = "Connected. Waiting for host"

    data = ""
    while not data.endswith("/E"):
        data += p2_conn.recv(4096).decode("utf-8") #May change if there is a better encoding for utc time object
    data = data[:-2]
    data = data.split()
    temp = []
    for i in data:
        temp.append(int(i))
    start_time = temp

def main():
    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick_busy_loop()

        time_utc = datetime.now(timezone.utc)
        minute, second, microsecond = int(time_utc.strftime("%M")), int(time_utc.strftime("%S")), int(time_utc.strftime("%f"))
        if (start_time):
            if (minute >= start_time[0]) and (second >= start_time[1]) and (microsecond >= start_time[2]):
                p2_conn.close()
                if(s):
                    s.close()
                game_loop.main(p2_addr, seed=shared_seed, start=start_time)

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                running = False
                if (s):
                    s.close()
                if (p2_conn):
                    p2_conn.close()
                break
            if (event.type == pygame.KEYDOWN):
                handle_key_input(event)
            if (event.type == pygame.MOUSEBUTTONDOWN):
                handle_mouse_input(event)

        mouse_pos = pygame.mouse.get_pos()

        if (screen == "main"):
            rendering.draw_main_screen(create_lobby_button, join_lobby_button, mouse_pos)
        elif (screen == "host"):
            rendering.draw_lobby_host(user_ip_display, p2_ip_display, quit_lobby_button, start_button, mouse_pos, user_ip, p2_addr, button_text)
        elif (screen == "client"):
            rendering.draw_lobby_client(user_ip_display, p2_ip_display, quit_lobby_button, start_button, mouse_pos, user_ip, p2_addr, typing_active, button_text)
        if (ready) and (start_time):
            rendering.draw_start_timer(second, microsecond, start_time)

    pygame.quit()
    sys.exit()

if (__name__ == "__main__"):
    pygame.init()
    rendering.create_window(WIDTH, HEIGHT)
    main()
