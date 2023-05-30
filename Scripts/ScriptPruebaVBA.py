import numpy as np
import pandas as pd
import time
import random
import matplotlib.pyplot as plt
import math
import copy

###########################################################################################################

df_distancias = pd.read_csv("Caso II - Matriz de Distancias.csv", delimiter= ",", index_col= 0)
dist_matrix = df_distancias.values
ubicacion_clientes = pd.read_csv("Caso II - Ubicacion Clientes.csv", delimiter= ",", index_col= 0)
datos_prueba = pd.read_csv("Caso II - Set de Datos.csv", delimiter= ",", index_col= 0)
##########################################################################################################

column_mapping = {column_name: int(column_name) for column_name in datos_prueba.columns}
# Reassign columns with new integer names
datos_prueba.rename(columns=column_mapping, inplace=True)
#DEFINO LA MATRIZ LLEGA
def llega(x):
   return True if x <= 2 else False

df_llega = df_distancias.applymap(llega)

