from steam import game_servers as gs
import subprocess
import os
import time
import random

i = open('/home/gamed/inssa/Insurgency/Config/Server/pvemaps.txt', 'r')
o = open('/home/gamed/inssa/Insurgency/Config/Server/MapCycle.txt', 'w')


def randomly(seq):
    shuffled = list(seq)
    random.shuffle(shuffled)
    return iter(shuffled)


try:
    # next(gs.query_master(r'\appid\581320\gameaddr\83.96.176.32'))
    server_addr = next(gs.query_master(r'\appid\581320\name_match\Dutch Recon*'))
    # print(server_addr)
    playerList = gs.a2s_players(server_addr)
    if len(playerList) == 0:
        print "Could now execute a restart"

        for item in randomly(i):
            o.write(item)

    subprocess.call(["/usr/bin/supervisorctl", "stop", "insurgency"], cwd='.')
    print "sleeping 5 seconds"
    time.sleep(5)
    subprocess.call(["/usr/bin/supervisorctl", "start", "insurgency"], cwd='.')
    else:
        print("Process active, no action")

except StopIteration as e:
    print("Error occurred.")
