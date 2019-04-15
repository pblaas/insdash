from steam import game_servers as gs
import valve.rcon
import sys
import os
import random
import time


__author__ = "Patrick Blaas <patrick@kite4fun.nl>"
__version__ = "0.1"

if "RCONIP" not in os.environ:
    os.environ["RCONIP"] = "0.0.0.0"
if "RCONPASS" not in os.environ:
    os.environ["RCONPASS"] = "none"
if "RCONPORT" not in os.environ:
    os.environ["RCONPORT"] = "27015"
if "INTERVAL" not in os.environ:
    os.environ["INTERVAL"] = "300"

global data

# Only used for debug purposes.
def broadcast_debug(RCONIP,RCONPORT,RCONPASS,MESSAGE):
    print "DEBUG stuff"
    print RCONIP
    print RCONPORT
    print RCONPASS
    print MESSAGE

def broadcast(RCONIP,RCONPORT,RCONPASS,MESSAGE):
    address = (RCONIP, int(RCONPORT))
    password = RCONPASS
    with valve.rcon.RCON(address, password) as rcon:
        rcon.execute(("say " + MESSAGE), block=False, timeout=5)

with open("broadcast.txt", "r") as f:
    data = f.readlines()

while ["true"]:
    for line in data:
        message = line.strip()
        broadcast(os.environ["RCONIP"],os.environ["RCONPORT"],os.environ["RCONPASS"],message)
        time.sleep(int(os.environ["INTERVAL"]))

