#############################################################################################################

import numpy as np
import pandas as pd
import time
import random
import math
import copy
import sys

#############################################################################################################
#Matriz de distancias
#file_path_distancias = sys.argv[1]
#file_path_pedidos = sys.argv[2]
DIRECCION_DE_RESULTADOS = "Datos/Caso II - Resultados.csv"
COSTO_DE_OPORTUNIDAD = 3000
CANTIDAD_DE_CLIENTES_POR_CAMION = 3
CANTIDAD_DE_CAMIONES = 6
TONS_MAX_POR_CAMION = 12
DIST_MAX_POR_CLIENTE = 2



df_distancias = pd.read_csv("Datos/Caso II - Matriz de Distancias.csv", delimiter= ",", index_col= 0)

#Informacion de pedidos
datos_prueba = pd.read_csv("Datos/Caso II - Set de Datos.csv", delimiter= ",", index_col= 0)
column_mapping = {column_name: int(column_name) for column_name in datos_prueba.columns}
datos_prueba.rename(columns=column_mapping, inplace=True) # Reassign columns with new integer names

#############################################################################################################

TARIFA_PROMEDIO = 1220
TARIFA_ESTRATO1 = 1400
TARIFA_ESTRATO2 = 1200
TARIFA_ESTRATO3 = 1000
AFORO_MINIMO = 5600
OCIOSIDAD = 5000
AHORRO = 0.05
TARIFA_OBJETIVO = TARIFA_PROMEDIO * (1-AHORRO)


#############################################################################################################

def llega(x):
   return True if x <= DIST_MAX_POR_CLIENTE else False
df_llega = df_distancias.applymap(llega)

#############################################################################################################
#RESTRICCION 1: "Los camiones no pueden salir con más de X entregas por día."
def restriccion1(clientes_por_camion, rand):
    
    camion_cliente = clientes_por_camion[rand]              
    cantidad_clientes = len(camion_cliente)                 

    return camion_cliente, cantidad_clientes 

#############################################################################################################
#RESTRICCION 2: "No se pueden superar los 2 km de distancia entre cliente y cliente de un mismo camion"
def restricion2(cantidad_clientes, camion_cliente, cliente):

    llega_list = []

    for j in range(cantidad_clientes):
        cliente_en_camion = camion_cliente[j]
        llega = df_llega.loc[cliente_en_camion,cliente]
        llega_list.append(llega)

    llega_array = np.array(llega_list)
    llega_todos = np.prod(llega_array)
    
    return llega_todos                      #llega_todos = 0 si hay al menos un FALSE y llega_todos = 1 si todos son TRUE

#############################################################################################################
#RESTRICCION 3: "Capacidad maxima del camion 12 ton"
def restriccion3(p, camion_cliente):
    
    pedido = p[camion_cliente]                          #Pedidos asignados hasta el momento       
    tons = pedido.values.sum()                          #Toneladas asignadas hasta el momento
    
    return tons 

#############################################################################################################

def calcularToneladas(clientes_por_camion, clientes_no_asignados, p):

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

    return toneladas, tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas

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

def costoPorTon(tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas):

    costo_por_camion = []
    
    #Calculo el costo por camion
    costo_por_camion = costoCamion(tons_repartidas_por_camion)
   
    #Calculo del costo total
    costo_total = sum(costo_por_camion) + (toneladas_no_asignadas + toneladas_no_repartidas)*COSTO_DE_OPORTUNIDAD

    #Calculo el costo por tonelada repartida
    costo_por_ton = costo_total / toneladas_repartidas
    
    return costo_por_camion, costo_total, costo_por_ton

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
        
        #Asigno el cliente a un camion o queda no asignado
        
        #Genero un numero aleatorio entero del 0 al 5 para elegir a que camion asignar dicho pedido
        rand = random.randint(0, CANTIDAD_DE_CAMIONES-1) 
            
        #Verifico el cumplimiento de las restricciones, si alguna no se cumple se considerará el pedido como no asignado
        camion_cliente, cantidad_clientes = restriccion1(clientes_por_camion, rand)
            
        if (cantidad_clientes < CANTIDAD_DE_CLIENTES_POR_CAMION) and (restricion2(cantidad_clientes, camion_cliente, cliente)) and (restriccion3(p, camion_cliente) < TONS_MAX_POR_CAMION):                    
           clientes_por_camion[rand].append(cliente)
        else:
            clientes_no_asignados.append(cliente)

    #Determino las toneladas asignadas, no asignadas, repartidas y no repartidas 
    toneladas, tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas = calcularToneladas(clientes_por_camion, clientes_no_asignados, p)
    
    #Costos
    costo_por_camion, costo_total, costo_por_ton = costoPorTon(tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas)
  
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
        
        #Asigno el cliente a un camion o queda no asignado
        #Genero un numero aleatorio entero del 0 al 5 para elegir a que camion asignar dicho pedido
        rand = random.randint(0, CANTIDAD_DE_CAMIONES-1) 
            
        #Verifico el cumplimiento de las restricciones, si alguna no se cumple se considerará el pedido como no asignado
        camion_cliente, cantidad_clientes = restriccion1(clientes_por_camion, rand)
            
        if cantidad_clientes < CANTIDAD_DE_CLIENTES_POR_CAMION:                         #RESTRICCION 1     
            
            llega_todos = restricion2(cantidad_clientes, camion_cliente, cliente)
            
            if(llega_todos):                                                            #RESTRICCION 2
                
                tons = restriccion3(p, camion_cliente)
                
                if (tons < TONS_MAX_POR_CAMION):                                        #RESTRICCION 3
                        
                    clientes_por_camion[rand].append(cliente)
                
                else:
                    clientes_no_asignados.append(cliente)
            else:
                clientes_no_asignados.append(cliente) 
        else:
            clientes_no_asignados.append(cliente)

    #Determino las toneladas asignadas, no asignadas, repartidas y no repartidas 
    toneladas, tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas = calcularToneladas(clientes_por_camion, clientes_no_asignados, p)
    
    #Costos
    costo_por_camion, costo_total, costo_por_ton = costoPorTon(tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas)
  
    return clientes_por_camion, clientes_no_asignados, toneladas, toneladas_no_asignadas, tons_repartidas_por_camion, toneladas_no_repartidas, costo_por_camion, costo_total, toneladas_repartidas, costo_por_ton

#############################################################################################################

T_INICIAL = 2000
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

            if delta <= 0 :                              #Si la solucion nueva es peor que la anterio delta < 0 porque estoy minimizando el costo
                
                #Como no es mejor, debo aplica un proceso de aceptacion estocastico

                acepto = math.e**(delta/t)              #Calculo la probabilidad de aceptar dicha solucion peor 
                probabilidad = random.random()          #Genero un numero aleatorio
            
                if acepto > probabilidad:               #Si el número generado es menor que la probabilidad de aceptar, entonces ACEPTO UNA PEOR SOLUCION
                    
                    clientes_por_camion_now = y1
                    clientes_no_asignados_now = y2
                    costo_por_ton_now = y10

            else:                                       #Si la solucion nueva es mejor que la anterior la acepto             
                clientes_por_camion_now = y1
                clientes_no_asignados_now = y2
                costo_por_ton_now = y10

            #¿Es mejor que la condicion minima?

            if costo_por_ton_now < costo_por_ton_min:   #Si la solucion actual es mejor que la minima, actualizo las variables

                clientes_por_camion_min = clientes_por_camion_now
                clientes_no_asignados_min = clientes_no_asignados_now
                costo_por_ton_min = costo_por_ton_now
                count = 0

            #Corto cuando llego a la tarifa objetivo
            if costo_por_ton_min < TARIFA_OBJETIVO:
                break

            #Corto cuando la solucion minima no cambia durante 10 iteraciones seguidas
            if count == 10:
                break
        
        #Corto cuando llego a la tarifa objetivo
        if costo_por_ton_min < TARIFA_OBJETIVO:
            break

    return clientes_por_camion_min, clientes_no_asignados_min, costo_por_ton_min

#############################################################################################################

def refino (p, clientes_por_camion_resultado, clientes_no_asignados_resultado):
    
    #Recorro toda la lista de clientes no asignados y los asigno al primero que encuentro libre
    for i in range(len(clientes_no_asignados_resultado)-1,-1,-1): 
            
        cliente = clientes_no_asignados_resultado[i] 
        
        #Voy recorriendo los camiones y veo si lo puedo meter ahi o no 
        for j in range (len(clientes_por_camion_resultado)):            
        
            #Verifico el cumplimiento de las restricciones, si alguna no se cumple se considerará el pedido como no asignado
            camion_cliente, cantidad_clientes = restriccion1(clientes_por_camion_resultado, j)
            
            if cantidad_clientes < CANTIDAD_DE_CLIENTES_POR_CAMION:                         #RESTRICCION 1     

                llega_todos = restricion2(cantidad_clientes, camion_cliente, cliente)
                
                if(llega_todos):                                                            #RESTRICCION 2
                
                    tons = restriccion3(p, camion_cliente)

                    if (tons < TONS_MAX_POR_CAMION):
                        
                        clientes_por_camion_resultado[j].append(cliente)
                        clientes_no_asignados_resultado.pop(i)
                        break
        
    #Determino las toneladas asignadas, no asignadas, repartidas y no repartidas 
    toneladas, tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas = calcularToneladas(clientes_por_camion_resultado, clientes_no_asignados_resultado, p)
    
    #Costos
    costo_por_camion, costo_total, costo_por_ton_resultado = costoPorTon(tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas)
   
    return clientes_por_camion_resultado, clientes_no_asignados_resultado, costo_por_ton_resultado

#############################################################################################################

def opt_2(cpc):
    
    #Elijo 2 camiones al azar
    rand1 = random.randint(0, CANTIDAD_DE_CAMIONES-1)
    while True:
        rand2 = random.randint(0, CANTIDAD_DE_CAMIONES-1)
        if rand1 != rand2:
            break
    #genero los 2 camiones
    camion_1 = cpc[rand1]
    camion_2 = cpc[rand2]

    #SELECCIONO UN CLIENTE AL AZAR DE CADA CAMION
    rand_cliente_1 = random.randint(0, len(camion_1) - 1 )
    rand_cliente_2 = random.randint(0, len(camion_2) - 1 )

    #Elimino el cliente del camion    
    cliente_2 = camion_1.pop(rand_cliente_1)
    cliente_1 = camion_2.pop(rand_cliente_2)

    #Verifico que se puedan poner uno en cada lugar]
    #Pruebo si puedo meter al cliente_1 en el camion_2
    llega_list_1 = []
    for cliente in camion_2:
        llega_1 = df_llega.loc[cliente,cliente_2]
        llega_list_1.append(llega_1)
    llega_todos_1 = all(llega_list_1)
    
    llega_list_2 = []
    for cliente in camion_1:
        llega_2 = df_llega.loc[cliente,cliente_1]
        llega_list_2.append(llega_2)
    llega_todos_2 = all(llega_list_2)

    #Si tanto el cliente_1 y el cliente_2 estan a menos de 2km de los otros clientes del camion los asigno cruzo y si no los dejo como estaban
    if(llega_todos_1 and llega_todos_2):
        #Los asigno cruzados
        camion_1.append(cliente_1)
        camion_2.append(cliente_2)
    else:
        #Los dejo como estaban
        camion_1.append(cliente_2)
        camion_2.append(cliente_1)

    #Retorno los clientes por camion
    return cpc

#############################################################################################################

def opt2Optimo(clientes_por_camion_resultado, clientes_no_asignados_resultado, cptr,p):

    clientes_por_camion_min = clientes_por_camion_resultado
    costo_por_ton_min = cptr

    for k in range(1000):
        
        clientes_por_camion = opt_2(clientes_por_camion_min)

        #Determino las toneladas asignadas, no asignadas, repartidas y no repartidas 
        toneladas, tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas = calcularToneladas(clientes_por_camion, clientes_no_asignados_resultado, p)
    
        #Costos
        costo_por_camion, costo_total, costo_por_ton = costoPorTon(tons_repartidas_por_camion, toneladas_no_asignadas, toneladas_no_repartidas, toneladas_repartidas)

        if costo_por_ton < cptr:

            clientes_por_camion_min = clientes_por_camion
            costo_por_ton_min = costo_por_ton

    return clientes_por_camion_min, clientes_no_asignados_resultado, costo_por_ton_min

#############################################################################################################



inicioG = time.time()
lista_de_pedidos = []
for a in datos_prueba:

    print("----------------------- DISTRIBUCION DE PEDIDOS DEL DIA ", a,"------------------------------")
    print(a)
    dia = datos_prueba[a]

    inicio = time.time()

    clientes_por_camion_resultado, clientes_no_asignados_resultado, costo_por_ton_resultado = recocidoSimulado(dia)
    print("##### MEJOR SOLUCION ENCONTRADA POR RECOCIDO SIMULADO")
    #Si quedo algun cliente sin asignar refino la solucion
    if len(clientes_no_asignados_resultado) != 0:
        print("Clientes por camion: ", clientes_por_camion_resultado)
        print("Clientes no asignados: ", clientes_no_asignados_resultado)
        print("Costo por tonelada: ", costo_por_ton_resultado)
        print("Ahorro porcentual: ", 100*(TARIFA_PROMEDIO - costo_por_ton_resultado)/TARIFA_PROMEDIO)
        print("##### SOLUCION REFINADA")
        clientes_por_camion_resultado, clientes_no_asignados_resultado, costo_por_ton_resultado = refino(dia,clientes_por_camion_resultado, clientes_no_asignados_resultado)

    print("Costo por tonelada: ", costo_por_ton_resultado)
  
    print("### 2 OPT")
    clientes_por_camion_resultado, clientes_no_asignados_resultado, costo_por_ton_resultado = opt2Optimo(clientes_por_camion_resultado, clientes_no_asignados_resultado, costo_por_ton_resultado,dia)

    fin = time.time()

    print("Clientes por camion: ", clientes_por_camion_resultado)
    print("Clientes no asignados: ", clientes_no_asignados_resultado)
    print("Costo por tonelada 2OPT: ", costo_por_ton_resultado)
    print("Ahorro porcentual: ", 100*(TARIFA_PROMEDIO - costo_por_ton_resultado)/TARIFA_PROMEDIO)
    print("Tiempo de ejecucion: ", fin - inicio)

    cpc = clientes_por_camion_resultado
    cna = clientes_no_asignados_resultado

    pedidos = datos_prueba[a]
    for i in range(len(cpc)):
        camion = cpc[i]
        for cliente in camion:
            tons = pedidos[cliente]
            new_row = {'Dia/ruteo': a, 'Camion': i+1, 'Cliente': cliente, 'Tons': tons, 'Costo por ton repartida': costo_por_ton_resultado,   }
            lista_de_pedidos.append(new_row)
    for cliente in cna:
            tons = pedidos[cliente]
            new_row = {'Dia/ruteo': a, 'Camion': 'No asignado', 'Cliente': cliente, 'Tons': tons, 'Costo por ton repartida': costo_por_ton_resultado,  }
            lista_de_pedidos.append(new_row)

df_resultados = pd.DataFrame(lista_de_pedidos)
df_resultados.to_csv(DIRECCION_DE_RESULTADOS)

finG = time.time()  

print("TIEMPO TOTAL: ", finG - inicioG)