#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import math
import time
from datetime import datetime
from multiprocessing import Process, Queue, Manager

DEBUG = 0

Ships = { 
    11: [1, 20, 350, 0, 0, 0, 4, [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]], 
    12: [1, 30, 275, 0, 0, 0, 5, [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]],
    13: [1, 35, 275, 0, 0, 0, 5, [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]],
    
    21: [3, 25, 1600, 0, 0, 0, 7, [21, 22, 23, 31, 32, 33, 11, 12, 13, 41, 42, 43]],
    22: [1, 225, 1500, 0, 0, 0, 9, [31, 32, 33, 41, 42, 43, 21, 22, 23, 11, 12, 13]],
    23: [5, 25, 1500, 0, 0, 0, 10, [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]],
    
    31: [3, 130, 7500, 2500, 0, 0, 28, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]],
    32: [8, 50, 6000, 2500, 0, 0, 50, [21, 22, 23, 31, 32, 33, 41, 42, 43, 11, 12, 13]],
    33: [1, 4000, 3500, 2500, 0, 0, 32, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]],
    
    41: [4, 400, 10000, 5000, 0, 0, 68, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]],
    42: [6, 750, 10000, 5000, 0, 0, 120, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]],
    43: [6, 800, 10000, 5000, 0, 0, 120, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]]
    }

Vaisseaux = { 
    11: "Chasseur", 
    12: "Intercepteur",
    13: "Prédateur",
    21: "Corvette légère",
    22: "Corvette lourde",
    23: "Corvette à tir multiple",
    31: "Frégate d'assaut",
    32: "Frégate à missile",
    33: "Frégate à canon ionique",
    41: "Croiseur",
    42: "Croiseur de combat",
    43: "Croiseur d'élite"
    }

TIMEUNIT = 5

class Armada():

    def __init__(self):
        self.fleets = []
        self.fleet = {}

    def addFleet(self, fleet):
        self.fleets.append(fleet)
        for shipid, ship in fleet.fleet.items():
            effectif = ship.effectif
            if shipid in self.fleet:
                effectif += self.fleet[shipid]
            self.fleet.update({shipid : effectif})
        
    def hit(self, shipid, damage):
        firepower = kill = 0
        for fleet in self.fleets:
            if fleet.effectif(shipid):
                dmg = int(damage * (fleet.effectif(shipid) / self.fleet[shipid]))
                fp, k = fleet.fleet[shipid].hit(dmg)
                firepower += fp
                kill += k
        return firepower, kill
    
    def effectif(self, shipid):
        if shipid in self.fleet:
            return self.fleet[shipid]
        else:
            return 0
        

class Fleet():

    def __init__(self, owner, ships):
        self.fleet = {}
        self.ships = 0
        self.signature = 0
        self.owner = owner
        self.addShip(ships)
        
    def addShip(self, ships):
        for index in range(12):
            n = ships[index]
            if n:
                shipid = (int(index / 3) + 1) * 10 + (index % 3 +1)
                ship = Ship(self, n, shipid)
                Battleship.append(ship)
                ship.index = Battleship.index(ship)
                ship.start()
                self.fleet.update({ship.shipid : ship})
                self.ships += n
                self.signature += (ship.signature * ship.effectif)

    def hit(self, shipid, damage):
        firepower, kill = self.fleet[shipid].hit(damage)
        return firepower, kill
    
    def update(self):
        ships = 0
        signature = 0
        for shipid, ship in self.fleet.items():
            ships += ship.effectif
            signature += (ship.signature * ship.effectif)
        self.ships = ships
        self.signature = signature

    def effectif(self, shipid):
        if shipid in self.fleet:
            return self.fleet[shipid].effectif
        else:
            return 0
        
    def stop(self):
        for shipid, ship in self.fleet.items():
            ship.stop()
            

class Ship():
    
    def __init__(self, fleet, n, shipid):

        args = Ships[shipid]
        
        self.index = 0
        self.fleet = fleet
        self.effectif = n
        self.shipid = shipid
        self.shipname = Vaisseaux[shipid]
        self.cadence = args[0]
        self.attack = args[1]
        self.coque = args[2]
        self.shield = args[3]
        self.signature = args[6]
        self.engagement = args[7]
        
        self.kill = {}
        
        self.structure = self.effectif * self.coque
        
        self.update()
        
        self.p = Process(target=self.engine)
        self.p.daemon = True

    def start(self):
        
        self.running = True
        self.p.start()
        
    def update(self):
        
        self.firepower = self.effectif * self.attack
        self.resistance = self.effectif * self.shield

    def engine(self):

        self.timestamp = datetime.now().timestamp() + (2 * TIMEUNIT)

        while self.running:
            now = datetime.now().timestamp()
            if now > self.timestamp + (TIMEUNIT / self.cadence):
                queue.put(self.index)
                self.timestamp = now

    def hit(self, damage):
        
        if damage >= self.structure + self.resistance:
            kill = self.effectif
            self.effectif = 0
            self.structure = 0
            self.stop()
            firepower = damage - (self.structure + self.resistance)
        else:
            kill = math.floor(damage / (self.coque + self.shield))
            self.effectif = self.effectif - kill
            remain = damage % (self.coque + self.shield)
            rd = rs = 0
            if remain:
                if remain > self.shield:
                    dc = remain - self.shield
                else:
                    ds = self.shield - remain
            self.structure = self.effectif * self.coque - rd
            self.resistance = self.effectif * self.shield - rs
            self.firepower = self.effectif * self.attack
            firepower = 0
            
        self.fleet.update()
        
        return firepower, kill

    def addKill(self, shipid, kill):
        
        if shipid in self.kill:
            kill = self.kill[shipid] + kill
        self.kill.update({shipid : kill})
        
    def stop(self):
        self.running = False
 

Battleship = []

queue = Queue()
#queue = Manager().Queue()

statQueue = []

class Battle():
    
    def __init__(self):
        
        self.fleets = []
        
    def addFleet(self, owner, fleet):
        f = Fleet(owner, fleet)
        print ("Flotte %s: %d" % (f.owner, f.signature))
        self.fleets.append(f)
        
    def do(self):
        
        print ("Fight !")
        
        self.startTime = datetime.now().timestamp()

        while True:
            
                index = queue.get()
                self.fight(Battleship[index])
                #statQueue.append(index)
                
                if DEBUG: print ()
                
                now = datetime.now().timestamp()
                self.rounds = math.ceil((now - self.startTime) / TIMEUNIT)
                
                if self.victory():
                    self.stop()
                    self.hitcount()
                    #print ("en %d round(s)" % self.rounds)
                    break
        
    def getOpponent(self, attacker):
        
        armada = Armada()
        
        if type(attacker) is Fleet:
            owner = attacker.owner
        else:
            owner = attacker.fleet.owner
            
        for fleet in self.fleets:
            if fleet.owner != owner:
                if fleet.ships != 0:
                    armada.addFleet(fleet)
                    
        return armada
        
    def fight(self, attacker):
        
        defender = self.getOpponent(attacker)
        
        if DEBUG: print("%s (%d)" % (Vaisseaux[attacker.shipid], attacker.effectif))
        
        for shipid in attacker.engagement:
            if defender.effectif(shipid):
                attacker.firepower, kill = defender.hit(shipid, attacker.firepower)
                attacker.addKill(shipid, kill)
                if DEBUG: print("\t%s (%d) %d" % (Vaisseaux[shipid], kill, attacker.firepower))
                if not attacker.firepower:
                    break
    
    def victory(self):
        
        if self.rounds > 24:
            return True
        
        for fleet in self.fleets:
            if fleet.ships != 0:
                if self.getOpponent(fleet).fleets:
                    return False
        return True
        
    def hitcount(self):
        
        print ()
        for opponent in self.fleets:
            print ("Flotte %s (%d)" % (opponent.owner, opponent.signature))
            for shipid, ship in sorted(opponent.fleet.items()):
                print ("%s (%d)" % (ship.shipname, ship.effectif))
                for idname, kill in sorted(ship.kill.items()):
                    if kill:
                        print ("\t%s (%d)" % (Vaisseaux[idname], kill))
            print ()
            
        print ("en %d round(s)" % self.rounds)
        
    def stop(self):
        for fleet in self.fleets:
            fleet.stop()
            

if __name__ == '__main__':
    
    battle = Battle()
    
    #battle.addFleet ('A', [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0])
    #battle.addFleet ('B', [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0])
    #battle.addFleet ('A', [0, 0, 0, 0, 0, 0, 2500, 0, 0, 0, 0, 0])
    #battle.addFleet ('B', [0, 0, 0, 2500, 0, 0, 0, 0, 0, 0, 0, 0])
    #battle.addFleet( 'A', [0, 0, 0, 0, 0, 0, 2500, 0, 11750, 0, 0, 0] )
    #battle.addFleet( 'B', [1189, 265, 0, 247, 350, 257, 380, 886, 317, 489, 588, 0] )
    #battle.addFleet( 'A', [0, 0, 750, 0, 150, 0, 0, 0, 0, 0, 0, 0] )
    #battle.addFleet( 'A', [5, 5, 5, 5, 5, 5, 2500, 250, 12500, 5, 1750, 0] )
    
    battle.addFleet( 'A', [1000, 1000, 500, 1000, 1000, 1000, 1000, 1000, 1000, 500, 1500, 250] )
    battle.addFleet( 'B', [669, 961, 0, 254, 212, 423, 424, 967, 388, 319, 640, 0] )
    '''
    battle.addFleet( 'C', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'D', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'E', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'F', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'G', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'H', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'I', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'J', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'K', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'L', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'M', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'N', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    battle.addFleet( 'O', [750, 750, 50, 250, 250, 500, 500, 1000, 500, 250, 750, 50] )
    '''
    
    battle.do()
    
    def stats():
        res = {}
        for index in statQueue:
            ship = Battleship[index]
            if ship.fleet.owner == 'A':
                count = 0
                if ship.shipid in res:
                    count = res[ship.shipid]
                res.update({ship.shipid : count + 1})
                
        for ship, count in sorted(res.items()):
            moyenne = round(count / (battle.rounds / TIMEUNIT))
            print ("%s: %d (%d - %d)" % (Vaisseaux[ship], count, moyenne, Ships[ship][0]))
    
    #stats()
