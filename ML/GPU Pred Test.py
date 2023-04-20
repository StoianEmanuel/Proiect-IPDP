import joblib
import numpy as np

# Încărcarea modelului antrenat
regressor = joblib.load('./ML/model_regresie_liniara.pkl')

# Introducerea datelor de test
release_year = 2000

# Transformarea datelor de test într-un vector numpy
X_test = np.array([[release_year]])

# Realizarea predicției folosind modelul antrenat
y_pred = regressor.predict(X_test)

# Afisarea rezultatelor
"""print("Predictie Number Shading Units:", y_pred[0][0])
print("Predictie Process Size (nm):", y_pred[0][1])
print("Predictie Memory Size (GB):", y_pred[0][2])
print("Predictie Core Base Clock (MHz):", y_pred[0][3])
print("Predictie Core Boost Clock (MHz):", y_pred[0][4])
print("Predictie Launch Price ($):", y_pred[0][5])
"""

print("Predictie Number Shading Units:", y_pred[0][0])
print("Predictie Memory Size (GB):", y_pred[0][1])
print("Predictie Core Base Clock (MHz):", y_pred[0][2])
print("Predictie Core Boost Clock (MHz):", y_pred[0][3])
print("Predictie Launch Price ($):", y_pred[0][4])