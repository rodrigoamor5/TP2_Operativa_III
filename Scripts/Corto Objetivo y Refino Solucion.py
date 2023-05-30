#############################################################################################################

import numpy as np
import pandas as pd
import time
import random
import math
import copy

#############################################################################################################

#Matriz de distancias
df_distancias = pd.read_csv("Caso II - Matriz de Distancias.csv", delimiter= ",", index_col= 0)

#Informacion de pedidos
datos_prueba = pd.read_csv("Caso II - Set de Datos.csv", delimiter= ",", index_col= 0)
column_mapping = {column_name: int(column_name) for column_name in datos_prueba.columns}
datos_prueba.rename(columns=column_mapping, inplace=True) # Reassign columns with new integer names

#############################################################################################################

TARIFA_PROMEDIO = 1200
TARIFA_ESTRATO1 = 1400
TARIFA_ESTRATO2 = 1200
TARIFA_ESTRATO3 = 1000
AFORO_MINIMO = 5600
OCIOSIDAD = 5000
COSTO_DE_OPORTUNIDAD = 3000
AHORRO = 0.05
TARIFA_OBJETIVO = TARIFA_PROMEDIO * (1-AHORRO)
CANTIDAD_DE_CLIENTES_POR_CAMION = 3
CANTIDAD_DE_CAMIONES = 6
TONS_MAX_POR_CAMION = 12
DIST_MAX_POR_CLIENTE = 2

#############################################################################################################

def llega(x):
   return True if x <= DIST_MAX_POR_CLIENTE else False
df_llega = df_distancias.applymap(llega)

#############################################################################################################

def costoCamion(tons_repartidas_por_camion):
    costo_por_camion = []
    for tons in tons_repartidas_por_camion:
        costo = float(0)
        if (tons == 0):
            costo = OCIOSIDAD
        elif (tons < 4):
            costo = AFORO_MINIMO
        elif (tons < 6.5):
            costo = tons * TARIFA_ESTRATO1
        elif (tons < 9.5):
            costo = tons * TARIFA_ESTRATO2
        else:
            costo = tons * TARIFA_ESTRATO3
        costo_por_camion.append(costo)
    return costo_por_camion

#############################################################################################################

def generarSolucionInicial(p):

    #Elimina los clientes con 0 ton, toma el index (nombre de los clientes), lo convierto en una lista y elimino el ultimo que es el total
    pedidos = p[p > 0].index
    pedidos = pedidos.to_list()
    pedidos.pop()

    #Inicializo las siguientes variables
    pedidos_por_asignar = pedidos                                   #Inicializo una lista con los pedidos a asignar
    clientes_por_camion = [[] for _ in range(CANTIDAD_DE_CAMIONES)] #Inicializo una lista con los pedidos asignados a cada camion
    clientes_no_asignados = []                                      #Inicializo un lista con los pedidos no asignados
    
    #Defino la cantidad de clientes por asignar
    cantidad_clientes = len(pedidos_por_asignar)

    #Recorro toda la lista de clientes por asignar
    for i in range(cantidad_clientes): 
        cliente = pedidos_por_asignar.pop()                     #Elimino el ultimo cliente de la lista de clientes a la vez que le asigno el cliente eliminado a la variable cliente
        rand = random.randint(0, CANTIDAD_DE_CAMIONES-1)        #Genero un numero aleatorio entero del 0 al 5 para elegir a que camion asignar dicho pedido
        camion_cliente = clientes_por_camion[rand]              #Defino los clientes asignados hasta el momento a ese camion
        cantidad_clientes = len(camion_cliente)                 #Determino la cantidad de clientes asignados hasta el momento a ese camion
        
        #Verifico que se cumplan todas las restricciones
            #RESTRICCION 1: "Los camiones no pueden salir con más de X entregas por día."
            #RESTRICCION 2: "No se pueden superar los 2 km de distancia entre cliente y cliente de un mismo camion"
        #Primero verifico la restriccion 1, si la cumple verifico la restriccion 2, si la cumple, asigno el cliente a ese camion
        #Si no cumple alguna de las condiciones lo considero un pedido no asignado

        if cantidad_clientes < CANTIDAD_DE_CLIENTES_POR_CAMION: #Verifico que el camion no tenga 3 clientes
            llega_list = []
            for j in range(cantidad_clientes):
                cliente_en_camion = camion_cliente[j]
                llega = df_llega.loc[cliente_en_camion,cliente]
                llega_list.append(llega)
            llega_array = np.array(llega_list)
            llega_todos = np.prod(llega_array)                  #llega_todos = 0 si hay al menos un FALSE y llega_todos = 1 si todos son TRUE
            if(llega_todos):                                    #Verifico que la distancia entre clientes sea menor a la maxima
                clientes_por_camion[rand].append(cliente)
            else:
                clientes_no_asignados.append(cliente)
        else:
            clientes_no_asignados.append(cliente)

    pedidos_por_camion = []                                    
    toneladas = []                                              #Inicializo una lista con las toneladas por camion
    toneladas_no_asignadas = 0                                  #Inicializo una variable con las toneladas no asignadas

    #Recorro los clientes asignados a cada camion
    for camion in clientes_por_camion:                         
        pedido = p[camion]                                      #Defino las toneladas pedidas por cada cliente 
        pedidos_por_camion.append(pedido)
    for pedidos in pedidos_por_camion:
        tons = pedidos.values.sum()
        toneladas.append(tons)
    
    #Calculo la cantidad de toneladas no asignadas
    toneladas_no_asignadas = p[clientes_no_asignados].values.sum()  

    tons_repartidas_por_camion = []                             #Inicializo una lista con las toneladas repartidas por camion
    toneladas_no_repartidas = 0                                 #Inicializo una variable con las toneladas no repartidas

    #De las toneladas asignadas a cada camion, calculo cuantas efectivamente se reparten y cuantas no
    for t in range(0,CANTIDAD_DE_CAMIONES-1):
        tons = toneladas[t]
        if(tons <= TONS_MAX_POR_CAMION):
            tons_repartidas_por_camion.append(tons)
        else:
            tons_repartidas_por_camion.append(TONS_MAX_POR_CAMION)
            toneladas_no_repartidas += tons-TONS_MAX_POR_CAMION
    
    #Calculo la cantidad de toneladas repartidas
    toneladas_repartidas = sum(tons_repartidas_por_camion)
    
    costo_por_camion = []
    
    #Calculo el costo por camion
    costo_por_camion = costoCamion(tons_repartidas_por_camion)
   
    #Calculo del costo total
    costo_total = sum(costo_por_camion) + (toneladas_no_asignadas + toneladas_no_repartidas)*COSTO_DE_OPORTUNIDAD

    #Calculo el costo por tonelada repartida
    costo_por_ton = costo_total / toneladas_repartidas
  
    return clientes_por_camion, clientes_no_asignados, toneladas, toneladas_no_asignadas, tons_repartidas_por_camion, toneladas_no_repartidas, costo_por_camion, costo_total, toneladas_repartidas, costo_por_ton

#############################################################################################################

#Funcion que genera el vecino
def generarVecino(p, clientes_por_camion, clientes_no_asignados): 
    
    #Elimino un pedido aleatorio por camion para reasignarlo nuevamente
    for i in range(CANTIDAD_DE_CAMIONES):

        clientes_por_camion_i = clientes_por_camion[i]          #Me quedo con los pedidos del camion i
        len_i = len(clientes_por_camion_i)                      #Veo cuantos pedidos tiene el camion
        
        if(len_i > 0):
            rand = random.randint(0, len_i-1)                     #Selecciono aleatoriamente el pedido a cambiar
            cliente_eliminado = clientes_por_camion_i.pop(rand)
            clientes_no_asignados.append(cliente_eliminado)      #Lo agrego a la lista de clientes no asignados
    
    #Asigno los clientes no asignados a los camiones aleatoriamente
    
    #Inicializo las siguientes variables
    pedidos_por_asignar = clientes_no_asignados                     #Inicializo una lista con los pedidos a asignar
    clientes_no_asignados = []                                      #Inicializo un lista con los pedidos no asignados
    
    #Defino la cantidad de clientes por asignar
    cantidad_clientes = len(pedidos_por_asignar)

    #Recorro toda la lista de clientes por asignar
    for i in range(cantidad_clientes): 
        cliente = pedidos_por_asignar.pop()                     #Elimino el ultimo cliente de la lista de clientes a la vez que le asigno el cliente eliminado a la variable cliente
        rand = random.randint(0, CANTIDAD_DE_CAMIONES-1)        #Genero un numero aleatorio entero del 0 al 5 para elegir a que camion asignar dicho pedido
        camion_cliente = clientes_por_camion[rand]              #Defino los clientes asignados hasta el momento a ese camion
        cantidad_clientes = len(camion_cliente)                 #Determino la cantidad de clientes asignados hasta el momento a ese camion
        
        #Verifico que se cumplan todas las restricciones
            #RESTRICCION 1: "Los camiones no pueden salir con más de X entregas por día."
            #RESTRICCION 2: "No se pueden superar los 2 km de distancia entre cliente y cliente de un mismo camion"
        #Primero verifico la restriccion 1, si la cumple verifico la restriccion 2, si la cumple, asigno el cliente a ese camion
        #Si no cumple alguna de las condiciones lo considero un pedido no asignado

        if cantidad_clientes < CANTIDAD_DE_CLIENTES_POR_CAMION: #Verifico que el camion no tenga 3 clientes
            llega_list = []
            for j in range(cantidad_clientes):
                cliente_en_camion = camion_cliente[j]
                llega = df_llega.loc[cliente_en_camion,cliente]
                llega_list.append(llega)
            llega_array = np.array(llega_list)
            llega_todos = np.prod(llega_array)                  #llega_todos = 0 si hay al menos un FALSE y llega_todos = 1 si todos son TRUE
            if(llega_todos):                                    #Verifico que la distancia entre clientes sea menor a la maxima
                clientes_por_camion[rand].append(cliente)
            else:
                clientes_no_asignados.append(cliente)
        else:
            clientes_no_asignados.append(cliente)

    pedidos_por_camion = []                                    
    toneladas = []                                              #Inicializo una lista con las toneladas por camion
    toneladas_no_asignadas = 0                                  #Inicializo una variable con las toneladas no asignadas

    #Recorro los clientes asignados a cada camion
    for camion in clientes_por_camion:                         
        pedido = p[camion]                                      #Defino las toneladas pedidas por cada cliente 
        pedidos_por_camion.append(pedido)
    for pedidos in pedidos_por_camion:
        tons = pedidos.values.sum()
        toneladas.append(tons)
    
    #Calculo la cantidad de toneladas no asignadas
    toneladas_no_asignadas = p[clientes_no_asignados].values.sum()  

    tons_repartidas_por_camion = []                             #Inicializo una lista con las toneladas repartidas por camion
    toneladas_no_repartidas = 0                                 #Inicializo una variable con las toneladas no repartidas

    #De las toneladas asignadas a cada camion, calculo cuantas efectivamente se reparten y cuantas no
    for t in range(0,CANTIDAD_DE_CAMIONES-1):
        tons = toneladas[t]
        if(tons <= TONS_MAX_POR_CAMION):
            tons_repartidas_por_camion.append(tons)
        else:
            tons_repartidas_por_camion.append(TONS_MAX_POR_CAMION)
            toneladas_no_repartidas += tons-TONS_MAX_POR_CAMION
    
    #Calculo la cantidad de toneladas repartidas
    toneladas_repartidas = sum(tons_repartidas_por_camion)
    
    costo_por_camion = []
    
    #Calculo el costo por camion
    costo_por_camion = costoCamion(tons_repartidas_por_camion)
   
    #Calculo del costo total
    costo_total = sum(costo_por_camion) + (toneladas_no_asignadas + toneladas_no_repartidas)*COSTO_DE_OPORTUNIDAD

    #Calculo el costo por tonelada repartida
    costo_por_ton = costo_total / toneladas_repartidas
  
    return clientes_por_camion, clientes_no_asignados, toneladas, toneladas_no_asignadas, tons_repartidas_por_camion, toneladas_no_repartidas, costo_por_camion, costo_total, toneladas_repartidas, costo_por_ton

#############################################################################################################

T_INICIAL = 1500
T_FINAL = 10
PASO = -1
ITERACIONES_POR_TEMPERATURA = 25

#############################################################################################################

def recocidoSimulado(dia):

    #Inicializo una serie de variables
    clientes_por_camion_min = []
    clientes_no_asignados_min = []
    costo_por_ton_min = float('inf')
    

    #Genero la solucion inicial
    x1, x2, x3, x4, x5, x6, x7, x8, x9, x10 = generarSolucionInicial(dia)
    #clientes_por_camion, clientes_no_asignados, toneladas, toneladas_no_asignadas, tons_repartidas_por_camion, toneladas_no_repartidas, costo_por_camion, costo_total, toneladas_repartidas, costo_por_ton

    #Guardo la solucion actual
    clientes_por_camion_now = x1
    clientes_no_asignados_now = x2
    costo_por_ton_now = x10

    #Guardo la solucion minima 
    clientes_por_camion_min = x1
    clientes_no_asignados_min = x2
    costo_por_ton_min = x10

    #Comienzo el recocido simulado

    for t in range(T_INICIAL, T_FINAL, PASO):

        count = 0

        #Para cada temperatura realizo varias iteraciones
        for n in range(ITERACIONES_POR_TEMPERATURA):
            
            count += 1
            
            #Defino un vecino
            y1, y2, y3, y4, y5, y6, y7, y8, y9, y10 = generarVecino(dia, copy.deepcopy(clientes_por_camion_now),copy.deepcopy(clientes_no_asignados_now))
            #clientes_por_camion, clientes_no_asignados, toneladas, toneladas_no_asignadas, tons_repartidas_por_camion, toneladas_no_repartidas, costo_por_camion, costo_total, toneladas_repartidas, costo_por_ton

            #Calculo la diferencia entre la solucion actual y la nueva solucion
            delta = costo_por_ton_now - y10
                        
            #¿Es mejor que la solucion actual?

            if delta < 0 :                              #Si la solucion nueva es peor que la anterio delta < 0 porque estoy minimizando el costo
                
                #Como no es mejor, debo aplica un proceso de aceptacion estocastico

                acepto = math.e**(delta/t)              #Calculo la probabilidad de aceptar dicha solucion peor 
                probabilidad = random.random()          #Genero un numero aleatorio
            
                if acepto > probabilidad:               #Si el número generado es menor que la probabilidad de aceptar, entonces ACEPTO UNA PEOR SOLUCION
                    
                    clientes_por_camion_now = y1
                    clientes_no_asignados_now = y2
                    costo_por_ton_now = y10
                    count = 0

            else:                                       #Si la solucion nueva es mejor que la anterior la acepto             
                clientes_por_camion_now = y1
                clientes_no_asignados_now = y2
                costo_por_ton_now = y10
                count = 0

            #¿Es mejor que la condicion minima?

            if costo_por_ton_now < costo_por_ton_min:   #Si la solucion actual es mejor que la minima, actualizo las variables

                clientes_por_camion_min = clientes_por_camion_now
                clientes_no_asignados_min = clientes_no_asignados_now
                costo_por_ton_min = costo_por_ton_now

            #Corto cuando llego a la tarifa objetivo
            if costo_por_ton_min < TARIFA_OBJETIVO:
                return clientes_por_camion_min, clientes_no_asignados_min, costo_por_ton_min
            
            if count == 5:
                break
            print("Temperatura: ", t)
            print("Iteracion: ", count)
            print("Costo: ",costo_por_ton_min)
    return clientes_por_camion_min, clientes_no_asignados_min, costo_por_ton_min

#############################################################################################################

dia = datos_prueba[8]

inicio = time.time()

clientes_por_camion_resultado, clientes_no_asignados_resultado, costo_por_ton_resultado = recocidoSimulado(dia)

#Si me quedo algun cliente sin asignar lo asigno al primer camion que puedo
if len(clientes_no_asignados_resultado) != 0:
    #Recorro toda la lista de clientes no asignados 
    for i in range(len(clientes_no_asignados_resultado)): 
        cliente = clientes_no_asignados_resultado.pop()          #Elimino el ultimo cliente de la lista de clientes a la vez que le asigno el cliente eliminado a la variable cliente
        for j in range (len(clientes_por_camion_resultado)): 
            camion_cliente = clientes_por_camion_resultado[j]   #Defino los clientes asignados hasta el momento a ese camion
        cantidad_clientes = len(camion_cliente)                 #Determino la cantidad de clientes asignados hasta el momento a ese camion
        
        #Verifico que se cumplan todas las restricciones
            #RESTRICCION 1: "Los camiones no pueden salir con más de X entregas por día."
            #RESTRICCION 2: "No se pueden superar los 2 km de distancia entre cliente y cliente de un mismo camion"
        #Primero verifico la restriccion 1, si la cumple verifico la restriccion 2, si la cumple, asigno el cliente a ese camion
        #Si no cumple alguna de las condiciones lo considero un pedido no asignado

        if cantidad_clientes < CANTIDAD_DE_CLIENTES_POR_CAMION: #Verifico que el camion no tenga 3 clientes
            llega_list = []
            for j in range(cantidad_clientes):
                cliente_en_camion = camion_cliente[j]
                llega = df_llega.loc[cliente_en_camion,cliente]
                llega_list.append(llega)
            llega_array = np.array(llega_list)
            llega_todos = np.prod(llega_array)                  #llega_todos = 0 si hay al menos un FALSE y llega_todos = 1 si todos son TRUE
            if(llega_todos):                                    #Verifico que la distancia entre clientes sea menor a la maxima
                clientes_por_camion_resultado[j].append(cliente)
            else:
                clientes_no_asignados_resultado.append(cliente)
        else:
            clientes_no_asignados_resultado.append(cliente)
fin = time.time()  

print("Clientes por camion: ", clientes_por_camion_resultado)
print("Clientes no asignados: ", clientes_no_asignados_resultado)
print("Costo por tonelada: ", costo_por_ton_resultado)
print("Ahorro porcentual: ", 100*(TARIFA_PROMEDIO - costo_por_ton_resultado)/TARIFA_PROMEDIO)
print("Tiempo de ejecucion: ", fin - inicio)
