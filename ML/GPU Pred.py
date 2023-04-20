import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import sqlite3

# Citirea datelor din fișierul SQLite
connection = sqlite3.connect('./Data/gaming.sqlite')
df = pd.read_sql_query('SELECT * FROM GPU WHERE [Release Year] > 1970 AND [Process Size (nm)] > 0 AND [Core Base Clock] IS NOT NULL AND [Memory Size] IS NOT NULL AND [Memory Bandwidth] IS NOT NULL AND [Memory Clock Speed (Effective)] IS NOT NULL AND [Launch Price ($)] > 0 AND [Launch Price ($)] < 3500', connection)

# Extragerea valorilor numerice din coloanele cu string-uri
# Extragerea valorilor numerice din coloana "Core Boost Clock" și transformarea lor în float
df['Core Base Clock'] = df['Core Base Clock'].str.replace(' MHz', '')
df['Core Base Clock (MHz)'] = df['Core Base Clock'].str.extract('(\d+)').astype(float)

# Înlocuirea valorilor goale ("") din coloana "Core Boost Clock" cu 0
df['Core Boost Clock'].fillna("0", inplace=True)
# Îndepărtarea "MHz" din valorile din coloana "Core Boost Clock"
df['Core Boost Clock'] = df['Core Boost Clock'].str.replace(' MHz', '')
# Extragerea valorilor numerice din coloana "Core Boost Clock" și transformarea lor în float
df['Core Boost Clock (MHz)'] = df['Core Boost Clock'].str.extract('(\d+)').astype(float)


# Înlăturarea partii "(GB/s)" din valorile din coloana "Memory Bandwidth"
df['Memory Bandwidth'] = df['Memory Bandwidth'].str.replace(' GB/s', '', regex=True)
df['Memory Clock Speed (Effective)'] = df['Memory Clock Speed (Effective)'].str.replace(' MHz', '', regex=True)

df['Memory Bandwidth (GB/s)'] = df['Memory Bandwidth'].str.extract('(\d+)').astype(float)  # Adăugarea memoriei bandwidth
df['Memory Clock Speed (Effective, MHz)'] = df['Memory Clock Speed (Effective)'].str.extract('(\d+)').astype(float)  # Adăugarea memoriei bandwidth


# Extrage partea numerică din coloana "Memory Size"
memory_size_numeric = df['Memory Size'].str.extract('(\d+)').astype(float)

# Extrage unitatea de măsură din coloana "Memory Size"
memory_size_unit = df['Memory Size'].str.extract('([a-zA-Z]+)')

# Conversie din MB în GB
memory_size_in_gb = np.where(memory_size_unit == 'MB', memory_size_numeric / 1024, memory_size_numeric)

# Adaugă rezultatul într-o nouă coloană "Memory Size (GB)"
df['Memory Size (GB)'] = memory_size_in_gb

# Șterge coloana "Memory Size" originală, dacă dorești
df.drop('Memory Size', axis=1, inplace=True)


# Separarea datelor în caracteristici (X) și etichete (y)
X = df[['Release Year']].values
#y = df[['Shading Units', 'Process Size (nm)', 'Memory Size (GB)', 'Core Base Clock (MHz)', 'Core Boost Clock (MHz)', 'Launch Price ($)',  'Memory Bandwidth (GB/s)', 'Memory Clock Speed (Effective, MHz)']].values
y = df[['Shading Units', 'Memory Size (GB)', 'Core Base Clock (MHz)', 'Core Boost Clock (MHz)', 'Launch Price ($)',  'Memory Bandwidth (GB/s)']].values


# Separarea datelor în set de antrenare și set de testare
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crearea și antrenarea modelului de regresie liniară
regressor = LinearRegression()
regressor.fit(X_train, y_train)

# Realizarea predicțiilor pe setul de testare
y_pred = regressor.predict(X_test)

# Evaluarea performanței modelului utilizând eroarea medie pătratică (Mean Squared Error)
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

# Salvarea modelului antrenat
joblib.dump(regressor, './ML/model_regresie_liniara.pkl')  # Salvare într-un fișier
