import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import joblib
import sqlite3
import re

def extract_number_with_reg_expr(string):
    numeric_part = re.findall(r"\d+\.+\d+", string)
    if numeric_part:
        number = float(numeric_part[0])
    else:
        number = -1
    return number

# Functie care returneaza valoarea numerica a fiecarui element din lista
def get_numeric_value(element):
    letters = ['a', 'b', 'c']
    if element.endswith(" Ultimate"):
        return float(element.split(" ")[0]) + 1
    if element[-1] in letters:
        return extract_number_with_reg_expr(element) + (ord(element[-1]) - ord('a'))/10
    if element.startswith("N/A"):
        return -1
    if element.startswith("ES"):                   # daca elementul incepe cu "ES", luam partea numerica de dupa "ES "
        return float(element.split(" ")[1]) - 0.1  # scadem 0.1 pentru a plasa versiunile ES inaintea celor non-ES
    else:
        return float(element)

# Citirea datelor din fișierul SQLite
connection = sqlite3.connect('./Data/gaming.sqlite')
df = pd.read_sql_query('SELECT * FROM GPU WHERE [Release Year] > 1970 AND [Transistors (millions)] > 0 AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [Launch Price ($)] > 0', connection)

MHz = " MHz"
GBps = " GB/s"
MB = "MB"
GB = "GB"
N_A = "N/A"

columns_to_transform = ['Core Base Clock', 'Core Boost Clock', 'Memory Bandwidth', 'Memory Clock Speed (Effective)', 'TDP','Shader Model', 'CUDA', 'OpenCL'], 
"""for column in columns_to_transform:
    df[column].fillna("0", inplace=True)
    df[column] = df[column].str.replace(' MHz', '')"""

# Extragerea valorilor numerice din coloanele cu string-uri si transormarea in float prin indepartarea "MHz"
df['Core Base Clock'] = df['Core Base Clock'].str.replace(MHz, '')
df['Core Base Clock'] = df['Core Base Clock'].str.extract('(\d+)').astype(float)      # rezultat in MHz

# Extragerea valorilor numerice din coloanele cu string-uri si transormarea in float prin indepartarea "MHz"
df['TDP'] = df['TDP'].str.replace(' W', '')
df['TDP'] = df['TDP'].str.extract('(\d+)').astype(float)      # rezultat in MHz

# Înlocuirea valorilor goale ("") din coloana "Core Boost Clock" cu 0
df['Core Boost Clock'].fillna("0", inplace=True)
df['Core Boost Clock'] = df['Core Boost Clock'].str.replace(' MHz', '')
df['Core Boost Clock'] = df['Core Boost Clock'].str.extract('(\d+)').astype(float)    # rezultat in MHz

# Înlăturarea partii "(GB/s)" din valorile din coloana "Memory Bandwidth" si "MHz" din Memory Clock Speed (Effective)
df['Memory Bandwidth'] = df['Memory Bandwidth'].str.replace(' GB/s', '', regex=True)
df['Memory Bandwidth'] = df['Memory Bandwidth'].str.extract('(\d+)').astype(float)  # Adăugarea memoriei bandwidth

df['Memory Clock Speed (Effective)'] = df['Memory Clock Speed (Effective)'].str.replace(' MHz', '', regex=True)
df['Memory Clock Speed (Effective)'] = df['Memory Clock Speed (Effective)'].str.extract('(\d+)').astype(float)  # Adăugarea memoriei bandwidth


# Lista de valori unice din coloana "OpenGL" a DataFrame-ului df
unique_DirectX = df["DirectX"].unique()
unique_OpenGL  = df["OpenGL"].unique()

# Lista ordonata de valori numerice din lista_valori_unice
ord_list_DirectX = sorted(unique_DirectX, key=get_numeric_value)
ord_list_OpenGL  = sorted(unique_OpenGL,  key=get_numeric_value)

# Definirea prioritatilor pe baza listei ordonate
priority_DirectX = {valoare: index for index, valoare in enumerate(ord_list_DirectX)}
priority_OpenGL  = {valoare: index for index, valoare in enumerate(ord_list_OpenGL)}

# Actualizarea valorilor din coloanele "OpenGL" si "DirectX a DataFrame-ului df in functie de prioritati
df["DirectX"] = df["DirectX"].map(priority_DirectX)
df["OpenGL"] = df["OpenGL"].map(priority_OpenGL)

df['OpenCL'] = df['OpenCL'].str.replace('N/A', '0', regex=True)
df['OpenCL'] = df['OpenCL'].str.extract('(\d+)').astype(float)

df['CUDA'] = df['CUDA'].str.replace('N/A', '0', regex=True)
df['CUDA'] = df['CUDA'].str.extract('(\d+)').astype(float)

df['Shader Model'] = df['Shader Model'].str.replace('N/A', '0', regex=True)
df['Shader Model'] = df['Shader Model'].str.extract('(\d+)').astype(float)

# Extrage partea numerică din coloana "Memory Size"
memory_size_numeric = df['Memory Size'].str.extract('(\d+)').astype(float)

# Extrage unitatea de măsură din coloana "Memory Size"
memory_size_unit = df['Memory Size'].str.extract('([a-zA-Z]+)')

# Conversie din MB în GB
memory_size_in_gb = np.where(memory_size_unit == 'MB', memory_size_numeric / 1024, memory_size_numeric)
df['Memory Size'] = memory_size_in_gb

# Definest coloanele folosite in cadrul corelatiei 
keys = ['Release Year', 'Shading Units', 'Transistors (millions)', 'Process Size (nm)', 'Core Base Clock', 'Core Boost Clock', 'Memory Size', 'Memory Bandwidth', 'Memory Clock Speed (Effective)', 'TDP', 'DirectX', 'OpenGL', 'OpenCL', 'Shader Model', 'CUDA']
main_key = ['Launch Price ($)']

# Șterge coloanele neutilizate
coloane_de_sters = list(set(df.columns) - set(keys) - set(main_key))
df = df.drop(columns=coloane_de_sters)

# Calcularea coeficientilor de corelatie
correlation_coefficients = []
for key in keys:
    coefficient, _ = pearsonr(df[main_key].values.flatten(), df[key].values.flatten())
    correlation_coefficients.append(coefficient)

# Returnare set de valori pentru corelatie
correlation_df = pd.DataFrame({'Feature': keys, 'Correlation Coefficient': correlation_coefficients})
correlation_df = correlation_df.sort_values(by='Correlation Coefficient', ascending=False)
print(correlation_df)