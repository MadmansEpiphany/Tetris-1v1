# Tetris-1v1

## Requirements
Python version 3.7+ (pygame will crash if python version is too low)

Willingness to set up port forwarding on your router.

Willingness to share your ip with your opponent.

## Instalation
Assuming you have a recent enough python version, use these terminal commands to install pygame and update your certificates (for a web api call that tells you your ip).

```bash
pip3 install pygame
pip3 install --upgrade certifi
```

Now you need to set up port forwarding for port 1337 on your router. A guide on how to do that: https://www.howtogeek.com/66214/how-to-forward-ports-on-your-router/

Please make sure you set up forwarding for both TCP and UDP, otherwise the game will not work!

You may also want to configure static device IP assignment on your LAN (or set up the port forwarding to be MAC based rather than IP based if the router allows for it). The above link contains a section on how to do this too.

## Running the game
To run the game as intended, open a terminal, navigate to the Tetris-1v1 folder, and run the following command:

```bash
python3 lobby.py
```

It is also possible to run the game in a pseudo singleplayer mode where both players are controlled by you, by running:

```bash
python3 game_loop.py
```

## Known bugs
Opponent's "next tetriminos" display does not work properly.

Both players are meant to have the exact same order of tetriminos, however this does not currently work.