import pyrebase
import time
import numpy as np
import cv2 as cv
import obspy	
import time
import serial;
from obspy.signal.detrend import polynomial
from umucv.stream import autoStream
import matplotlib.pyplot as plot
try:
    import httplib
except:
    import http.client as httplib

#Creamos un objeto que se conecta a Firebase para controlar la base de datos en tiempo real  
class RealTimeDataBase(object):
    config = {
      "apiKey": "AIzaSyAhD4Gl0P0nOPQwbwBV8lKP2afAZGsHfzw",
      "authDomain": "tfg-francisco.firebaseapp.com",
      "databaseURL": "https://tfg-francisco.firebaseio.com",
      "storageBucket": "tfg-francisco.appspot.com",
    };

    firebase = None
    ready = None 
    wait = False
    internet = False
    
    @property
    def is_ready(self) -> bool:
        return self.ready is not None

    def have_internet(self):
        conn = httplib.HTTPConnection("www.google.com", timeout=5)
        try:
            conn.request("HEAD", "/")
            conn.close()
            self.wait=False
            return True
        except:
            conn.close()
            self.wait=False
            return False

    def actualiza(self):
        self.wait=True
        self.internet=self.have_internet()

        
    def stream_handler(self, message):
        print("Got some update from the Firebase")
        # We only care if something changed
        if message["event"] in ("put", "patch"):
            print("Something changed")
            if message["path"] == "/":
                print("Seems like a fresh data or everything have changed, just grab it!")
                self.my_stuff = message["data"]
    
    def putVelocidad(velocidad):
      self.firebase.child("Velocidad").push(velocidad)
      
    def putDistancia(distancia):
      self.firebase.child("Distancia").push(distancia)
         
    def conecta(self):
        self.wait=True
        self.firebase=pyrebase.initialize_app(self.config).database()
        try:
            self.firebase.child("Encendido").stream(self.stream_handler)
            self.internet=self.have_internet()
        except:
            pass
        self.wait=False
        
    def __init__(self) -> None:
        """Start tracking my stuff changes in Firebase"""
        super().__init__()
        self.conecta()
    
#Busca dónde se puede encontrar la línea de la izquierda
def buscaMargenAbajo(maximo, intervalo, distanciaLineas):
    if maximo-int(intervalo*2.5)-distanciaLineas > 0:
        return maximo-int(intervalo*2.5)-distanciaLineas
    else:
        if maximo-distanciaLineas > 0:
            return 0
        else:
            return -1
            
#Busca dónde se puede encontrar la línea de la derecha        
def buscaMargenArriba(maximo, intervalo, distanciaLineas, y):
    if maximo+int(intervalo*2.5)+distanciaLineas < y:
        return maximo+int(intervalo*2.5)+distanciaLineas
    else:
        if maximo+distanciaLineas < y:
            return y-1
        else:
            return -1

#Busca un pico
def buscaMaximo(v, maximo):
    maximos = np.argpartition(v, -3)[-3:]
    m = maximos[0]
    resta = abs(maximo - m)
    print (maximos)
    for k in maximos[1:3]:
        if abs(maximo - k) < resta:
            print("Cambio ", m, " por ", k)
            m = k
            resta = abs(maximo - k)
    return m

#Definimos la conexión con Arduino
ser = serial.Serial('/dev/ttyUSB0', 115200,timeout=0.0001)
ser.flush()

#Creamos el objeto de la base de datos en tiempo real
database = RealTimeDataBase()

intervalo = None  
maximo1 = None
maximo2 = None
unaLinea = False
maximo = None
nframe = 0
porcentaje = 0.6
distanciaLineas = 0
distanciaLineasTotal = 0
nDist = 1
x,y,z = None,None,None
linea = 0
distancia = 0
mitad = 0
encendido = 0

while True:
    #Mientras esté apagado el robot o no estemos conectados a internet, intenta conectarse
    while not database.ready or not database.internet:
        if not database.wait:
            database.conecta()
        pass 
    #Cuando está encendido
    ser.write("3".encode()); #Arrancar
    for key, frame in autoStream():
        #Si lo apagamos desde la app web o se deconecta de internet, paramos el robot
        # y volvemos al primer while
        if not database.ready or not database.internet:
            ser.write("2".encode());#Parar
            break
            
        if nframe == 0:    
            (x,y,z) = frame.shape
            linea = int(180*x/270)
            intervalo = int(40*y/480)
            mitad=int(y/2)
        
        #Calculamos los valores de la gráfica    
        h0 = frame[linea,:,0]/3 + frame[linea-1,:,0]/3 + frame[linea+1,:,0]/3
        h1 = frame[linea,:,1] + frame[linea-1,:,1]/3 + frame[linea+1,:,1]/3
        h2 = frame[linea,:,2] + frame[linea-1,:,2]/3 + frame[linea+1,:,2]/3
        h = (h0/3+h1/3+h2/3)
        v = polynomial(h,2)
        
        #Si es el primer frame, calculamos la posición de las líneas de una forma distinta
        if nframe == 0:
            half = int(y/2)
            maximo1 = np.argmax(v[0:half])
            maximo2 = np.argmax(v[half:y]) + half
            distanciaLineas = int(350*y/480)
            if maximo2 - maximo1 < distanciaLineas-100:
                unaLinea = True
                if v[maximo1] > v[maximo2]:
                    maximo = maximo1
                else:
                    maximo = maximo2
            else:
                distanciaLineasTotal = maximo2-maximo1
                distanciaLineas = distanciaLineasTotal
        else:
            #Si solo tenemos una linea dibujada
            if unaLinea:
                #Si el maximo pertenece a la segunda mitad, comprobamos si en función de la distancia de las líneas nos cabe la línea de la primera mitad
                #si es así, calculamos los máximos y comprobamos que el nuevo máximo1 es mayor que máximo2*0.75, ya que es posible que no se pueda ver la línea.
                #Si no es así, definimos maximo2 como maximo.
                #En el else hacemos lo mismo pero desde la primera mitad.
                if maximo >= y/2:
                    margenAbajo = buscaMargenAbajo(maximo,intervalo,distanciaLineas)
                    if margenAbajo!=-1:
                        print (maximo, maximo-distanciaLineas+int(intervalo*2.5), margenAbajo)
                        maximo1= buscaMaximo(v[margenAbajo:maximo-distanciaLineas+int(intervalo*2.5)], maximo-distanciaLineas-margenAbajo) + margenAbajo 
                        if maximo + intervalo < y:
                            maximo2= buscaMaximo(v[maximo-intervalo:maximo+intervalo], intervalo) + maximo - intervalo
                        else:
                            maximo2= buscaMaximo(v[maximo-intervalo:y], intervalo) + maximo - intervalo
                        if v[maximo1] > v[maximo2]*porcentaje:
                            unaLinea=False
                            nDist = nDist + 1
                            distanciaLineasTotal = (maximo2 - maximo1) + distanciaLineasTotal
                            distanciaLineas = int(distanciaLineasTotal/nDist)
                        else:
                            maximo = maximo2
                    else:
                       maximo = buscaMaximo(v[maximo-intervalo:maximo+intervalo], intervalo) + maximo-intervalo 
                else:
                    margenArriba = buscaMargenArriba(maximo,intervalo,distanciaLineas,y)
                    if margenArriba != -1:
                        if maximo - intervalo >= 0:
                            maximo1= buscaMaximo(v[maximo-intervalo:maximo +intervalo], intervalo) + maximo - intervalo
                        else:
                            maximo1= buscaMaximo(v[0:maximo +intervalo], maximo)  
                        maximo2= buscaMaximo(v[maximo+distanciaLineas-int(intervalo*2.5):margenArriba], intervalo*2) + maximo+distanciaLineas-int(2.5*intervalo) 
                        if v[maximo2] > porcentaje*maximo1:
                            unaLinea=False
                            nDist = nDist + 1
                            distanciaLineasTotal = (maximo2 - maximo1) + distanciaLineasTotal
                            distanciaLineas = int(distanciaLineasTotal/nDist)
                        else:
                            maximo = maximo1
                    else:
                       maximo = buscaMaximo(v[maximo-intervalo:maximo+intervalo], intervalo) + maximo-intervalo                     
            #Si tenemos dos lineas dibujadas
            else:
                #Calculamos su nueva posición y si el valor de una es menor de 0.75*máxima no la consideramos una línea
                margenAbajo1 = maximo1 - intervalo
                margenArriba2 = maximo2 + intervalo
                if margenAbajo1 < 0:
                    margenAbajo1 = 0
                if margenArriba2 > y:
                    margenArriba2 = y-1
                maximo1 = buscaMaximo(v[margenAbajo1:maximo1+intervalo], maximo1-margenAbajo1) + margenAbajo1
                maximo2 = buscaMaximo(v[maximo2-intervalo:margenArriba2], intervalo) + maximo2 - intervalo
                m = max(v[maximo1], v[maximo2]) * porcentaje

                if v[maximo1] > m and v[maximo2] > m:
                    nDist = nDist + 1
                    distanciaLineasTotal = (maximo2 - maximo1) + distanciaLineasTotal
                    distanciaLineas = int(distanciaLineasTotal/nDist)
                elif v[maximo1] > m:
                    unaLinea = True
                    maximo = maximo1
                elif v[maximo2] > m:
                    unaLinea = True
                    maximo = maximo2
                    
        #Calculamos la dirección en la que hay que girar        
        if unaLinea:
            dis=abs(mitad-maximo)
            if dis < mitad/2:
                if maximo > mitad:
                    #Giramos a la izquierda
                    ser.write("0".encode());
                else:
                    #Giramos a la derecha
                    ser.write("1".encode());
        else:
            centro = int((maximo1+maximo2)/2)
            disCentro = abs(centro-mitad)
            if disCentro > mitad/2:
                if centro > mitad:
                    #Giramos a la derecha
                    ser.write("1".encode());
                else:
                    #Giramos a la izquierda
                    ser.write("0".encode());
            
        #Si Arduino nos envía algún dato por el puerto USB, lo enviamos a Firebase
        while ser.inWaiting() > 0:
            txt += ser.read(1)
            orden = txt.split();    
            if orden[0] == 'Velocidad':
              putVelocidad(int(orden[1]))
            elif orden[0] == 'Distancia':
              distancia = distancia + int(orden[1])
              putDistancia(distancia)

        nframe = nframe + 1

            
