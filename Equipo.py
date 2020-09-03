# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 10:17:28 2019

@author: Juyas
"""

from Jugador import *
class Equipo(object):
    
    def __init__(self,jugadores):
        self.jugador1 = jugadores[0]
        self.jugador2 = jugadores[-1]
        self.ataque = False
        self.bazas = 0
        self.puntuacion = 0
        
        self.declarante = None
        self.muerto = None
        
    def existeJugador(self,nombre):
        if self.jugador1.nombre == nombre:
            return True
        elif self.jugador2.nombre == nombre:
            return True
        else:
            return False
        
    def buscaContrario(self,nombre):
        if self.jugador1.nombre == nombre:
            return self.jugador2
        else:
            return self.jugador1
        
    def reinicia(self):
        self.ataque = False
        self.bazas = 0
        self.declarante = False
        self.muerto = False
        
    def sumaBazas(self):
        self.bazas += 1
        
    def sumaPuntuacion(self,puntos):
        self.puntuacion += puntos
        
    def actualizaRol(self,declarante):
        self.ataque = True
        if self.jugador1.nombre == declarante:
            self.declarante = self.jugador1
            self.muerto = self.jugador2
        else:
            self.declarante = self.jugador2
            self.muerto = self.jugador1
            
    def getBazasEquipo(self):
        return self.bazas
    
    def getPuntuacion(self):
        return self.puntuacion
        