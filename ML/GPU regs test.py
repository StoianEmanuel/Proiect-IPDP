from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from joblib import load
import numpy as np

# Load linear regression model and polynomial regression model
liniar_regressor = load('./ML/GPU_liniar_regressor.joblib')
poly_regressor = load('./ML/GPU_poly_regressor.joblib')

release_year = [1990, 1996, 1999, 2000, 2001, 2002, 2005, 2009, 2010, 2012, 2015, 2020, 2021, 2023, 2025, 2027, 2030] # set used for predictions
X_release_year = np.array(release_year).reshape(-1, 1)

# Generare caracteristici polinomiale pentru valorile de release_year
poly_features = PolynomialFeatures(degree = 2)
X_release_year_poly = poly_features.fit_transform(X_release_year)

# Predictions
liniar_prediction = liniar_regressor.predict(X_release_year)
poly_prediction = poly_regressor.predict(X_release_year_poly)

liniar_prediction = np.exp(liniar_prediction)
poly_prediction = np.exp(poly_prediction)

liniar_prediction[:, 0:-1] = liniar_prediction[:, 0:-1].astype(int)
poly_prediction[:, 0] = poly_prediction[:, 0].astype(int)

concatenated_matrix = np.concatenate((X_release_year, liniar_prediction, poly_prediction), axis=1)

np.set_printoptions(precision=4, suppress=True) # Folosita pentru a imbunatati afisarea in consola
print(concatenated_matrix)
