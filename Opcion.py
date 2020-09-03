# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 10:24:15 2019

@author: Juyas
"""

from Carta import *

class Opcion(object):
    
    def __init__(self,baza,palot):
        self.bazas = baza
        self.palo = palot
        
    def getBazas(self):
        return self.bazas
    
    def getPalo(self):
        return self.palo
    
    def __repr__(self):
        return "("+ str(self.getBazas()) +"," + str(self.getPalo()) +")"
    
    def __eq__(self,otro):
        if otro == None:
            return False
        if otro.getPalo() == None:
            if self.getPalo() == None:
                return self.getBazas() == otro.getBazas()
            else:
                return False
        elif self.getPalo() == None:
            return False
        else:
            return self.getBazas() == otro.getBazas() and self.getPalo() == otro.getPalo()
    
class Subasta(object):
    def __init__(self,nombre,opcion):
        self.nombre = nombre
        self.opcion = opcion
        
    def getNombre(self):
        return self.nombre
    
    def getOpcion(self):
        return self.opcion
    
    def __repr__(self):
        return "("+ self.getNombre() +"," + repr(self.getOpcion()) +")"
    

def opcionACom(opcion):
    if opcion.getBazas() == 0:
        return 0
    if opcion.getPalo() == None:
        return opcion.getBazas() + 100
    return opcion.getBazas() + opcion.getPalo().value

def comAOpcion(com):
    if com == 0:
        return Opcion(0,None)
    if com <= 13:
        baza = Opcion(com,Palo.TREBOL)
        return baza
    if com <= 26:
        baza = Opcion(com-13,Palo.DIAMANTE)
        return baza
    if com <= 39:
        baza = Opcion(com-26,Palo.CORAZON)
        return baza
    if com <= 52:
        baza = Opcion(com-39,Palo.PICA)
        return baza
    return Opcion(com-100,None)

def opcionesACom(lista):
    array = [str(opcionACom(x)) for x in lista]
    com = '/'.join(array)
    return com

def comAOpciones(string):
    array = string.split('/')
    array = [comAOpcion(int(x)) for x in array]
    return array


def subastaACom(subasta):
    nombre = subasta.getNombre()
    opcion = str(opcionACom(subasta.getOpcion()))
    com = '_'.join([nombre,opcion])
    return com

def comASubasta(com):
    array = com.split("_")
    opcion = comAOpcion(int(array[1]))
    return Subasta(array[0],opcion)