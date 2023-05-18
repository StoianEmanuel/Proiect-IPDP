from consoles_predictions import ConsolePredictor
import pandas as pd

console = ConsolePredictor(database_path = './Data/gaming.sqlite', linear_regressor_path='./ML/consoles_linear_regressor.joblib',
                 polynomial_regressor_path1='./ML/consoles_poly_regressor1.joblib', poly_degree1=2,
                 polynomial_regressor_path2='./ML/consoles_poly_regressor2.joblib', poly_degree2=7)


console.set_data_for_df()

console.prediction_for_consoles(years = [1990, 2000, 2010, 2015, 2020, 2021, 2022, 2023])

console.get_graphs()

console.export_mse_to_file(output_path = './ML/prediction_consoles.txt')

console.add_units_for_prediction_df()

for i in range(0, console.predicted_df.shape[1], 3):
    pd.options.display.max_rows = None
    print(console.predicted_df.iloc[:, i:i+3])