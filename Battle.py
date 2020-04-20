#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import math
import time
from datetime import datetime
import threading


DEBUG = 0

Ships = { 
    11: [1, 20, 350, 0, 0, 0, 4, [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]], 
    12: [1, 30, 275, 0, 0, 0, 5, [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]],
    13: [1, 35, 275, 0, 0, 0, 5, [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]],
    
    21: [3, 15, 1600, 0, 0, 0, 7, [21, 22, 23, 31, 32, 33, 11, 12, 13, 41, 42, 43]],
    22: [1, 225, 1500, 0, 0, 0, 9, [31, 32, 33, 41, 42, 43, 21, 22, 23, 11, 12, 13]],
    23: [5, 15, 1500, 0, 0, 0, 10, [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43]],
    
    31: [3, 130, 7500, 2500, 0, 0, 28, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]],
    32: [8, 50, 6000, 2500, 0, 0, 50, [21, 22, 23, 31, 32, 33, 41, 42, 43, 11, 12, 13]],
    33: [1, 4000, 3500, 2500, 0, 0, 32, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]],
    
    41: [4, 400, 10000, 20000, 0, 0, 68, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]],
    42: [6, 750, 10000, 25000, 0, 0, 120, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]],
    43: [6, 800, 10000, 25000, 0, 0, 120, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]]
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

TIMEUNIT = 2

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
                self.fleet.update({ship.shipid : ship})
                ship.start()
                self.ships += n

    def update(self):
        ships = 0
        signature = 0
        for shipid, ship in self.fleet.items():
            ships += ship.effectif
            signature += (ship.signature * ship.effectif)
        self.ships = ships
        self.signature = signature

    def stop(self):
        for shipid, ship in self.fleet.items():
            ship.stop()
            

class Ship(threading.Thread):
    
    def __init__(self, fleet, n, shipid):

        threading.Thread.__init__(self, name=None, target=None)

        args = Ships[shipid]
        
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
        
    def update(self):
        
        self.firepower = self.effectif * self.attack
        self.resistance = self.effectif * self.shield

    def run(self):
        self.running = True
        self.do()
    
    def do(self):

        self.timestamp = datetime.now().timestamp()

        while self.running:
            now = datetime.now().timestamp()
            if now > self.timestamp + (TIMEUNIT / self.cadence):
                Queue.append(self)
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
 

Queue = []

class Battle():
    
    def __init__(self):
        
        self.startTime = datetime.now().timestamp()
        self.do()
        
    def do(self):
        
        while True:
            
            if Queue:
                ship = Queue.pop(0)
                self.fight(ship)
                
                if DEBUG: print ()
                
                now = datetime.now().timestamp()
                self.rounds = math.ceil((now - self.startTime) / TIMEUNIT)
                
                if self.victory():
                    self.stop()
                    self.hitcount()
                    break
        
    def getOpponent(self, attacker):
        
        defenders = []
        
        if type(attacker) is Fleet:
            owner = attacker.owner
        else:
            owner = attacker.fleet.owner
            
        for fleet in Fleets:
            if fleet.owner != owner:
                if fleet.ships != 0:
                    defenders.append(fleet)
        return defenders
        
    def fight(self, attacker):
        
        defenders = self.getOpponent(attacker)
        
        if DEBUG: print("%s (%d)" % (Vaisseaux[attacker.shipid], attacker.effectif))
        
        for shipid in attacker.engagement:
            for defender in defenders:
                if shipid in defender.fleet:
                    ship = defender.fleet[shipid]
                    if ship.effectif > 0:
                        attacker.firepower, kill = ship.hit(attacker.firepower)
                        attacker.addKill(ship.shipid, kill)
                        if DEBUG: print("\t%s (%d) %d" % (ship.shipname, kill, attacker.firepower))
                        if not attacker.firepower:
                            break
    
    def victory(self):
        
        for fleet in Fleets:
            if fleet.ships != 0:
                if self.getOpponent(fleet):
                    return False
        return True
        
    def hitcount(self):
        
        for opponent in Fleets:
            print ("Flotte %s (%d)" % (opponent.owner, opponent.signature))
            for shipid, ship in sorted(opponent.fleet.items()):
                print ("%s (%d)" % (ship.shipname, ship.effectif))
                for idname, kill in sorted(ship.kill.items()):
                    if kill:
                        print ("\t%s (%d)" % (Vaisseaux[idname], kill))
            print ()
            
        print ("en %d round(s)" % self.rounds)
        
    def stop(self):
        for fleet in Fleets:
            fleet.stop()
            

Fleets = []


if __name__ == '__main__':
    
    #oppA = Fleet('A', [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0])
    #oppB = Fleet('B', [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0])
    #oppA = Fleet('A', [0, 0, 0, 0, 0, 0, 2500, 0, 0, 0, 0, 0])
    #oppB = Fleet('B', [0, 0, 0, 2500, 0, 0, 0, 0, 0, 0, 0, 0])

    oppA = Fleet('A', [0, 0, 0, 0, 0, 0, 2500, 0, 11750, 0, 0, 0])
    oppB = Fleet('B', [1189, 265, 0, 247, 350, 257, 380, 886, 317, 489, 588, 0])
    oppC = Fleet('C', [0, 0, 750, 0, 150, 0, 0, 0, 0, 0, 0, 0])

    Fleets.append(oppA)
    Fleets.append(oppB)
    Fleets.append(oppC)
    
    Battle()
