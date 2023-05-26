# Proiect-IPDP

Rest API (gaming.py) realizat în Python folosind Flask și bază de date SQLite.

1. Endpoint-uri folosite:

- http://127.0.0.1:8086/get_data?data_type=x&snippet=option, endpoint este folosit pentru a extrage un anumit tip da date. x poate fi: consoles, video_games, CPU, GPU, mice. option poate fi: true, false și limitează numărul de elemente obținute din baza de date la primele 20; false pentru a extrage toate datele.
- http://127.0.0.1:8086/get_meta, endpoint folosit pentru a extrage coloanele tabelelor din baza de date folosita
- http://127.0.0.1:8086/get_predictions?data_type=x&years=, endpoint folosit pentru a obține predicții în funcție de parametrul years. x poate fi: consoles, CPU, GPU. years este format dintr-un șir de caractere format din anii pentru care se face prediciția, anii fiind separati prin ",". Ordinea acestora nu contează și dacă nu valorile nu respectă un anumit domeniu nu se vor returna valori pentru aceastea.


2. Structura proiectului:

- Directorul API - partea de Rest API
- Directorul Data - baza de date
- Directorul ML - partea de antrenare și testare a modelelor de machine learning pentru realizarea predicțiilor. Prin cpu_gpu_predicitons se pot salva în fișierele prdicion_cpu.txt și prdicion_gpu.txt valorile MSE pentru fiecare atribut pentru care s-a realizat predicția și vizualiza grafice pentru a analiza mai bine diferența dintre datele folosite pentru antrenare și datele prezise. Pentru testare se folosește console_predictions_test.py. utils.py conține majoritatea funcțiilor folosite pentru formatarea datelor prezise și de antrenare.