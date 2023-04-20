import joblib
import numpy as np
from sklearn.preprocessing import PolynomialFeatures

# Încărcarea modelului antrenat
regressor = joblib.load('./ML/model_regresie_liniara2.pkl')

# Introducerea datelor de test
X_test = [[2000]]

# Crearea și inițializarea instanței PolynomialFeatures
poly_features = PolynomialFeatures(degree=25)  # Puteți specifica gradul dorit de polinom
poly_features.fit(X_test)  # Apelarea metodei fit() pe datele de test
X_data_poly = poly_features.transform(X_test)

# Realizarea predicției folosind modelul antrenat
y_pred = regressor.predict(X_data_poly)

# Afisarea rezultatelor
print(y_pred)
print("Predictie Number Shading Units:", y_pred[0][0])
print("Predictie Memory Size (GB):", y_pred[0][1])
print("Predictie Core Base Clock (MHz):", y_pred[0][2])
print("Predictie Core Boost Clock (MHz):", y_pred[0][3])
print("Predictie Launch Price ($):", y_pred[0][4])
