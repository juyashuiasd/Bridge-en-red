# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 18:35:19 2019

@author: Juacarleo
"""

from enum import Enum

class Carta(object):
    
    def __init__(self,valor,palo):
        self.valor = valor;
        self.palo = palo;
        self.com = cartaACom2(valor,palo)
        
    def getValor(self):
        return self.valor
    
    def getPalo(self):
        return self.palo
    
    def getCom(self):
        return self.com
    
    def __eq__(self,other):
        return self.getCom() == other.getCom()
 
    def __repr__(self):
        return "("+repr(self.getValor().value)+","+repr(self.getPalo().name)+")"

def cartaACom2(valor,palo):
    return valor.value - 1 + palo.value

def cartaACom(carta):
    return carta.getValor().value - 1 + carta.getPalo().value
    
def comACarta(com):
    if com <= 13:
        carta = Carta(Identificador(com - Palo.TREBOL.value + 1),Palo.TREBOL)
        return carta
    if com <= 26:
        carta = Carta(Identificador(com - Palo.DIAMANTE.value + 1),Palo.DIAMANTE)
        return carta
    if com <= 39:
        carta = Carta(Identificador(com - Palo.CORAZON.value + 1),Palo.CORAZON)
        return carta
    if com <= 52:
        carta = Carta(Identificador(com - Palo.PICA.value + 1),Palo.PICA)
        return carta
    
def barajaACom(lista):
    array = [str(x.getCom()) for x in lista]
    com = '/'.join(array)
    return com

def comABaraja(string):
    array = string.split('/')
    array = [comACarta(int(x)) for x in array]
    return array

def nombrebarajaACom(nombre,baraja):
    string = barajaACom(baraja)
    string = '-'.join([nombre,string])
    return string

def comANombrebaraja(string):
    array = string.split('-')
    arrayBaraja = comABaraja(array[-1])
    return array[0],arrayBaraja    
    
class Palo(Enum):
    _order_ = 'TREBOL DIAMANTE CORAZON PICA'
    
    TREBOL = 0
    DIAMANTE = 13
    CORAZON = 26
    PICA = 39
    
class Identificador(Enum):
    DOS = 2
    TRES = 3
    CUATRO = 4
    CINCO = 5
    SEIS = 6
    SIETE = 7
    OCHO = 8
    NUEVE = 9
    DIEZ = 10
    JACK = 11
    REINA = 12
    REY = 13
    AS = 14