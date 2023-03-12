#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRÁCTICA 1 PRODUCTOR-CONSUMIDOR (opcional)
APELLIDOS: Ballesteros Gómez
NOMBRE:    Gabriela 
"""
from multiprocessing import Process
from multiprocessing import Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
import random
from time import sleep


numProductos = 5 #número de veces que produce cada productor
K = 3 #Cada productor tiene K huecos para producir 
NPROD = 3 #nº productores


def delay(factor = 3):
    sleep(3/factor)
        
def add_data(storage, posicion, ultNum, ultInd, mutex): #añadimos un valor al buffer 
    mutex.acquire()
    try:
        storage[posicion*K+ultInd[posicion]] = ultNum[posicion] #tengo que meter el valor en el lugar (nº del productor*longitud del buffer de cada uno + último índice en el que he metido) 
        ultInd[posicion] += 1 #aumento en uno el índice 
        #no actualizo el nuevo valor de ultNum porqeu ya lo he hecho en productor 
    finally:
        mutex.release()


def get_data(storage, mutex, ultInd):
    mutex.acquire()

    try:
        i=0
        menor=10000 #uso una variable auxiliar mayor que el máximo al que voy a llegar 

        while i<len(storage):
            if menor>storage[i] and storage[i] not in (-1,-2): #el productor nunca llega a quedarse con el valor -2 así que no lo incluimos. Con este bucle buscamos el mínimo (distinto de -1)
                menor=storage[i]
                posMin=i
            i+=1
        elegido=(menor,posMin//K)#quiero saber el número y el productor 
        
        ultInd[posMin//K]-=1
        for i in range((posMin-posMin%K),posMin+K-1):#movemos los elementos correspondientes a ese productor un lugar a la izquierda 
            storage[i]=storage[i+1]
        storage[posMin+K-1]=-2 #colocamos el vacío después de correr los elementos a la izquierda 
        
    finally:
        mutex.release()
    return elegido

    
def finProceso(storage, mutex):
    mutex.acquire()
    products = True
    i = 0
    while products and i < len(storage) :#termino si todos los procesos han terminado 
        products = products and storage[i]==-2
        i = i + 1

    mutex.release()
    return products
        
    
def productor(storage, empty, nonEmpty, ultNum, ultInd, mutex, posicion):
    for i in range (numProductos):
        empty[posicion].acquire()
        ultNum[posicion]=ultNum[posicion]+random.randint(0,50) #genero el número sumándole una cantidad al último que hice 
        print (f"El {current_process().name} ha producido un {ultNum[posicion]}")

        add_data(storage, posicion, ultNum, ultInd, mutex)
        delay(6)
        nonEmpty[posicion].release() #señal de que ya he metido mi elemento
        print("el almacén queda:",storage[:])
        
        
    empty[posicion].acquire()
    print(f"El {current_process().name} ha acabado.") 
    
    nonEmpty[posicion].release()  
    
        
        
def consumidor(storage, empty, nonEmpty, listaDef, ultInd, mutex):
    for i in range(NPROD):
        nonEmpty[i].acquire()
        
    while not finProceso(storage,mutex):
        elegido=get_data(storage, mutex, ultInd) #llamo al mínimo y al productor que le corresponde 
        print (f"Consumiendo un {elegido[0]} del productor {elegido[1]}")
        listaDef.append(elegido[0])#lo añado a mi almacén de consumidos 
        print ("El almacén actual es ",storage[:],"\n","La lista definitiva actual es:",listaDef)
        
        empty[elegido[1]].release()#despertamos al productor del número seleccionado
        nonEmpty[elegido[1]].acquire()
        
    delay(6)
    print("La lista definitiva es:",listaDef) #Muestro el almacén final
        

def main():
    storage = Array('i', K*NPROD)#defino un array con K posiciones por productor 
    for i in range(K*NPROD):
        storage[i] = -2 #inicialmente está vacío 
    print ("almacen inicial", storage[:])
    
    ultNum = Array('i', NPROD) #lista de NPROD elementos que guarda el último número que ha fabricado dicho productor (para que se haga en orden creciente)
    ultInd = Array('i', NPROD) #lista de NPROD elementos que guarda la última posición en la que el productor ha añadido elementos  
    for i in range(NPROD):
        ultNum[i] = 0 #iniciamos todos los valores en 0 pues los producidos son vacío 
        ultInd[i] = 0 #iniciamos todos los índices en 0 pues los producidos son vacío
        
        
    last_index = Array('i', NPROD)
    for i in range(NPROD):
        last_index[i] = 0

    
    empty= [Semaphore(K) for i in range(NPROD)]
    nonEmpty = [Semaphore(0) for i in range(NPROD)]
    mutex = Lock()
     
    procs = [ Process(target=productor,
                        name=f'prod_{i}',
                        args=(storage, empty, nonEmpty, ultNum, ultInd, mutex, i))
                for i in range(NPROD) ]

    cons = [Process(target=consumidor, name= "consumidor", 
                         args=(storage, empty, nonEmpty, [], ultInd, mutex))]

    for p in procs + cons: #inicio los procesos 
        p.start()
    
    for p in procs + cons: #termino los procesos 
        p.join()
    

if __name__ == '__main__':
    main()