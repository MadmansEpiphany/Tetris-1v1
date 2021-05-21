import json, socket, threading, pygame

GAME_PORT = 1337
GARBAGE = pygame.USEREVENT + 2 #Garbage placement event
WIN = pygame.USEREVENT + 5 #Player wins game event
class P2p_client:
    def __init__(self, opp_ip, p1, p2):
        # Networking 
        self.opp_ip = opp_ip
        self.sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvSock.bind(("", GAME_PORT))
        self.p1 = p1
        self.p2 = p2
        self.unacknowledged = {0} #weird initialization but needed for python to understand this is a set
        self.acks = []
        self.gg = False
        self.own_seq = 0
        self.p2_seq = 0

    def receiving(self):
        while True:
            try:
                data = self.recvSock.recv(1024) # buffer size is 1024 bytes                
                data = json.loads(data.decode())

                seq_num = data.get("seq")
                if not (seq_num > self.p2_seq):
                    continue #skips this packet if it's stale
                else:
                    self.p2_seq = seq_num
                
                self.p2.lives = data.get("lives")
                if (self.p2.lives <= 0):
                    pygame.time.set_timer(WIN, 2000, True)
                    self.acks.append("gg")
                kind = data.get("kind")
                while (kind != self.p2.active.kind):
                    self.p2.new_active()
                self.p2.grid = data.get("grid")
                self.p2.active.root = data.get("root")
                self.p2.active.state = data.get("state")
                self.p2.lines = data.get("lines")
                
                new_garbage = data.get("garbage")
                if (new_garbage):
                    do_not_accept = {0} #forming a list of duplicates to check against
                    for i in self.p1.garbage_queue:
                        do_not_accept.add(i[0])
                    self.acks = [] #our next message's acks will depend only on what was just sent. If our acks get lost, the opponent will resend them and we will try to reack them
                    counter = 0
                    for i in new_garbage:
                        if (i[0] in do_not_accept):
                            self.acks.append(i[0]) #add the garbage id to the acks for the next message(s)
                            continue
                        self.p1.garbage_queue.append(i) #add the garbage to our player's queue
                        counter += 1
                        self.acks.append(i[0]) #add the garbage id to the acks for the next message(s)
                        pygame.time.set_timer(GARBAGE, counter*300, True)
                
                acked_garbage = data.get("acks")
                if (acked_garbage):
                    for i in acked_garbage:
                        if (i == "gg"):
                            self.gg = False
                        if (i in self.unacknowledged):
                            self.unacknowledged.discard(i) #remove from unacknowledged
                            for entry in self.p1.line_queue: #also find it in the line_queue and remove it from there
                                if (entry[0] == i):
                                    self.p1.line_queue.remove(entry)
                                    break #no need to keep looking if we found it

            except Exception as e:
                print(e)        

    def create_send_package(self):
        self.own_seq += 1
        garbage = []
        if (self.p1.line_queue): #if our line_queue is not empty
            for entry in self.p1.line_queue:
                garbage.append(entry)
                if (not entry[0] in self.unacknowledged):
                    self.unacknowledged.add(entry[0])

        package = json.dumps({"seq" : self.own_seq, "grid" : self.p1.grid, "kind" : self.p1.active.kind, "root" : self.p1.active.root, "state" : self.p1.active.state, "garbage" : garbage, "acks": self.acks, "lives" : self.p1.lives, "lines" : self.p1.lines})
        return package

    def send_state(self, data):
        self.sendSock.sendto(data.encode(), (self.opp_ip, GAME_PORT))

    def start_recv_thread(self):
        receive = threading.Thread(target=self.receiving, daemon=True)
        receive.start()

    def close_sockets(self):
        self.recvSock.close()
        self.sendSock.close()
