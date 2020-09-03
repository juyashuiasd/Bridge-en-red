# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 18:41:03 2019

@author: Juacarleo
"""
from Carta import *
import random

class Baraja(object):
    
    def __init__(self,cartas = []):
        self.cartas=cartas
        
    def creaBaraja(self):
        baraja = []
        for palo in Palo:
            for id in Identificador:
                CartaAux = Carta(id,palo)
                baraja.append(CartaAux)
        self.cartas = baraja
        
    def barajarBaraja(self):
        random.shuffle(self.cartas)
        
    def reparteCarta(self):
        if not self.cartas:
            print("Cuidado que no hay cartas en la baraja")
            return None
        reparto = self.cartas[0:13]
        self.cartas = self.cartas[13:]
        return reparto
    
    def cartaPuedeGanar(self,carta,arrayCartas):
        palo = carta.getPalo()
        lista = [x for x in self.cartas if x.getPalo().value == palo.value and x not in arrayCartas]
        for x in lista:
            if x.getValor().value > carta.getValor().value:
                return False
        return True