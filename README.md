# [PSI] [Zespół 40]

### Miłosz Cieśla, Filip Ryniewicz, Aleksander Szymczyk

# Opis

W repozytorium znajdują się trzy foldery _z1_1_, _z1_2_ oraz _z2_.

## Z1_1

### Struktura

W tym folderze znajdują się cztery podfoldery:

- `client_c`
- `server_c`
- `client_py`
- `server_py`

W każdym z nich znajduje się plik źródłowy odpowiedniego modułu wraz z dockerfilem. Dodatkowo w folderze głównym znajdują się wspólne pliki źródłowe:

- `utils.c`
- `utils.h`
- `utils.py`

Do uruchamiania zadania przeznaczony jest skrypt `start.sh`.

### Uruchamianie

Skrypt `start.sh` ma kilka opcji uruchomienia. Można zobaczyć dostępne opcje poprzez wpisanie nazwy skryptu bez podawania argumentów wywołania.
Skrypt służy do zbudowania obrazów i uruchomienia kontenerów, które komunikują się za pomocą protokołu UDP. \\
Główne opcje:

- py: klient i serwer napisane w python.
- c: klient i serwer napisane w C.
- server-c-client-py: klient napisany w python, serwer w C.
- server-py-client-c: klient napisany w C, serwer w python.

Dodatkowo, uruchamiając `./start.sh clean` usuwane są wszystkie powstałe obrazy, a kontenery są zatrzymywane i również usuwane. Skryptu można także użyć do pojedynczych operacji zbudowania/uruchomienia klienta/serwera w wybranej implementacji.

### Sprawozdanie

W folderze znajduje się również sprawozdanie z zadania w formacie pdf: `z40_sprawozdanie_z1_1.pdf`.

## Z1_2

### Struktura

W tym folderze znajdują się dwa podfoldery:

- `client_py`
- `server_py`

W każdym z nich znajduje się plik źródłowy odpowiedniego modułu wraz z dockerfilem. Dodatkowo w folderze głównym znajdują się pliki:

- `utils.py`
- `docker-compose.yml`

Do uruchamiania zadania przeznaczony jest skrypt `start.sh`.

### Uruchamianie

Skrypt `start.sh` ma kilka opcji uruchomienia. Można zobaczyć dostępne opcje poprzez wpisanie nazwy skryptu bez podawania argumentów wywołania.
Skrypt służy do zbudowania obrazów i uruchomienia kontenerów, które komunikują się za pomocą protokołu UDP. \
Główne opcje:

- py: klient i serwer uruchomione bez zakłóceń.
- disturbance: klient i serwer uruchomione z zakłóceniami. W tej wersji, na początku następuje czyszczenie za pomocą `docker compose down`. Następnie obrazy są budowane i uruchamiane kontenery. Stan uruchomienia kontenera z40_client_container jest sprawdzany w pętli. W momencie wykrycia działającego kontenera, uruchamiane są zakłócenia.

Dodatkowo, uruchamiając `./start.sh clean` usuwane są wszystkie powstałe obrazy, a kontenery są zatrzymywane i również usuwane. Skryptu można także użyć do pojedynczych operacji zbudowania/uruchomienia klienta/serwera w wybranej implementacji.

### Sprawozdanie

W folderze znajduje się również sprawozdanie z zadania w formacie pdf: `z40_sprawozdanie_z1_2.pdf`.


## Z2
### Struktura

W tym folderze znajdują się dwa podfoldery:

- `c`
- `python`

W folderze `c` znajdują się podfoldery `client_c` (plik źródłowy klienta oraz dockerfile) oraz `server_c` (plik źródłowy serwera oraz dockerfile), plik `docker-compose.yml` oraz pliki z funkcjami pomocniczymi `utils.c` i `utils.h`. \
W folderze `python` znajdują się podfoldery `client_py` (plik źródłowy klienta oraz dockerfile) oraz `server_py` (plik źródłowy serwera oraz dockerfile), plik `docker-compose.yml` oraz plik z funkcjami pomocniczymi `utils.py`.

### Uruchamianie

Uruchamianie za pomocą docker compose.
Wersja C:
`docker compose up --build --scale z40_client_c=10` uruchomione w folderze `z2/c`

Wersja Python:
`docker compose up --build --scale z40_client_py=10` uruchomione w folderze `z2/python`

Zatrzymanie poprzez wciśnięcie Ctrl-c.
Usunięcie kontenerów oraz obrazów poprzez wykonanie `docker compose down` w odpowiednim folderze.

### Sprawozdanie

W folderze znajduje się również sprawozdanie z zadania w formacie pdf: `z40_sprawozdanie_z2.pdf`.

