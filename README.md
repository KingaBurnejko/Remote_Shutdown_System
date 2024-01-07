# Remote Shutdown System

## Temat Zadania
System zdalnego wyłączania komputerów, który umożliwia serwerowi wysyłanie komend do podłączonych klientów, w tym komendy zamknięcia systemu.

## Protokół Komunikacyjny
Komunikacja między klientem a serwerem odbywa się za pomocą protokołu TCP. Klient po połączeniu z serwerem może odbierać komendy tekstowe, w tym komendy takie jak "shutdown" (wyłączenie systemu) czy "disconnect" (rozłączenie klienta z serwerem).

## Opis Implementacji
Projekt składa się z dwóch głównych części: serwera (`server.c`) i klienta (`client.py`).

### `server.c`
- **Funkcje pomocnicze:** Są to: funkcje do czyszczenia terminala, wyświetlania listy podłączonych klientów i wysyłania komend do klientów.
- **Obsługa klienta (`handle_client`):** Funkcja obsługująca indywidualnego klienta w osobnym wątku. Rejestruje klienta, nasłuchuje, oczekując na wiadomości i zarządza rozłączeniem.
- **Obsługa wejścia serwera (`handle_server_input`):** Oddzielny wątek do obsługi komend wprowadzanych przez operatora serwera.
- **Główna funkcja (`main`):** Ustawia gniazdo serwera, obsługuje połączenia przychodzące i tworzy wątki dla każdego klienta.

### `client.py`
- **Klasa `Client`:** Zarządza połączeniem z serwerem, odbiera i obsługuje wiadomości od serwera, w tym realizację komend takich jak zamknięcie systemu.
- **Klasa `ClientGUI`:** Tworzy interfejs graficzny użytkownika, umożliwiający łączenie i rozłączanie z serwerem oraz wyświetlanie otrzymanych wiadomości.
- **Główna Logika:** Inicjalizuje GUI klienta i uruchamia główną pętlę interfejsu użytkownika.

## Sposób kompilacji, uruchomienia i obsługi programów projektu

### Kompilacja `server.c`
Aby skompilować serwer, potrzebujesz kompilatora GCC. Użyj następującego polecenia:
```
gcc -o server server.c -lpthread
```

### Uruchomienie Serwera
Po skompilowaniu, uruchom serwer używając:
```
./server
```

### Uruchomienie Klienta
Skrypt klienta w Pythonie uruchom przy pomocy polecenia:
```
python client.py
```

## Obsługa Programu
- **Serwer**: Po uruchomieniu serwera, będzie on nasłuchiwał na połączenia od klientów. Możesz wysyłać komendy do wszystkich klientów lub wybranych po ID. Format takiej komendy to: `id_klienta_1,id_klienta_2 treść_komendy`, czyli numery określające id wybranych klientów (wymienione po przecinku) i komenda po spacji. W razie konieczności wysłania komendy do wszystkich klientów jako id wystarczy wpisać 0 (jest to id, które nie zostaje wykorzystane w przypisaniu identyfikatorów dla klientów; jest zarezerwowane do komunikacji ze wszystkimi klientami).

- **Klient**: Po uruchomieniu, GUI umożliwi wpisanie IP serwera oraz numeru portu. Następnie przy pomocy przycisków klient będzie w stanie połączyć się oraz rozłączyć z serwerem. Po połączeniu, komendy wysyłane przez serwer do klienta, będę widoczne na ekranie.

## Uwagi
- Projekt został przygotowany do używania serwera w środowisku Linux oraz klienta bez ograniczeń systemu operacyjnego.
