#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRÁCTICA 1 PRODUCTOR-CONSUMIDOR 
APELLIDOS: Ballesteros Gómez
NOMBRE:    Gabriela 
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random

MAX=500 #número más alto que pueden generar los productores 

numProductos=3 #número de productos que fabrica cada productor 
NPROD = 4
#tenemos un solo consumidor 


def delay(factor = 3):
    sleep(3/factor)


def add_data(storage, data, mutex, posicion):#añadimos un valor al buffer 
    mutex.acquire()#teniendo instanciado el objeto le damos la capacidad de bloqueo 
    try:
        storage[posicion] = data #le añadimos cosas al productor, lo he cambiado por una suma por lo que me ha dicho cesar 
        #print('he añadido', data, 'al ', posicion)
        delay(6)
    finally:
        mutex.release() #liberas el candado 


def get_data(storage, mutex):
    mutex.acquire()

    try:
        piv=MAX+1#uso una variable auxiliar mayor que el máximo al que voy a llegar 
        pos=0
        posMin=0
        for i in storage:
            if piv>i and i!=-1: #el productor nunca llega a quedarse con el valor -2 así que no lo incluimos. Con este bucle buscamos el mínimo (distinto de -1)
                piv=i
                posMin=pos
            pos+=1
        elegido=(piv,posMin)
        
        storage[posMin]=-2 #hemos cogido el valor así que colocamos el vacío en esa posición 
    finally:
        mutex.release()
    return elegido

    
def finProceso(storage, mutex,listaFinal):
    mutex.acquire()
    products = True
    i = 0
    while products and (i < len(storage) or len(listaFinal)<numProductos):#termino si todos los procesos han terminado 
        products = products and storage[i] == -1
        i = i + 1
    mutex.release()
    return products


def productor(storage, empty, nonEmpty, mutex, posicion):
    """
    Genero números aleatorios de forma creciente 
    los meto en el buffer en mi posición de productor cuando me dan la señal 
    """
    nuevo = 0
    for i in range(numProductos): #cada productor produce numProductos 
        nuevo += random.randint(0,50)
        empty[posicion].acquire() #espero a que mi lugar haya quedado vacío 
        add_data(storage,nuevo,mutex,posicion)
        print (f"El {current_process().name} ha producido un {nuevo}")
        nonEmpty[posicion].release()#señal de que ya he metido mi elemento 
                                                       
    empty[posicion].acquire()
    print(f"El {current_process().name} ha acabado.") #cuando ya he producido los números correspondientes me actualizo a -1 
    add_data(storage,-1,mutex,posicion) 
    nonEmpty[posicion].release()    
    
    
def consumidor(storage, empty, non_empty, mutex,listaFinal):
    for i in range(len(non_empty)): #nos aseguramos de que todos los productores han añadido un valor
        non_empty[i].acquire()
        
    while not finProceso(storage, mutex, listaFinal): #cogemos números del buffer mientras quede algún productor en uso  
        print (f"{current_process().name}: tomamos el menor de:", storage[:])
        elegido=get_data(storage,mutex)
        listaFinal+=[elegido[0]]#get_data elige el menor elemento, cogemos el 0 porque devuelve [num,productor]
        print ("que es ", elegido[0], " producido por:", elegido[1], ". Lista final actual:", listaFinal)
        
        empty[elegido[1]].release() #despertamos al productor del número seleccionado 
        non_empty[elegido[1]].acquire() 
        

    delay(6)
    print("La lista definitiva es:",listaFinal) #Muestro el almacén final 
    


def main():
    storage = Array('i', NPROD) #defino storage como un array compartido 

    for i in range(NPROD):
        storage[i] = -2 #usamos -2 para indicar que los valores son vacíos 
    print ("Almacen inicial:", storage[:])

     
    non_empty=[Semaphore(0) for i in range(NPROD)]
    empty=[BoundedSemaphore(1) for i in range(NPROD)]
    
    mutex = Lock() #semáforo general para trabajar con el Array
    
    
    prodlst = [Process(target=productor,
                        name=f'prod_{i}',
                        args=(storage, empty, non_empty, mutex, i))
               for i in range(NPROD)] 
    
    cons = [Process(target=consumidor,
                      name="consumidor",
                      args=(storage, empty, non_empty, mutex,[])) ]
     

    for p in prodlst + cons:
        p.start()

    for p in prodlst + cons: 
        p.join()

        
if __name__ == '__main__':
    main()
