# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 18:37:14 2019

@author: Juacarleo
"""

class Jugador(object):
    
    def __init__(self,nombre,mano=[],ai = False):
        self.nombre=nombre
        self.mano=mano
        
    def getNombre(self):
        return self.nombre
    
    def getCartas(self):
        return self.mano
        
    def recibirCartas(self,baraja):
        if len(self.mano) == 13:
           return None 
        reparto = baraja.reparteCarta()
        reparto.sort(key=lambda x: (x.getPalo().value,x.getValor().value))
        self.mano = reparto
        
    def devuelveCartas(self):
        self.mano=[]
        
    def sacaCarta(self,carta):
        self.mano.remove(carta)
        
    def muestraCartas(self):
        for x in self.mano:
            print((x.getValor().name,x.getPalo().name))
            
    def __repr__(self):
        return self.nombre