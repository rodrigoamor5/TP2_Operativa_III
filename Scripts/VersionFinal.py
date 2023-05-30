import numpy as np
import pandas as pd
import time
import random
import matplotlib.pyplot as plt
import math
import copy

df_distancias = pd.read_csv("Caso II - Matriz de Distancias.csv", delimiter= ",", index_col= 0)
dist_matrix = df_distancias.values
ubicacion_clientes = pd.read_csv("Caso II - Ubicacion Clientes.csv", delimiter= ",", index_col= 0)
datos_prueba = pd.read_csv("Caso II - Set de Datos.csv", delimiter= ",", index_col= 0)
test_data = datos_prueba.values

column_mapping = {column_name: int(column_name) for column_name in datos_prueba.columns}

# Reassign columns with new integer names
datos_prueba.rename(columns=column_mapping, inplace=True)

#DEFINO LA MATRIZ LLEGA
def llega(x):
   return True if x <= 2 else False

df_llega = df_distancias.applymap(llega)

#DEFINIMOS CONSTANTES
#PROBLEMA
TARIFA_PROMEDIO = 1200
AHORRO = 0.05
TARIFA_OBJETIVO = TARIFA_PROMEDIO * (1-AHORRO)
CANTIDAD_DE_CLIENTES_POR_CAMION = 3
CANTIDAD_DE_CAMIONES = 6
TONS_MAX_POR_CAMION = 12
#METAHEURISTICA
CANTIDAD_DE_PEDIDOS_CAMBIAR = 3

#FUNCIONES
#generarSolucionInicial
def generarSolucionInicial(pedidos): #PEDIDOS ES UNA PANDAS SERIES CON LOS PEDIDOS
    #-----------------------CAMBIAR DATOS_PRUEBA 2 ----------------------------------------------------------------------
    pedidos = pedidos[pedidos > 0 ].index #Elimina los clientes con 0 toneladas y toma el index(Nombre de los clientes)
    pedidos = pedidos.to_list() #Lo convierte a lista
    pedidos.pop() #Elimino el ultimo (el total)
    pedidos_por_asignar = pedidos #Asigno todos lo pedidos a pedidos por asignar
    clientes_por_camion = [[] for _ in range(CANTIDAD_DE_CAMIONES)] #Armo la lista con los pedidos de los camiones por cliente
    pedidos_no_asignados = [] #Inicializo un lista con pedidos no asignados
    cantidad_clientes = len(pedidos_por_asignar) 
    for i in range(cantidad_clientes): #Recorro toda la lista de clientes para ese dia
        cliente = pedidos_por_asignar.pop() #Elimino el ultimo cliente de la lista de clientes a la vez que le asigno el cliente eliminado a la variable cliente
        rand = random.randint(0, CANTIDAD_DE_CAMIONES-1) #genero un numero aleatorio entero del 0 al 5
        camion_cliente = clientes_por_camion[rand] #Elijo el camion al aleatoriamente
        cantidad_clientes = len(camion_cliente)
        if cantidad_clientes < CANTIDAD_DE_CLIENTES_POR_CAMION: #Verifico que el camion no tenga 3 clientes
            llega_list = []
            for j in range(cantidad_clientes):
                cliente_en_camion = camion_cliente[j]
                llega = df_llega.loc[cliente_en_camion,cliente]
                llega_list.append(llega)
            llega_array = np.array(llega_list)
            llega_todos = np.prod(llega_array) #Si da 0 es decir que hay al menos un false, entonces no llega a todos
            if(llega_todos):
                clientes_por_camion[rand].append(cliente)
            else:
                pedidos_no_asignados.append(cliente)
        else:
            pedidos_no_asignados.append(cliente)
    return clientes_por_camion, pedidos_no_asignados #Devuelve dos listas ej: ([['A', 'B'],['J', 'H','D'] ] ['C','E','F'])

def pedidosPorCamion(clientes_por_camion, pedidos): #RECIBE UNA LISTA Y UN A PANDAS.SERIES DEVUELVE UNA LIST DE SERIES
    pedidos_por_camion = []
    for camion in clientes_por_camion: #Recorro los clientes por camion
            pedido = pedidos[camion] #Selecciono los pedidos de ese cliente(las tons)
            pedidos_por_camion.append(pedido)
    return pedidos_por_camion #Una lista de pandas.Series

#Calcular costo de la solucion
def tonsRepartidasPorCamion(pedidos_por_camion): #RECIBE UNA LIST DE SERIES Y DEVULEVE UNA LISTA DE NUMEROS
    tons = 0
    tons_repartidas_por_camion = []
    toneladas_no_repartidas = 0
    for pedido in pedidos_por_camion:
        tons = pedido.values.sum()
        if(tons <= TONS_MAX_POR_CAMION):
            tons_repartidas_por_camion.append(tons)
        else:
            tons_repartidas_por_camion.append(TONS_MAX_POR_CAMION)
            toneladas_no_repartidas += tons-TONS_MAX_POR_CAMION
    return tons_repartidas_por_camion, toneladas_no_repartidas

#SUPER OK
def costoPorCamion(tons_repartidas_por_camion):
    costo_por_camion = []
    for tons in tons_repartidas_por_camion:
        costo = float(0)
        if (tons == 0):
            costo = 5000
        elif (tons < 4):
            costo = 5600
        elif (tons < 6.5):
            costo = tons * 1400
        elif (tons < 9.5):
            costo = tons * 1200
        else:
            costo = tons * 1000
        costo_por_camion.append(costo)
    return costo_por_camion

def tonsNoAsignadas(pedidos_no_asignados, pedidos):
    return pedidos[pedidos_no_asignados].values.sum();

def costoTotal(costo_por_camion, tons_no_asignadas_o_no_repartidas):
    costo_total = sum(costo_por_camion) + tons_no_asignadas_o_no_repartidas * 3000
    return costo_total

def tonsRepartidas(tons_repartidas_por_camion):
    tons_repartidas = sum(tons_repartidas_por_camion)
    return tons_repartidas

def generarVecino1(clientes_por_camion, pedidos_por_asignar): #Recibe una list de lists y una list
    pedidos_no_asignados = []
    #---------SACA UN PEDIDO POR CAMION----------
    for i in range(CANTIDAD_DE_CAMIONES):
        clientes_por_camion_i = clientes_por_camion[i]#Seleccionamos los pedidos del camion i
        len_i = len(clientes_por_camion_i) #Veo cuantos pedidos tiene el camion
        if(len_i > 0):
            rand = random.randint(0, len_i-1) #Selecciono el pedido a cambiar
            cliente_eliminado = clientes_por_camion_i.pop(rand)
            #print("Cliente eliminado: ", cliente_eliminado)
            pedidos_por_asignar.append(cliente_eliminado)
 
    #------AGREGA LOS PEDIDOS ALEATORIAMENTE A LOS CAMIONES------
    cantidad_pedidos_por_asignar = len(pedidos_por_asignar)
    for i in range(cantidad_pedidos_por_asignar):
        cliente_a_asignar = pedidos_por_asignar.pop()
        rand = random.randint(0, CANTIDAD_DE_CAMIONES-1)
        camion = clientes_por_camion[rand]
        cantidad_clientes = len(camion)
        if  cantidad_clientes < CANTIDAD_DE_CLIENTES_POR_CAMION:
            llega_list = []
            for j in range(cantidad_clientes):
                cliente_en_camion = camion[j]
                llega = df_llega.loc[cliente_en_camion,cliente_a_asignar]
                llega_list.append(llega)
            llega_array = np.array(llega_list)
            prod = np.prod(llega_array)
            if(prod):
                clientes_por_camion[rand].append(cliente_a_asignar)
            else:
                pedidos_no_asignados.append(cliente_a_asignar)
        else:
            pedidos_no_asignados.append(cliente_a_asignar)
    return  clientes_por_camion, pedidos_no_asignados #Devuelve una list de lists y una list

#HIPERPARÁMETROS DE RECOCIDO SIMULADO
T_INICIAL = 1000
T_FINAL = 10
PASO = -1
ITERACIONES_POR_TEMPERATURA = 10
# clientes_camion,pedidos_no_asignados = generarSolucionInicial(1)
# print(pedidos_no_asignados)
# print(clientes_camion)
pedidos = datos_prueba[5]

def recocidoSimulado(pedidos):
    #INICIALIZACION DE VARIABLES
    clientes_por_camion_min = []
    pedidos_no_asignados_min = []
    costo_por_ton_repartida_min = float('inf')
    pedidos_no_asignados = None
    #pedidos = datos_prueba[1]

    #GENERO LAS SOLUCION INICIAL
    clientes_por_camion, pedidos_no_asignados = generarSolucionInicial(pedidos)
    pedidos_por_camion = pedidosPorCamion(clientes_por_camion, pedidos)
    tons_repartidas_por_camion, tons_no_repartidas = tonsRepartidasPorCamion(pedidos_por_camion = pedidos_por_camion)
    tons_no_asignadas = tonsNoAsignadas(pedidos_no_asignados, pedidos)
    costo_por_camion = costoPorCamion(tons_repartidas_por_camion)
    tons_no_asignadas_o_no_repartidas = tons_no_repartidas + tons_no_asignadas
    #costo_por_camion = costoPorCamion(tons_repartidas_por_camion)
    costo_total = costoTotal(costo_por_camion, tons_no_asignadas_o_no_repartidas)
    tons_repartidas = tonsRepartidas(tons_repartidas_por_camion)
    #CALCULO EL COSTO POR TON REPARTIDA
    costo_por_ton_repartida_1 = costo_total/tons_repartidas
    #print('clientes_por_camion:', clientes_por_camion)
    #print('pedidos_no_asignados:', pedidos_no_asignados)
    clientes_por_camion_1 = clientes_por_camion
    pedidos_no_asignados_1 = pedidos_no_asignados
    clientes_por_camion_min = clientes_por_camion
    pedidos_no_asignados_min = pedidos_no_asignados
    costo_por_ton_repartida_min = costo_por_ton_repartida_1
    print("costo_por_ton_repartida_min:", costo_por_ton_repartida_min)

    for t in range(T_INICIAL, T_FINAL, PASO):
        #print("-----------------Temperatura:", t,"----------------")
        #print("costo_por_ton_repartida_min", costo_por_ton_repartida_min)
        #print("clientes_por_camion_min:", clientes_por_camion_min)
        #print("pedidos_no_asignados_min:", pedidos_no_asignados_min)
        for n in range(ITERACIONES_POR_TEMPERATURA):
            clientes_por_camion, pedidos_no_asignados = generarVecino1(copy.deepcopy(clientes_por_camion_1), copy.deepcopy(pedidos_no_asignados_1))
            #print("clientes_por_camion:", clientes_por_camion)
            #print("pedidos_no_asignados:", pedidos_no_asignados)
            pedidos_por_camion = pedidosPorCamion(clientes_por_camion, pedidos)
            tons_repartidas_por_camion, tons_no_repartidas = tonsRepartidasPorCamion(pedidos_por_camion = pedidos_por_camion)
            tons_no_asignadas = tonsNoAsignadas(pedidos_no_asignados, pedidos)
            costo_por_camion = costoPorCamion(tons_repartidas_por_camion)
            tons_no_asignadas_o_no_repartidas = tons_no_repartidas + tons_no_asignadas
            #costo_por_camion = costoPorCamion(tons_repartidas_por_camion)
            costo_total = costoTotal(costo_por_camion, tons_no_asignadas_o_no_repartidas)
            tons_repartidas = tonsRepartidas(tons_repartidas_por_camion)
            #CALCULO EL COSTO POR TON REPARTIDA
            costo_por_ton_repartida = costo_total/tons_repartidas
            delta = costo_por_ton_repartida_1 - costo_por_ton_repartida #Calculo delta como Sa - Sb
            if delta < 0 : #Si la solucion nueva es peor que la anterio delta < 0
                p = math.e**(delta/t)
                rand_0_1 = random.random()
                #print("p:",  f"{p:.2f}") 
                #print("rand:", f"{rand_0_1:.2f}")
                if p > rand_0_1 :
                    #ACEPTO UNA PEOR SOLUCION
                    ##print("----Tomo solucion peor---")
                    costo_por_ton_repartida_1 = costo_por_ton_repartida
                    pedidos_no_asignados_1 = pedidos_no_asignados
                    clientes_por_camion_1 = clientes_por_camion
                #else:
                    #SE QUEDA CON LA SOLUCION ANTERIOR
                    # costo_por_ton_repartida_1 = copy.copy(costo_por_ton_repartida_1)
                    # pedidos_no_asignados_1 = pedidos_no_asignados_1[:]
                    # clientes_por_camion_1 = clientes_por_camion_1[:]
            else:
                #ACEPTA LA SOLUCION MEJOR
                #ACA ESTA EL PROBLEMA
                costo_por_ton_repartida_1 = costo_por_ton_repartida
                pedidos_no_asignados_1 = pedidos_no_asignados
                clientes_por_camion_1 = clientes_por_camion

            if costo_por_ton_repartida_min > costo_por_ton_repartida:
                #ACTUALIZA A LA MEJOR SOLUCION HASTA AHORA
                costo_por_ton_repartida_min = costo_por_ton_repartida
                clientes_por_camion_min = clientes_por_camion
                pedidos_no_asignados_min = pedidos_no_asignados
            # #print("costo_por_ton_repartida:",costo_por_ton_repartida)
            # print("costo_por_ton_repartida_1:", costo_por_ton_repartida_1)
            # print("clientes_por_camion:", clientes_por_camion)
            # print("Pedidos_no_asignados:", pedidos_no_asignados)
            # print("clientes_por_camion_1:", clientes_por_camion_1)
            # print("pedidos_no_asignados_1:", pedidos_no_asignados_1)


    return costo_por_ton_repartida_min, clientes_por_camion_min, pedidos_no_asignados_min


pedidos = datos_prueba[5]
costo_por_ton_repartida_min, clientes_por_camion_min, pedidos_no_asignados_min = recocidoSimulado(pedidos)
print(costo_por_ton_repartida_min)
print(clientes_por_camion_min)
print(pedidos_no_asignados_min)