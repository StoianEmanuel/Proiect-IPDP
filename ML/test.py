import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
import joblib
import sqlite3

# Citirea datelor din fișierul SQLite
connection = sqlite3.connect('./Data/gaming.sqlite')
df = pd.read_sql_query('SELECT * FROM GPU', connection)

# Separarea datelor în caracteristici (X) și etichete (y)
X = df[['Release Year']].values
y = df[['Process Size (nm)']].values

degrees = [7, 25, 35]
for degree in degrees:
    # Transformarea caracteristicii "Release Year" în caracteristici polinomiale
    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)

    # Separarea datelor în set de antrenare și set de testare
    X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)

    # Definirea valorilor de alpha pentru căutarea în grilă
    alpha_values = [0.00001, 0.00005, 0.0001, 0.005, 0.001, 0.05, 0.01, 0.5, 0.1, 1, 5, 10, 100]

    # Definirea grilei de parametri pentru căutarea în grilă
    param_grid = {'alpha': alpha_values}

    # Crearea modelului de regresie Ridge
    ridge = Ridge()

    cv = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for val in cv:
        # Realizarea căutării în grilă utilizând validarea încrucișată
        grid_search = GridSearchCV(ridge, param_grid, scoring='neg_mean_squared_error', cv=val)
        grid_search.fit(X_train, y_train)

        # Obținerea parametrilor optimi
        best_alpha = grid_search.best_params_['alpha']
        best_model = grid_search.best_estimator_

        # Antrenarea modelului pe setul de antrenare cu parametrii optimi
        best_model.fit(X_train, y_train)

        # Realizarea predicțiilor pe setul de testare
        y_pred = best_model.predict(X_test)

        # Limitarea valorilor prezise între 0 și o valoare maximă specificată
        max_value = 1000  # Valoare maximă permisă
        y_pred = np.clip(y_pred, 0.5, max_value)

        # Calcularea erorii medie pătratice
        mse = mean_squared_error(y_test, y_pred)
        print(best_alpha)
        print("Eroarea medie patratica (MSE) pe setul de testare:", mse)

        #joblib.dump(best_model, './ML/GPU_Reg_Process.pkl')  # Salvare într-un fișier
        # Realizarea unei predicții pentru anumite valori de intrare
        # X_input reprezintă valorile de intrare pentru caracteristica "Release Year"
        X_input = np.array([[1990], [2000], [2010], [2022], [2023], [2024], [2030]])  # Exemplu de valori de intrare
        X_input_poly = poly_features.transform(X_input)  # Aplicăm transformarea polinomială

        # Realizăm predicțiile utilizând modelul antrenat cu parametrii optimi
        y_pred_input = best_model.predict(X_input_poly)

        y_pred_input_lim = np.clip(y_pred_input, 0.5, 1000)
        # Afisăm predicțiile
        print("\n", degree, val, best_alpha, "Predictii obtinute:", y_pred_input_lim)


#7 12 0.001 / 7 9 0.001 / 7 5 0.001