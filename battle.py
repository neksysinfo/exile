#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import math
import random
import time
from datetime import datetime

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
    
    41: [4, 400, 10000, 25000, 0, 0, 68, [41, 42, 43, 31, 32, 33, 21, 22, 23, 11, 12, 13]],
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
                fleet = []
                if shipid in Battleship:
                    fleet = Battleship[shipid]
                fleet.append(self)
                Battleship.update({shipid : fleet})
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
        

class Ship():
    
    def __init__(self, fleet, n, shipid):

        args = Ships[shipid]
        
        self.fleet = fleet
        self.effectif = n
        self.shipid = shipid
        self.shipname = Vaisseaux[shipid]
        self.cadence = args[0]
        self.attack = args[1]
        self.hull = args[2] + args[3]
        #self.shield = args[3]
        self.signature = args[6]
        self.engagement = args[7]
        
        self.kill = {}
        
        self.damage_hull = 0
        #self.damage_shield = 0
        
        self.update()
        
    def update(self):
        
        self.firepower = self.effectif * self.attack * self.cadence
        self.structure = self.effectif * self.hull - self.damage_hull
        #self.resistance = self.effectif * self.shield - self.damage_shield

    def hit(self, damage):
        
        kill = 0
        
        if damage >= self.structure:
            kill = self.effectif
            self.effectif = 0
            self.damage_hull = 0
            firepower = damage - self.structure
            
        else:
            defense = self.structure - damage
            effectif = math.ceil(defense / self.hull)
            kill = self.effectif - effectif
            self.effectif = effectif
            
            self.damage_hull += damage - (kill * self.hull)
            
            if DEBUG: print ("damage kill/remain: %d %d/%d" % (damage, kill, self.damage_hull))
            
            firepower = 0
            
        self.update()
        self.fleet.update()
        
        if DEBUG: print ("damage: %d/%d" % (self.damage_hull, self.structure))
        
        return firepower, kill

    '''
    def hit(self, damage):
        
        kill = 0
        
        if damage >= self.structure + self.resistance:
            kill = self.effectif
            self.effectif = 0
            self.damage_hull = 0
            self.damage_shield = 0
            firepower = damage - (self.structure + self.resistance)
        else:
            if damage > self.shield - self.damage_shield:
                
                defense = (self.structure + self.resistance) - damage
                effectif = math.ceil(defense / (self.hull + self.shield))
                kill = self.effectif - effectif
                self.effectif = effectif
                
                remain = damage - (kill * (self.hull + self.shield))
                
                if remain:
                    if remain > self.shield:
                        self.damage_hull += (remain - self.shield)
                        self.damage_shield = 0
                    else:
                        self.damage_shield += (self.shield - remain)
                        
                if DEBUG: print ("kill/remain: %s/%s" % (kill, remain))
            else:
                self.damage_shield += damage
                
            firepower = 0
            
        self.update()
        self.fleet.update()
        
        if DEBUG: print ("damage: %s/%s" % (self.damage_hull, self.structure))
        
        return firepower, kill
    '''
    
    def addKill(self, shipid, kill):
        
        if shipid in self.kill:
            kill = self.kill[shipid] + kill
        self.kill.update({shipid : kill})
        

Battleship = {}

class Battle():
    
    def __init__(self):
        
        self.fleets = []
        self.initiative()
        
    def addFleet(self, owner, fleet):
        f = Fleet(owner, fleet)
        if DEBUG: print ("Flotte %s: %d" % (f.owner, f.signature))
        self.fleets.append(f)
        
    def initiative(self):
        
        self._initiative = {}
        
        for shipid, ship in sorted(Ships.items()):
            cadence = ship[0]
            c = 1 / cadence
            for t in range(cadence):
                i = c * (t + 1)
                if i in self._initiative:
                    liste = self._initiative[i]
                else:
                    liste = []
                liste.append(shipid)
                self._initiative.update({i : liste})
        
    def do(self):
        
        self.rounds = 1
        
        if DEBUG: print ("Fight !")

        while True:
            
            if DEBUG: print ("Round %d" % self.rounds)
            
            for t, ships in sorted(self._initiative.items()):
                random.shuffle(ships)
                for shipid in ships:
                    if shipid in Battleship:
                        fleets = Battleship[shipid]
                        random.shuffle(fleets)
                        for fleet in fleets:
                            ship = fleet.fleet[shipid]
                            self.fight(ship)
                            
                            if DEBUG: print ()
                            
                            if self.victory():
                                report = self.hitcount()
                                return report
            '''
            for shipid, fleets in sorted(Battleship.items()):
                random.shuffle(fleets)
                for fleet in fleets:
                    
                    ship = fleet.fleet[shipid]
                    self.fight(ship)
                    
                    if DEBUG: print ()
                    
                    if self.victory():
                        report = self.hitcount()
                        return report
            '''
            self.rounds += 1
            
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
        
        if DEBUG: print("%s (%d, %d)" % (Vaisseaux[attacker.shipid], attacker.effectif, attacker.firepower))
        
        for shipid in attacker.engagement:
            if defender.effectif(shipid):
                firepower, kill = defender.hit(shipid, attacker.firepower)
                attacker.addKill(shipid, kill)
                if DEBUG: print("\t%s (%d) %d" % (Vaisseaux[shipid], kill, firepower))
                if not firepower:
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
        
        report = "<br>"
        for opponent in self.fleets:
            report += ("Flotte %s (%d)" % (opponent.owner, opponent.signature))
            report += "<br><br>"
            for shipid, ship in sorted(opponent.fleet.items()):
                report += ("%s (%d)" % (ship.shipname, ship.effectif))
                report += "<br>"
                for idname, kill in sorted(ship.kill.items()):
                    if kill:
                        report += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                        report += ("%s (%d)" % (Vaisseaux[idname], kill))
                        report += "<br>"
            report += "<br>"
            
        report += ("en %d round(s)" % self.rounds)
        
        return (report)
    
if __name__ == '__main__':
    
    battle = Battle()
    battle.addFleet( 'A', [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] )
    battle.addFleet( 'B', [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] )
    #battle.addFleet( 'A', [5, 5, 5, 5, 5, 5, 2500, 250, 13675, 5, 3725, 0] )
    #battle.addFleet( 'B', [397, 371, 0, 211, 268, 205, 218, 684, 347, 376, 571, 0] )
    report = battle.do()
    
    print (report.replace("<br>", "\n").replace("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;", "\t"))
