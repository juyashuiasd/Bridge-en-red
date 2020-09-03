# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 12:38:56 2019

@author: Juyas
"""

from Carta import *
from Jugador import *
from Baraja import *
from Equipo import *
from Opcion import *
import socket
import threading
import time

from tkinter import *    # Carga módulo tk (widgets estándar)
import tkinter.font as font
from tkinter import ttk  # Carga ttk (para widgets nuevos 8.5+)

#=============================
#VARIABLES GLOBALES
#=============================
lock = threading.Lock()
comunicador = None




nombre = ""
mano = []
subasta = 0
dic1 = {}
dic2 = {}
ia = 1
puntuacionEquipo1 = 0
puntuacionEquipo2 = 0
ronda = 1

dicFunc = ["SALIR","MODOESPERA","SUBASTA","INICIALIZA","REINICIA","CARTEO","FINALIZAR"]

#=============================
#VARIABLES DE RED
#=============================

conex = None
host = "127.0.0.1"
port = 8888

#=============================
#VARIABLES DE SUBASTA
#=============================

maximo = "Ninguna"
nombremaximo = "Ninguna"
anterior = "Ninguna"
maxNorte = Opcion(0,None)
maxSur= Opcion(0,None)
maxEste = Opcion(0,None)
maxOeste = Opcion(0,None)
subastaTrue = True

#=============================
#VARIABLES DE CARTEO
#=============================

triunfo = None
nombretriunfo = None
turnoAnterior = None
cartaNorte = None
cartaEste = None
cartaSur = None
cartaOeste = None
dicTablero = {}
dicMuerto = {}
dicPropias = {}
dicPropiasNo = {}
dicMuertoNo = {}

#=============================
#VARIABLES DE IA
#=============================

cartasJugadas = []
jugadaEspecial = []
baraja = None


#=============================
#JUEGO
#=============================



class Window(object):
    
    def __init__(self):
        
        
        self.root = Tk()
        self.root.geometry(("1280x720"))
        self.root.title("Bridge")
        self.root.configure(bg = '#00AA39')
        self.frameIni = Frame(self.root)
        self.frameIni.pack()
        t1 = threading.Thread(target=self.frameInicio, args=[])
        t1.start()
        self.root.mainloop()
        
    def frameInicio(self):
            
        global host, port, conex
        self.frameIni.destroy()
        self.frameGame = False
        conex = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conex.connect((host, port))
        except:
            print("Connection error")
            sys.exit()
        self.funcionesCliente("MODOESPERA")
        
    def modoEspera(self):
        global conex
        com = recibeMensaje(conex)
        self.funcionesCliente(com)
        
    def inicializa(self):
        global conex, nombre, mano, ia
        com = recibeMensaje(conex)
        array = com.split("|")
        nombre, mano = comANombrebaraja(array[0])
        self.funcionesCliente("MODOESPERA")
        
    def subasta(self):
    
        def mensajeFin(strMsg):
            if strMsg == "REINICIA":
                return True
            if "FIN2" in strMsg:
                return True
            return False
        
    
        def ejecutaMensaje(strMsg):
            global comunicador,ia, maximo,nombremaximo
            array = strMsg.split('-')
            nombreTurno = array[0]
            
            if strMsg == "REINICIA":
                return 0
            opcionesSubasta = array[1] #Cuando FINT apuesta máxima
            if nombreTurno == "FIN2":
                maximoS = comASubasta(opcionesSubasta)
                maximo = maximoS.getOpcion()
                nombremaximo= maximoS.getNombre()
                return 0
            
            subastaAnterior = array[2]
            subastaMaxima = array[3]
            
            self.borraSubasta()
            self.imprimeSubasta()
            self.imprimeBaraja(nombreTurno)
            self.imprimeDatosS(nombreTurno,comASubasta(subastaAnterior))
            if nombreTurno == nombre:
                if ia == 0:
                    self.imprimeOpciones(opcionesSubasta)
                    while not comunicador:
                        pass
                    enviaMensaje(conex,comunicador)
                    comunicador = None
                else:
                    self.imprimeOpciones(opcionesSubasta)
                    comunicador = subasta(opcionesSubasta)
                    time.sleep(1)
                    enviaMensaje(conex,comunicador)
                    comunicador = None
        
        
        reiniciaSubasta()
        mensaje = ""
        while not mensajeFin(mensaje):
            mensaje = recibeMensaje(conex)
            
            ejecutaMensaje(mensaje)
            if mensaje == "REINICIA":
                self.funcionesCliente("REINICIA")
            if "FIN2" in mensaje:
                self.funcionesCliente("REINICIA")
    
    def funcionesCliente(self,funcion):
        global dicFunc
        index = dicFunc.index(funcion)
        if index == 0:
            return 0
        if index == 1:
            self.modoEspera()
        if index == 2:
            self.subasta()
        if index == 3:
            self.inicializa()
        if index == 4:
            self.modoEspera()
        if index == 5:
            self.carteo()
        if index == 6:
            self.finalizar()
            
    def borraSubasta(self):
        if self.frameGame:
            self.frameGame.destroy()
        
    def imprimeSubasta(self):
        self.frameGame = Frame(self.root)
        self.gameCanvas = Canvas(self.frameGame,width=1280,height=720,bg='#00AA39')
        self.frameGame.pack()
        self.gameCanvas.pack()
        self.gameCanvas.create_rectangle(430,112,711,163,fill='#CECACA')
        self.gameCanvas.create_rectangle(100,217,400,462, fill='#CECACA')
        self.gameCanvas.create_rectangle(740,217,1040,462, fill='#CECACA')
        self.gameCanvas.create_rectangle(430,472,711,523, fill='#CECACA')
        self.imprimeGenerales()
        self.frameDerecha()
        
    def modificaIA(self):
        global ia
        ia = not ia
        self.labelIAMOD.destroy()
        stringTrue = "IA: "+repr(bool(ia))
        self.labelIAMOD=ttk.Label(self.frameGame, text = stringTrue, font = "Verdana 13", background='#8E551C')
        self.labelIAMOD.place(x= 1100 ,y = 150, in_=self.frameGame)
        
        
    def imprimeDatosS(self,nombre,anteriorSub):
        
        def imprimeDato():
            
            stringN = "Equipo 1:\n\nNorte: "+repr(maxNorte)+"\n\nSur: "+repr(maxSur)
            self.label=ttk.Label(self.frameGame, text = stringN, font = "Verdana 13", background='#CECACA')
            self.label.place(x= 115 ,y = 230, in_=self.frameGame)
            stringE = "Equipo 2:\n\nEste: "+repr(maxEste)+"\n\nOeste: "+repr(maxOeste)
            self.label=ttk.Label(self.frameGame, text = stringE, font = "Verdana 13", background='#CECACA')
            self.label.place(x= 755 ,y = 230, in_=self.frameGame)
            stringA = "Anterior: "+repr(anterior)
            self.label=ttk.Label(self.frameGame, text = stringA, font = "Verdana 13", background='#CECACA')
            self.label.place(x= 440 ,y = 125, in_=self.frameGame)
            stringM = "Máxima: "+repr(maximo)
            self.label=ttk.Label(self.frameGame, text = stringM, font = "Verdana 13", background='#CECACA')
            self.label.place(x= 440 ,y = 485, in_=self.frameGame)
            
            
            
        global maximo, anterior, maxNorte, maxSur, maxEste, maxOeste, nombremaximo
        nombreA = anteriorSub.getNombre()
        if nombreA == "Nadie":
            return imprimeDato()
        subastaA = anteriorSub.getOpcion()
        anterior = subastaA
        if not opcionACom(subastaA) == 0:
            maximo = subastaA
            nombremaximo = nombreA
            if nombreA == "Oeste":
                maxOeste = subastaA
            elif nombreA == "Este":
                maxEste = subastaA
            elif nombreA == "Norte":
                maxNorte = subastaA
            elif nombreA == "Sur":
                maxSur = subastaA
        return imprimeDato()
            
        
        
    def imprimeBaraja(self,turno):
        
        global mano, dic2
        a = 50 + 40 * (13-len(mano))
        for i in range(len(mano)):
            self.label=ttk.Label(self.frameGame)
            string = str(mano[i].getCom())
            photo=PhotoImage(file=".\\images\\cards\\"+string+"b.png", master= self.frameGame)
            dic2[i]=photo
            self.label.config(image=dic2[i])
            self.label.place(x=a,y = 605, in_=self.frameGame)
            a += 80
            
    def imprimeOpciones(self,array):
        
        
        self.frameOpciones = Frame(self.frameGame,width= 278 ,height = 242,bg="#00AA39")
        self.frameOpciones.place(x = 425, y = 165)
        arrayOpciones = comAOpciones(array)
        x = [repr(y) for y in arrayOpciones]
        a = 440
        y = 230
        
        s = ttk.Style()
        s.configure('my.TButton', font=('Helvetica', 7),background = '#00AA39')
        
        for i in range(len(arrayOpciones)):
            string = opcionACom(arrayOpciones[i])
            self.botonO = ttk.Button(self.frameOpciones, text=arrayOpciones[i], style='my.TButton', command = lambda j = string : self.devuelveNumero(j))
            self.botonO.grid(row=i//3,column=i%3,sticky="ew")
        self.botonO=ttk.Button(self.frameOpciones, text="Pasar", style='my.TButton', command = lambda : self.devuelveNumero(opcionACom(Opcion(0,None))))
        self.botonO.grid(sticky="ew")
    
    def devuelveNumero(self,opcion):
        
        com =  str(opcion)
        self.imprimeComunicacion(com)
        
    def imprimeComunicacion(self,string):
        global comunicador
        comunicador = string
        
    def carteo(self):
        
        global maximo, triunfo, nombremaximo, nombretriunfo, cartasJugadas
        
        
    
        def mensajeFin(strMsg):
            if "FIN2" in strMsg:
                return True
            return False
    
        def ejecutaMensaje(strMsg):
            global mano, comunicador, cartasJugadas, ronda
            array = strMsg.split("-")
            nombreJugador = array[0] #FIN2 O FINT
            nombreTurno = array[1] #Bazas equipo 1 al FIN2 o Tablero FINT
            
        
            if nombreJugador == "FIN2":
                global puntuacionEquipo1, puntuacionEquipo2
                
                mensaje = recibeMensaje(conex)
                puntos = int(mensaje)
                puntuacionEquipo1 = puntos
                puntuacionEquipo2 = (-1) * puntos
                ronda += 1
                return 0
        
            if nombreJugador == "FINT":
                self.imprimeTablero(comABaraja(nombreTurno),None)
                cartasJugadas += comABaraja(nombreTurno)
                time.sleep(3)
                self.reinicioVariables()
                return 0
            self.borraCarteo()
            self.imprimeCarteo()
            opcionesJugador = array[2] 
            cartasMuerto = array[3]
            cartasTablero = array[4]
            bazasEquipo1 = array[5]
            bazasEquipo2 = array[6]
            nombreMuerto = array[7]
            if cartasTablero == "None":
                self.imprimeTablero(None,nombreTurno)
            else:
                self.imprimeTablero(comABaraja(cartasTablero),nombreTurno)
            
            if cartasMuerto == "None":
                self.imprimeMuerto(None,nombreJugador,nombreTurno,None)
            else:
                self.imprimeMuerto(comABaraja(cartasMuerto),nombreJugador,nombreTurno,comABaraja(opcionesJugador))
            self.imprimePropias(mano,nombreJugador,nombreTurno,comABaraja(opcionesJugador),nombreMuerto)
            
            self.imprimeDatosC(bazasEquipo1,bazasEquipo2,nombreTurno)
                
            
            if array[0] == nombre:
                if ia == 0:
                    while not comunicador:
                        pass
                    mano = [x for x in mano if int(comunicador) != x.getCom()]
                    enviaMensaje(conex,comunicador)
                    comunicador = None
                else:
                    comunicador = carteoAI(opcionesJugador,cartasTablero,cartasMuerto)
                    time.sleep(1)
                    mano = [x for x in mano if int(comunicador) != x.getCom()]
                    enviaMensaje(conex,comunicador)
                    comunicador = None
                    
        
        triunfo = maximo
        nombretriunfo = nombremaximo
        mensaje = ""
        cartasJugadas = []
        while not mensajeFin(mensaje):
            mensaje = recibeMensaje(conex)
            ejecutaMensaje(mensaje)
        if "FIN2" in mensaje:
            self.funcionesCliente("REINICIA")
            
    def borraCarteo(self):
        if self.frameGame:
            self.frameGame.destroy()
            
    def imprimeCarteo(self):

        self.frameGame = Frame(self.root)
        self.gameCanvas = Canvas(self.frameGame,width=1280,height=720,bg='#00AA39')
        self.frameGame.pack()
        self.gameCanvas.pack()
        self.gameCanvas.create_rectangle(430,157,711,208,fill='#CECACA')
        self.gameCanvas.create_rectangle(430,217,711,462)
        self.gameCanvas.create_rectangle(100,217,400,462, fill='#CECACA')
        self.gameCanvas.create_rectangle(740,217,1040,462, fill='#CECACA')
        self.gameCanvas.create_rectangle(430,472,711,523, fill='#CECACA')
        self.imprimeGenerales()
    
    def imprimeDatosC(self,be1,be2,turno):
        
        def imprimeDato(st1,st2,re1,b1,b2):
            
            
            stringTu = "Turno: "+repr(turno)
            self.label=ttk.Label(self.frameGame, text = stringTu, font = "Verdana 13", background='#CECACA')
            self.label.place(x= 440 ,y = 175, in_=self.frameGame)
            if triunfo.getPalo() == None:
                stringTR = "Triunfo: Ninguno"
            else:
                stringTR = "Triunfo: "+repr(triunfo.getPalo())
            self.label=ttk.Label(self.frameGame, text = stringTR, font = "Verdana 12", background='#CECACA')
            self.label.place(x= 440 ,y = 485, in_=self.frameGame)
            stringE1 = repr(st1)
            self.label=ttk.Label(self.frameGame, text = stringE1, font = "Verdana 13", background='#CECACA')
            self.label.place(x= 115 ,y = 230, in_=self.frameGame)
            stringE2 = repr(st2)
            self.label=ttk.Label(self.frameGame, text = stringE2, font = "Verdana 13", background='#CECACA')
            self.label.place(x= 755 ,y = 230, in_=self.frameGame)
            if re1:
                restantes = triunfo.getBazas() - int(b1)
                if restantes < 0:
                    restantes = "0"
                else:
                    restantes = str(restantes)
                stringb1 = "Ganadas: "+repr(b1) + " \n\n" + "Restantes: " + repr(restantes)
                self.label=ttk.Label(self.frameGame, text = stringb1, font = "Verdana 13", background='#CECACA')
                self.label.place(x= 115 ,y = 277, in_=self.frameGame)
                stringb2 = "Ganadas: "+repr(b2)
                self.label=ttk.Label(self.frameGame, text = stringb2, font = "Verdana 13", background='#CECACA')
                self.label.place(x= 755 ,y = 277, in_=self.frameGame)
            else:
                restantes = triunfo.getBazas() - int(b2)
                if restantes < 0:
                    restantes = "0"
                else:
                    restantes = str(restantes)
                stringb1 = "Ganadas: "+repr(b1)
                self.label=ttk.Label(self.frameGame, text = stringb1, font = "Verdana 13", background='#CECACA')
                self.label.place(x= 115 ,y = 277, in_=self.frameGame)
                stringb2 = "Ganadas: "+repr(b2) + " \n\n" + "Restantes: " + repr(restantes)
                self.label=ttk.Label(self.frameGame, text = stringb2, font = "Verdana 13", background='#CECACA')
                self.label.place(x= 755 ,y = 277, in_=self.frameGame)
            
        global triunfo, nombretriunfo
        
        if nombretriunfo == "Norte" or nombretriunfo == "Sur":
            stringE1 = "Equipo 1: Atacante"
            stringE2 = "Equipo 2: Defensor"
            restanteE1 = True
        else:
            stringE1 = "Equipo 1: Defensor"
            stringE2 = "Equipo 2: Atacante"
            restanteE1 = False
        imprimeDato(stringE1,stringE2,restanteE1,be1,be2)
        
    def imprimeTablero(self,tablero, turno):
        
        def imprimeCarta(carta):
            
            global turnoAnterior, cartaNorte, cartaOeste, cartaSur, cartaEste, dicTablero
            
            string = str(carta.getCom())
            photo=PhotoImage(file=".\\images\\cards\\"+string+".png", master= self.frameGame)
            if turnoAnterior == "Norte":
                dicTablero["Norte"] = photo
                cartaNorte = True
            elif turnoAnterior == "Sur":
                dicTablero["Sur"] = photo
                cartaSur = True
            elif turnoAnterior == "Este":
                dicTablero["Este"] = photo
                cartaEste = True
            elif turnoAnterior == "Oeste":
                dicTablero["Oeste"] = photo
                cartaOeste = True
            
        global turnoAnterior, cartaNorte, cartaOeste, cartaSur, cartaEste, dicTablero
        
        if not tablero:
            turnoAnterior = turno
        else:
            imprimeCarta(tablero[-1])
            turnoAnterior = turno
            
            if cartaNorte:
            
                self.labelN = Label(self.frameGame)
                self.labelN.config(image=dicTablero["Norte"])
                self.labelN.place(x=530,y = 227, in_=self.frameGame)
            
            if cartaOeste:
                self.labelO = Label(self.frameGame)
                self.labelO.config(image=dicTablero["Oeste"])
                self.labelO.place(x=440,y = 280, in_=self.frameGame)
            
            if cartaSur:
                self.labelS = Label(self.frameGame)
                self.labelS.config(image=dicTablero["Sur"])
                self.labelS.place(x=530,y = 344, in_=self.frameGame)
            
            if cartaEste:
                self.labelE = Label(self.frameGame)
                self.labelE.config(image=dicTablero["Este"])
                self.labelE.place(x=620,y = 280, in_=self.frameGame)
             
        self.frameDerecha()
                
            
    def reinicioVariables(self):
        global turnoAnterior, cartaNorte, cartaOeste, cartaSur, cartaEste, dicTablero
        dicTablero = {}
        cartaNorte = None
        cartaSur = None
        cartaOeste = None
        cartaEste = None
        
        
    def imprimeMuerto(self,baraja, nombreJugador, nombreMuerto, opciones):
        
        global nombre
        
        if baraja:
            
            if nombreJugador == nombre and nombreJugador != nombreMuerto:
                
                a = 50 + 40 * (13-len(baraja))
                for i in range(len(baraja)):
                    string = str(baraja[i].getCom())
                    photo=PhotoImage(file=".\\images\\cards\\"+string+".png", master= self.frameGame )
                    photoN=PhotoImage(file=".\\images\\cards\\"+string+"b.png", master= self.frameGame )
                    dicMuerto[i]=photo
                    dicMuertoNo[i]=photoN
                    if baraja[i] in opciones:
                        self.buttonM=ttk.Button(self.frameGame,text=string , command = lambda j = string : self.devuelveNumero(j) )
                        self.buttonM.config(image=dicMuerto[i])
                        self.buttonM.place(x=a,y = 0, in_=self.frameGame)
                    else:
                        self.labelM=ttk.Label(self.frameGame,text=string)
                        self.labelM.config(image=dicMuertoNo[i])
                        self.labelM.place(x=a,y = 0, in_=self.frameGame)
                    a += 80
                
            else:
                
                a = 50 + 40 * (13-len(baraja))
                for i in range(len(baraja)):
                    string = str(baraja[i].getCom())
                    photo=PhotoImage(file=".\\images\\cards\\"+string+"b.png", master= self.frameGame)
                    dicMuertoNo[i]=photo
                    self.labelM=ttk.Label(self.frameGame,text=string)
                    self.labelM.config(image=dicMuertoNo[i])
                    self.labelM.place(x=a,y = 0, in_=self.frameGame)
                    a += 80
                    
    def imprimePropias(self,baraja, nombreJugador, nombreMuerto, opciones, nombreMuertoX):
        
        global nombre
        
        if baraja:
            
            
            if nombreJugador == nombre and nombreJugador == nombreMuerto:
                
                a = 50 + 40 * (13-len(baraja))
                for i in range(len(baraja)):
                    string = str(baraja[i].getCom())
                    photo=PhotoImage(file=".\\images\\cards\\"+string+".png", master= self.frameGame)
                    photoN=PhotoImage(file=".\\images\\cards\\"+string+"b.png", master= self.frameGame)
                    dicPropias[i]=photo
                    dicPropiasNo[i]=photoN
                    if baraja[i] in opciones:
                        self.buttonM=ttk.Button(self.frameGame,text=string, command = lambda j = string : self.devuelveNumero(j))
                        self.buttonM.config(image=dicPropias[i])
                        self.buttonM.place(x=a,y = 605, in_=self.frameGame)
                    else:
                        self.labelM=ttk.Label(self.frameGame,text=string)
                        self.labelM.config(image=dicPropiasNo[i])
                        self.labelM.place(x=a,y = 605, in_=self.frameGame)
                    a += 80
            elif nombre == nombreMuertoX:
                pass
            else:
                
                a = 50 + 40 * (13-len(baraja))
                for i in range(len(baraja)):
                    string = str(baraja[i].getCom())
                    self.labelM=ttk.Label(self.frameGame,text=string)
                    photo=PhotoImage(file=".\\images\\cards\\"+string+"b.png", master= self.frameGame)
                    dicPropiasNo[i]=photo
                    self.labelM.config(image=dicPropiasNo[i])
                    self.labelM.place(x=a,y = 605, in_=self.frameGame)
                    a += 80
                    
    def finalizar(self):
        
        global conex, puntuacionEquipo1,puntuacionEquipo2
        
        p1 =  puntuacionEquipo1
        p2 = puntuacionEquipo2
        self.frameGame.destroy()
        self.frameGame = Frame(self.root)
        self.gameCanvas = Canvas(self.frameGame,width=1280,height=720,bg='#00AA39')
        self.frameGame.pack()
        self.gameCanvas.pack() 
        string = ""
        if p1 > p2:
            string = "Gana el equipo 1 con: " + str(p1) + "\nPierde el equipo 2 con: " + str(p2)
        elif p2 > p1:
            string = "Pierde el equipo 1 con: " + str(p1) +"\nGana el equipo 2 con: " + str(p2)
        else:
                tring = "Empatan los dos equipos con: " + str(p1)
        self.labelF=ttk.Label(self.frameGame,text=string,font = "Verdana 20", background='#00AA39')
        self.labelF.place(x=500,y = 300, in_=self.frameGame)
        s = ttk.Style()
        s.configure('my.TButton', font=('Helvetica', 10),background = '#00AA39')
        self.buttonExit=ttk.Button(self.frameGame,text= "Pulsa aquí para salir", style='my.TButton', command = lambda : self.cierra(conex) )
        self.buttonExit.place(x=600,y = 440, in_=self.frameGame)
        conex.close()
        
    def imprimeGenerales(self):
            
        global nombre, puntuacionEquipo1, puntuacionEquipo2, dato
            
        
        self.gameCanvas.create_rectangle(1095,0,1281,721, fill='#8E551C')
        if nombre == "Norte" or nombre == "Sur":
            string = "Eres "+ nombre+"\ndel Equipo 1"
        else:
            string = "Eres "+ nombre+"\ndel Equipo 2"
        self.label=ttk.Label(self.frameGame, text = string, font = "Verdana 13", background='#8E551C')
        self.label.place(x= 1100 ,y = 250, in_=self.frameGame)
        stringP = "Puntuaciones\nEquipo 1: "+str(puntuacionEquipo1)+"\nEquipo 2: "+str(puntuacionEquipo2) +"\n\nRonda: " + str(ronda)
        self.label=ttk.Label(self.frameGame, text = stringP, font = "Verdana 13", background='#8E551C')
        self.label.place(x= 1100 ,y = 350, in_=self.frameGame)

    def frameDerecha(self):
            
        global ia
        s = ttk.Style()
        s.configure('my.TButton', font=('Helvetica', 10),background = '#8E551C')
        self.buttonIA=ttk.Button(self.frameGame,text= "IA ON/OFF", style='my.TButton', command = lambda : self.modificaIA() )
        self.buttonIA.place(x=1100,y = 100, in_=self.frameGame)
        stringTrue = "IA: "+repr(bool(ia))
        self.labelIAMOD=ttk.Label(self.frameGame, text = stringTrue, font = "Verdana 13", background='#8E551C')
        self.labelIAMOD.place(x= 1100 ,y = 150, in_=self.frameGame)
    
    def cierra(self,conex): 
        self.root.destroy()
        conex.close()
    
        
        
                    
                
                
                
        
def subasta(opciones):
    res = subastaAI()
    array = opciones.split("/")
    if res == 0:
        return str(0)
    if res in array:
        return res
    else:
        return str(0)
        
        
        
def getSubastaComp():
    global nombre
    if nombre == "Norte":
        return maxSur
    if nombre == "Este":
        return maxOeste
    if nombre == "Sur":
        return maxNorte
    else:
        return maxEste
    
def reiniciaSubasta():
    global maximo,nombremaximo,anterior,maxNorte,maxSur,maxEste,maxOeste, subastaTrue
    maximo = "Ninguna"
    nombremaximo = "Ninguna"
    anterior = "Ninguna"
    maxNorte = Opcion(0,None)
    maxSur= Opcion(0,None)
    maxEste = Opcion(0,None)
    maxOeste = Opcion(0,None)
    subastaTrue = True
    
def valoraPalo(lista,fortaleza):
    x = [x[-1] for x in lista if x[0] > 4 and ( x[-1] == Palo.CORAZON or x[-1] == Palo.PICA)]
    if x:
        return Opcion(7,x[-1])
    x = [x[0] < 6 and x[0] > 1 for x in lista]
    if sum(x) == 4:
        if fortaleza > 14 and fortaleza < 20:
            return Opcion( 7 , None)
        elif fortaleza > 19:
            return Opcion( 8 , None)
    x = [x[-1] for x in lista if x[-1] == Palo.TREBOL or x[-1] == Palo.DIAMANTE]
    if x:
        return Opcion(7 , x[-1])
    return Opcion(0,None)

def valorCartas(lista):
    return [(x.getValor().value-10,x.getPalo()) for x in lista]

def valorMejorado(lista):
    
    def condicion(a,b):
        return a[0] + 1 == b[0] and a[1] == b[1]
    
    def transforma(lista):
        valor = lista[-1][0]
        return [(valor,b[1]) for b in lista]
        
    aux = []
    listaR = []
    for i in range(len(lista)):
        if i == len(lista) - 1 or not condicion(lista[i],lista[i+1]):
            aux.append(lista[i])
            aux = transforma(aux)
            listaR += aux
            aux = []
            if i == len(lista) - 1:
                listaR = [x for x in listaR if x[0] > 0]
                return listaR
        else:
            aux.append(lista[i])
            
def fortalezaValor(lista):
    
    return sum([a for (a,b) in lista])

def longitudPalo(lista):
    
    def conteoPalos(lista):
        aux = []
        for palo in Palo:
            tupla = (lista.count(palo),palo)
            aux.append(tupla)
        return aux

    palo = [x.getPalo() for x in lista]
    palo = conteoPalos(palo)
    palo.sort(key = lambda x:x[0])
    return palo

def cartasFuertes(opciones):
    
    lista = [x for x in opciones if x.getValor().value > 8]
    aux = []
    listaR = []
    for palo in Palo:
        x = [x for x in lista if palo.value == x.getPalo().value]
        if len(x)>2:
            return x
    return False

def cartasFuertesInteriores(opciones):
    lista = [x for x in opciones if x.getValor().value > 9]
    for palo in Palo:
        x = [x for x in lista if palo.value == x.getPalo().value]
        if len(x)>2:
            return x
    return False

def honoresJuntos(lista,longitud):
    
    def condicion(a,b):
        return a.getValor().value + 1 == b.getValor().value and a.getPalo().value == b.getPalo().value
    
    aux = []
    lista = [x for x in lista if x.getValor().value > 10]
    for i in range(len(lista)):
        if i == len(lista) - 1 or not condicion(lista[i],lista[i+1]):
            aux.append(lista[i])
            if len(aux) > longitud:
                return aux
            else:
                aux = []
        else:
            aux.append(lista[i])
    return []
    

def subastaAI():
    
    global mano, subastaTrue
        
    subastaComp = getSubastaComp()
    if subastaComp.getBazas() > 8 or not subastaTrue:
        return str(0)
    subastaTrue = False
    valorC = fortalezaValor(valorMejorado(valorCartas(mano)))
    res = Opcion(0,None)
    if valorC < 12:
        return str(0)
    elif valorC < 22:
        res = valoraPalo(longitudPalo(mano),valorC)
        subasta = res
    else:
        subasta =  Opcion(8, None)
    if subasta.getBazas() == 0:
        return str(0)
    if subastaComp.getBazas() - 6 > 0:
        subastaComp = subastaComp.getBazas() - 6
    else:
        subastaComp = 0
    resultadoSubasta = Opcion(subasta.getBazas() + subastaComp, subasta.getPalo())
    return str(opcionACom(resultadoSubasta))

def cartaGanadora(carta,muerto):
        global mano,cartasJugadas
        baraja = Baraja()
        baraja.creaBaraja()
        manoAux = mano.copy()
        cartasJugadasAux = cartasJugadas.copy()
        cartasMuertoAux = muerto.copy()
        cartasTotales = manoAux + cartasJugadasAux + cartasMuertoAux
        return baraja.cartaPuedeGanar(carta,cartasTotales)

        
def reyCombinado(opciones):
    rey = [x for x in opciones if x.getValor() == 13]
    if rey:
        for carta in rey:
            otra = [x for x in opciones if x == carta or (x.getValor().value + 1 == carta.getValor().value and x.getPalo().value == carta.getPalo().value)
                    or (x.getValor().value - 1 == carta.getValor().value and x.getPalo().value == carta.getPalo().value)]
            if len(otra) > 1:
                otra.remove(carta)
                return carta,otra
    else:
        return []
    
def carteoAI(opciones,tablero,muerto):
    
    global triunfo
    
    if tablero == "None":
        tablero = []
    else:
        tablero = comABaraja(tablero)
    if muerto == "None":
        muerto = []
    else:
        muerto = comABaraja(muerto)
    opciones = comABaraja(opciones)
    paloTriunfo = triunfo.getPalo()
    
    if len(opciones) == 1:
        return str(cartaACom(opciones[0]))
    else:
        if len(tablero) == 3:
            return str(cartaACom(jugadaUltimo(tablero,opciones,paloTriunfo)))
        elif len(tablero) == 2:
            return str(cartaACom(jugadaTercero(tablero,opciones,paloTriunfo,muerto)))
        elif len(tablero) == 1:
            return str(cartaACom(jugadaSegundo(tablero,opciones,paloTriunfo,muerto)))
        else:
            return str(cartaACom(jugadaPrimero(tablero,opciones,paloTriunfo,muerto)))
    return 0

def jugadaUltimo(tablero,opciones,triunfo):
    
    def estimaBaja(opciones,triunfo):
        if triunfo == None:
            opcionesAux = opciones
            opcionesAux.sort(key=lambda x: x.getValor().value)
            return opcionesAux[0]
        else:
            cartas = [x for x in opciones if not x.getPalo().value == triunfo.value]
            cartas.sort(key=lambda x: x.getValor().value)
            if cartas:
                return cartas[0]
            else:
                return opciones[0]
    
    
    if tablero[0].getPalo().value == opciones[0].getPalo().value:
        index = ganarBaza(tablero,[0,1,2,3],triunfo)
        if index == 1:
            return opciones[0]
        for x in opciones:
            tablero.append(x)
            index = ganarBaza(tablero,[0,1,2,3],triunfo)
            if index == 3:
                return x
            else:
                tablero.pop()
        return opciones[0]
    else:
        if triunfo == None:
            return estimaBaja(opciones,triunfo)
        index = ganarBaza(tablero,[0,1,2,3],triunfo)
        if index == 1:
            return estimaBaja(opciones,triunfo)
        for x in opciones:
            tablero.append(x)
            index = ganarBaza(tablero,[0,1,2,3],triunfo)
            if index == 3:
                return x
            else:
                tablero.pop()
        return estimaBaja(opciones,triunfo)
    

def jugadaTercero(tablero,opciones,triunfo,muerto):
    
    def estimaBaja(opciones,triunfo):
        if triunfo == None:
            opcionesAux = opciones
            opcionesAux.sort(key=lambda x: x.getValor().value)
            return opcionesAux[0]
        else:
            cartas = [x for x in opciones if not x.getPalo().value == triunfo.value]
            cartas.sort(key=lambda x: x.getValor().value)
            if cartas:
                return cartas[0]
            else:
                return opciones[0]
    
    index = ganarBaza(tablero,[0,1,2,3],triunfo)
    if index == 0:
        return estimaBaja(opciones,triunfo)
    opciones = opciones[::-1]
    if tablero[0].getPalo().value == opciones[0].getPalo().value:
        cartaGanar = [x for x in opciones if cartaGanadora(x,muerto)]
        if cartaGanar:
            return cartaGanar[0]
        opciones[::-1]
        for x in opciones:
            tablero.append(x)
            index = ganarBaza(tablero,[0,1,2,3],triunfo)
            if index == 2:
                return opciones[0]
            else:
                tablero.pop()
        return opciones[0]
    else:
        if triunfo == None:
            return estimaBaja(opciones,triunfo)
        if index == 1:
            return estimaBaja(opciones,triunfo)
        for x in opciones:
            tablero.append(x)
            index = ganarBaza(tablero,[0,1,2,3],triunfo)
            if index == 2:
                return x
            else:
                tablero.pop()
        return estimaBaja(opciones,triunfo)
    
def jugadaSegundo(tablero,opciones,triunfo,muerto):
    
    def estimaBaja(opciones,triunfo):
        
        if triunfo == None:
            opcionesAux = opciones
            opcionesAux.sort(key=lambda x: x.getValor().value)
            return opcionesAux[0]
        else:
            cartas = [x for x in opciones if not x.getPalo().value == triunfo.value]
            cartas.sort(key=lambda x: x.getValor().value)
            if cartas:
                return cartas[0]
            else:
                return opciones[0]
    
        
    
    
    if tablero[0].getPalo().value == opciones[0].getPalo().value:
        cartaGanar = [x for x in opciones if cartaGanadora(x,muerto)] #Puedes ganar
        if cartaGanar:
            return cartaGanar[0]
        opcionesN = [x for x in opciones if x.getValor().value > 11] #Tienes q,k,a
        for x in opcionesN:
            tablero.append(x)
            index = ganarBaza(tablero,[0,1,2,3],triunfo)
            if index == 1:
                return x
            else:
                tablero.pop()
        opcionesN2 = [x for x in opciones if x.getValor().value < 11 and x.getValor().value > 7][::-1] #Intenta tirar Low
        for x in opcionesN2:
            tablero.append(x)
            index = ganarBaza(tablero,[0,1,2,3],triunfo)
            if index == 1:
                return x
            else:
                tablero.pop()
        #MasAltaConocida
        return opciones[0]
    else:
        if triunfo == None:
            return estimaBaja(opciones,triunfo)
        for x in opciones:
            tablero.append(x)
            index = ganarBaza(tablero,[0,1,2,3],triunfo)
            if index == 1:
                return x
            else:
                tablero.pop()
        return estimaBaja(opciones,triunfo)
    
def jugadaPrimero(tablero,opciones,triunfo,muerto):
    
    global jugadaEspecial
    
    if jugadaEspecial:
        return jugadaEspecial[-1]
    jugadaEspecial = None
    
    if len(opciones) < 9:
        cartaGanar = [x for x in opciones if cartaGanadora(x,muerto)] #Si puedes ganar
        if cartaGanar:
            return cartaGanar[0]
    if triunfo == None:
        paloLargo = longitudPalo(opciones)
        palitoLargo = [x for x in paloLargo if x[0] > 3]
        if palitoLargo:
            return [x for x in opciones if x.getPalo().value == palitoLargo[-1][-1].value][2] #Tercera carta de palo largo
        cartasFInt = cartasFuertesInteriores(opciones)
        if cartasFInt:
            return cartasFInt[1] #Carta interior de cartas desde 10 a AS
        cartasFuerte = honoresJuntos(opciones,3)
        if cartasFuerte:
            jugadaEspecial = cartasFuertes[-2::-1]
            return cartasFuertes[-1] #Carta más fuerte de cartas desde 9 a AS
        
        cartasdiez = [x for x in opciones if x.getValor().value == 10] 
        if cartasdiez:
            return cartasdiez[0] #Tira 10 para forzar cartas fuertes
        if len(opciones) > 4: #Tira la carta más fuerte que tengas
            opcionesAux = opciones.copy()
            opcionesAux.sort(key=lambda x: x.getValor().value)
            return opcionesAux[-4]
        return opciones[0]
    else:
        paloCorto = longitudPalo(opciones)
        palitoCorto = [x for x in paloCorto if x[0] == 1]
        if palitoCorto:
            return [x for x in opciones if x.getPalo().value == palitoCorto[0][-1].value][0] #Quitate singleton
        palitoCorto = [x for x in paloCorto if x[0] == 2]
        if palitoCorto:
            return [x for x in opciones if x.getPalo().value == palitoCorto[0][-1].value][0] #Quitate dobleton
        honores = honoresJuntos(opciones,2)
        if honores:
            return honores[-1] #Mas fuerte de honores consecutivos
        reyotra = reyCombinado(opciones)
        if reyotra:
            jugadaEspecial = reyotra[-1]
            return reyotra[0]
        cartasdiez = [x for x in opciones if x.getValor().value == 10] 
        if cartasdiez:
            return cartasdiez[0] #Tira 10 para forzar cartas fuertes
        if len(opciones) > 4:
            opcionesAux = opciones.copy()
            opcionesAux.sort(key=lambda x: x.getValor().value)
            return opcionesAux[-4]
        return opciones[0]
            

            
        
    
    
    
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

def recibeMensaje(conex):
    return conex.recv(1000).decode()

def enviaMensaje(conex,string):
    s = string.encode()
    conex.send(s)
    
if __name__ == "__main__":
    Window()