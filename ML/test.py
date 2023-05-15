from utils import filter_values
import pandas as pd

txt = []
print(not txt)

txt = [1,2,[2]]
column, operator, values = txt[0:3]
print(column, operator, values)



# Definim datele într-un dicționar
data = {'Nume': ['Ana', 'Bogdan', 'Cristina', 'Dan', 'Elena'],
        'Varsta': [28, 31, 29, 20, 27],
        'Ocupatie': ['Inginer', 'Avocat', 'Inginer', 'Medic', 'Artist']}

# Creăm dataframe-ul
df = pd.DataFrame(data)

# Afisam dataframe-ul
print(len(filter_values(df, [['Varsta', '>', [20]]])))

