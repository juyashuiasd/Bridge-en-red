# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 10:54:40 2019

@author: Juyas
"""

from Carta import *
from Jugador import *
from Baraja import *
from Equipo import *
from Opcion import *
import socket
import sys
from threading import Thread
import threading
import time

#=============================
#VARIABLES GLOBALES
#=============================

clients = []
arrayClienteJugador = []
equipo1 = None
equipo2 = None

#=============================
#VARIABLES GLOBALES
#=============================



#=============================
#VARIABLES SUBASTA
#=============================

subastaNorte = None
subastaSur = None
subastaOeste = None
subastaEste = None

def broadcast(msg):
    time.sleep(1)
    for client in clients:
        s = str.encode(msg)
        client.send(s)
        
def buscaCliente(nombre):
    client = [b for (a,b) in arrayClienteJugador if a.getNombre() == nombre]
    return client[0]

def recibeMensaje(conexion):
    com = conexion.recv(2014).decode()
    return com

def main():
    start_server()


def start_server():
    host = "127.0.0.1" #Conexión a localhost
    port = 8888
    conex = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conex.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("El socket ha sido creado")
    try:
        conex.bind((host, port))
    except:
        print("El binding ha fallado")
    
    modo_espera(conex)
    
def modo_espera(conex):
    conex.listen(4)      
    print("El socket está escuchando")
    while len(clients) < 4:
        connection, address = conex.accept()
        ip, port = str(address[0]), str(address[1])
        print("Conexión con " + ip + ":" + port)
        clients.append(connection)
    time.sleep(5)
    
    jugar(conex)
    
def jugar(conex):
    juego(conex)
    
def juego(conex):
    
    def creaJugadores():
        j1 = Jugador("Norte")
        j2 = Jugador("Este")
        j3 = Jugador("Sur")
        j4 = Jugador("Oeste")
        return j1,j2,j3,j4
    
    def distribuye(arrayJugador):
        baraja = Baraja()
        baraja.creaBaraja()
        baraja.barajarBaraja()
        for x in arrayJugador:
            x.devuelveCartas()
            x.recibirCartas(baraja)
            
    def enviaCartas(array):
        for a,b in arrayClienteJugador:
            com = nombrebarajaACom(a.getNombre(),a.getCartas())
            com = com + "|0"
            com = com.encode()
            b.send(com)
            
    def subasta(arrayJugador):
        
        def muestraOpciones(opcion):
            opciones = []
            for x in range(7,14):
                for y in Palo:
                    opciones.append(Opcion(x,y))
                opciones.append(Opcion(x,None))
            if opcion == None:
                return opciones
            else:
                index = opciones.index(opcion) + 1
                return opciones[index:]
            
        def mensajeApuesta(jugador,anteriorSubasta,maxSubasta):
            anteriorMSG,maxMSG = "",""
            variableMuestraOpciones = None
            if anteriorSubasta == None:
                anteriorMSG = subastaACom(Subasta("Nadie",Opcion(0,None)))
            else:
                anteriorMSG = subastaACom(anteriorSubasta)
            if maxSubasta == None:
                maxMSG = subastaACom(Subasta("Nadie",Opcion(0,None)))
            else:
                maxMSG = subastaACom(maxSubasta)
                variableMuestraOpciones = maxSubasta.getOpcion()
            com = '-'.join([jugador.getNombre(),opcionesACom(muestraOpciones(variableMuestraOpciones)),anteriorMSG,maxMSG])
            # Nombre del jugador - Opciones de Subasta - Subasta anterior - Subata Máxima
            return com
        
        def mensajeFIN(maxSubasta):
            com = '-'.join(["FIN2",subastaACom(maxSubasta)])
            return com
            
        maxSubasta = None
        anteriorSubasta = None
        while True:
            for x in arrayJugador:
                if  maxSubasta and maxSubasta.getNombre() == x.getNombre():
                    broadcast(mensajeFIN(maxSubasta))
                    return maxSubasta
                elif maxSubasta and (maxSubasta.getOpcion().getBazas() == 13 and maxSubasta.getOpcion().getPalo() == None):
                    broadcast(mensajeFIN(maxSubasta))
                    return maxSubasta
                else:
                    broadcast(mensajeApuesta(x,anteriorSubasta,maxSubasta))
                    time.sleep(1)
                    mensaje = int(recibeMensaje(buscaCliente(x.getNombre())))
                    
                        
                        
                    """POR HACER #########################################################"""
                    
                    if mensaje != 0:
                        maxSubasta = Subasta(x.getNombre(),comAOpcion(mensaje))
                        anteriorSubasta = Subasta(x.getNombre(),comAOpcion(mensaje))
                    else:
                        anteriorSubasta = Subasta(x.getNombre(),comAOpcion(0))
                        
            if maxSubasta == None:
                broadcast("REINICIA")
                return False
    def carteo(arrayJugador,subastaGanadora):
        
        def configuraEquipos(nombre):
            if equipo1.existeJugador(nombre):
                equipo1.actualizaRol(nombre)
            else:
                equipo2.actualizaRol(nombre)
                
        def getMuerto():
            if equipo1.ataque == True:
                return equipo1.muerto
            else:
                return equipo2.muerto
            
        def getEquipoAtaque():
            if equipo1.ataque == True:
                return equipo1
            else:
                return equipo2
        
        def muestraCarta(cartas):
            for x in cartas:
                print((x.getValor().name,x.getPalo().name))
                
        def turnoJugador(jugador,tabla,baza1,baza2):
            opciones = muestraOpciones(jugador,tabla)
            turno = jugador
            if jugador.nombre == getMuerto().nombre:
                turno = getEquipoAtaque().buscaContrario(jugador.getNombre())
                
            if not tabla:
                com = '-'.join([turno.getNombre(),jugador.getNombre(),barajaACom(opciones),barajaACom(getMuerto().getCartas()),"None",str(baza1),str(baza2),getMuerto().nombre])
            else:
                if getMuerto().getCartas():
                    com = '-'.join([turno.getNombre(),jugador.getNombre(),barajaACom(opciones),barajaACom(getMuerto().getCartas()),barajaACom(tabla),str(baza1),str(baza2),getMuerto().nombre])
                else:
                    com = '-'.join([turno.getNombre(),jugador.getNombre(),barajaACom(opciones),"None",barajaACom(tabla),str(baza1),str(baza2),getMuerto().nombre])

            # Turno JUGADOR (JUEGA) - Turno Jugador (MUERTO) - Opciones - Cartas Muerto - Tablero - baza1 - baza2 - nombreMuerto
            broadcast(com)
            carta = creaCarta(opciones,jugador)
            jugador.sacaCarta(carta)
            return carta
                
        def creaCarta(opciones,jugador):
            if jugador == getMuerto():
                jugador = getEquipoAtaque().buscaContrario(jugador.getNombre())
            mensaje = int(recibeMensaje(buscaCliente(jugador.getNombre())))
            carta = comACarta(mensaje)
            return carta 
        
        def muestraOpciones(j,tablero):
            
            def existeCarta(pC,cJ):
                return [x for x in cJ if pC.getPalo().value == x.getPalo().value]
            
            if not tablero:
                return j.mano
            else:
                aux = existeCarta(tablero[0],j.mano)
                if not aux:
                    return j.mano
                else:
                    return aux
            
        def ganarBaza(tablero,arrayJugador,triunf):
                
            def filtra(tabla,palo):
                return [x for x in tabla if palo == None or x.getPalo().value == palo.value]
            
            def devuelveCartaGanadora(lista):
                lista.sort(key=lambda x: x.getValor().value)
                return lista[-1]
                
                    
            def devuelveGanador(tablo,cartaGanar):
                return tablo.index(cartaGanar)
                
            aux1 = filtra(tablero,triunf)
            if aux1:
                ganador = devuelveCartaGanadora(aux1)
                return devuelveGanador(tablero,ganador)
            aux1 = filtra(tablero,tablero[0].getPalo())
            ganador = devuelveCartaGanadora(aux1)
            return devuelveGanador(tablero,ganador)
        
        def sumaBaza(ganador):
            global equipo1
            if equipo1.existeJugador(ganador.nombre):
                return equipo1.sumaBazas()
            else:
                return equipo2.sumaBazas()
        
        def finTurno(tablero):
            
            string = '-'.join(["FINT",barajaACom(tablero)])
            broadcast(string)
            
            
        turno = 1
        subastaCarteo = subastaGanadora
        configuraEquipos(subastaCarteo.getNombre())
        while turno != 14:
            tablero = []
            for x in arrayJugador:
                carta = turnoJugador(x,tablero,equipo1.getBazasEquipo(),equipo2.getBazasEquipo())
                tablero.append(carta)
            finTurno(tablero)
            time.sleep(5)
            index = ganarBaza(tablero,arrayJugador,subastaCarteo.getOpcion().getPalo())
            sumaBaza(arrayJugador[index])
            arrayJugador = desplazaJugadores(arrayJugador,arrayJugador[index].getNombre(),1)
            turno +=1
        broadcast("-".join(["FIN2",str(equipo1.getBazasEquipo()),str(equipo2.getBazasEquipo())]))
            
    j1,j2,j3,j4 = creaJugadores()
    arrayJugador = [j1,j2,j3,j4]
    for i in range(0,4):
        arrayClienteJugador.append((arrayJugador[i],clients[i]))
    global equipo1, equipo2
    equipo1 = Equipo(arrayJugador[0::2])
    equipo2 = Equipo(arrayJugador[1::2])
    ronda = 1
    while ronda != 4:
        subastaGanadora = False
        while subastaGanadora == False:
            distribuye(arrayJugador)
            broadcast("INICIALIZA")
            enviaCartas(arrayJugador)
            broadcast("SUBASTA")
            subastaGanadora = subasta(arrayJugador)
        broadcast("CARTEO")
        arrayJugador = desplazaJugadores(arrayJugador,subastaGanadora.getNombre(),2)
        carteo(arrayJugador,subastaGanadora)
        puntuaEquipos(subastaGanadora)
        enviaPuntos()
        equipo1.reinicia()
        equipo2.reinicia()
        ronda += 1
    time.sleep(3)
    broadcast("FINALIZAR")
    time.sleep(15)
    conex.close()
    
def enviaPuntos():
    global equipo1
    time.sleep(1)
    puntos = equipo1.getPuntuacion()
    stringP = str(puntos)
    broadcast(stringP)
    
    
def puntuaEquipos(subastaGanadora):
    
    def bonificacionesTriunfo(palo):
        triunfo,bonificacionST = 0,0
        if not palo == None and palo.value < 20:
            triunfo,bonificacionST = 20, 0
        elif not palo == None:
            triunfo,bonificacionST = 30, 0
        else:
            triunfo,bonificacionST = 30, 10
        return triunfo,bonificacionST
    
    def bonificacionesImportancia(bazas,sumaA):
        suma = 0
        if bazas - 6 == 7:
            suma += 1300
        if bazas - 6 == 6:
            suma += 800
        if sumaA > 100: 
            suma += 300
        if sumaA < 100:
            suma += 50
        return suma
    
    def puntua(opcion,bazas):
        if opcion.getBazas() > bazas: #Fallo
            return (-1) * 50 * (opcion.getBazas()-bazas)
        else:
            triunfo,bonificacionST = bonificacionesTriunfo(opcion.getPalo())
            suma1 = opcion.getBazas() * triunfo + bonificacionST
            suma2 = (bazas - opcion.getBazas()) * triunfo
            importancia = bonificacionesImportancia(opcion.getBazas(),suma2)
            sumaTotal = suma1 + suma2 + importancia
            return sumaTotal
    
    if equipo1.existeJugador(subastaGanadora.getNombre()):
        puntos = puntua(subastaGanadora.getOpcion(),equipo1.getBazasEquipo())
        equipo1.sumaPuntuacion(puntos)
        equipo2.sumaPuntuacion((-1)*puntos)
    else:
        puntos = puntua(subastaGanadora.getOpcion(),equipo2.getBazasEquipo())
        equipo2.sumaPuntuacion(puntos)
        equipo1.sumaPuntuacion((-1)*puntos)
    
def desplazaJugadores(array,triunfo,index):
    arrayAux = array.copy()
    while True:
        if [x.getNombre() for x in arrayAux].index(triunfo) == (index-1):
            return arrayAux
        else:
            arrayAux = arrayAux[1:]+arrayAux[:1]
            

if __name__ == "__main__":
    main()