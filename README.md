Politechnika Świętokrzyska w Kielcach
Wydział Elektrotechniki, Automatyki i Informatyki
Katedra Informatyki Stosowanej
Kierunek:
Informatyka
Laboratorium:
Projekt - Języki Skryptowe


Grupa dziekańska:

3ID15B
Temat projektu
Statki


Wykonał :
Maksymilian Szeląg
Julia Kusztal
Data wykonania:


20.05.2025
Data oddania:

27.05.2025
Ocena i podpis:

1. Opis projektu
Celem projektu było stworzenie sieciowej gry typu statki, umożliwiającej rozgrywkę dwóch graczy w czasie rzeczywistym. Aplikacja została zbudowana w języku Python, z wykorzystaniem bibliotek Pygame (interfejs graficzny) oraz socket (komunikacja sieciowa TCP/IP).

2. Architektura aplikacji
Projekt składa się z dwóch głównych komponentów:
 game.py – Aplikacja kliencka
Graficzny interfejs użytkownika (GUI) zbudowany w Pygame.
Obsługa logiki gry, plansz, rozmieszczania statków i tury graczy.
Komunikacja z serwerem za pomocą gniazda TCP.
 server.py – Serwer gry
Oczekuje na połączenia dwóch graczy.
Przesyła dane między klientami i zarządza turami.
Obsługuje sytuacje końca gry i rozłączenia przeciwnika.



3. Etapy działania gry

a) Ekran początkowy i sposób uruchomienia


Gra jest uruchamiana poprzez skrót na pulpicie(kliknięcie dwukrotnie w ikonę)



Następnie użytkownik wpisuje adres IP serwera.



Po kliknięciu przycisku „CONNECT” następuje próba połączenia z serwerem.


b) Rozmieszczanie statków

Gracz przeciąga statki na swoją planszę.

Statki można obracać prawym przyciskiem myszy.Każdy statek zajmuje odpowiednią liczbę pól (2x, 3x, 4x jednostki).



c) Start gry

Po rozmieszczeniu wszystkich statków gracz ma możliwość kliknięcia przycisku „START” “INFO”. Klikając “INFO” wyskakują nam zasady gry.

Po kliknięciu przycisku “START” gracz sygnalizuje że jest gotowy do rozpoczęcia rozgrywki.
Gra rozpoczyna się, gdy obaj gracze są gotowi (Gracze gotowi: 2/2).


Po rozpoczęciu gry, gracze wykonują ruchy naprzemiennie.





d) Tura gracza

Gracz oddaje strzał na planszy przeciwnika.


Trafienie zaznaczone jest czerwonym kolorem, pudło – niebieskim.


e) Zakończenie gry

Gra kończy się po zatopieniu wszystkich statków przeciwnika.

Wyświetlany jest komunikat o wygranej jak w przykładzie powyżej i w taki sam sposób pojawia się komunikat o przegranej.
(Wygrałeś na tym screenie znajduje się na przycisku info, ponieważ zmniejszyłem okno aplikacji)

Po wygraniu gry, po kilku chwilach przeniesie nas do momentu, gdzie wpisujemy IP, przez co możemy znowu rozpocząć grę na nowo
4. Elementy techniczne
a) Komunikacja klient-serwer
Protokół: TCP/IP


Dane przesyłane są w formie serializowanej (moduł pickle).


Klient nasłuchuje danych w osobnym wątku (threading.Thread).


b) Interfejs graficzny (Pygame)
Plansze o rozmiarze 10x10 pól (każde po 50x50 pikseli).


Dwie plansze: MY BOARD i ENEMY BOARD.


Statki wyświetlane jako obrazy (.png) lub prostokąty w przypadku braku obrazów.


c) Logika rozmieszczania
Zakazane nakładanie statków oraz sąsiadowanie (bufor bezpieczeństwa).


Obsługa przeciągania i upuszczania (drag & drop).


Walidacja poprawnego rozmieszczenia
5. Kody do gry i ich krótkie wytłumaczenie:
Najważniejsze funkcje i ich opisy
Kod game.py
1. reset_game_state()
Resetuje stan gry – czyści plansze, ustawia statki w pozycjach początkowych, zeruje wszystkie zmienne (np. tura, gotowość graczy).



2. draw_grid(offset_x, offset_y)
Rysuje siatkę planszy (linie pionowe i poziome), bazując na podanych współrzędnych początkowych.



3. draw_coordinates(offset_x, offset_y)
Dodaje litery i cyfry do planszy – oznaczenia kolumn i wierszy (A–J, 1–10).



4. draw_button(rect, text)
Rysuje przycisk z podanym tekstem w określonym miejscu.







5. draw_turn_message()
Wyświetla informację czyja tura – gracza lub przeciwnika.



6. draw_game_over_message()
Pokazuje komunikat o wygranej lub przegranej po zakończeniu gry.



7. draw_ships_to_place()
Pokazuje statki do rozmieszczenia na dole ekranu – te, które jeszcze nie zostały ustawione.



8. place_ship_on_board(ship, cell)
Próbuje umieścić statek na planszy w wybranym miejscu. Sprawdza poprawność i unikanie kolizji.



9. get_ship_at_pos(pos)
Zwraca statek, który został kliknięty (jeśli jakiś został trafiony myszką).





10. rotate_ship(ship)
Obraca wybrany statek (zmienia orientację pion/poziom) i aktualizuje jego obrazek.



11. shoot(cell)
Oddaje strzał na pole przeciwnika – zapisuje go lokalnie i wysyła do serwera.



12. get_cell(pos)
Przekształca współrzędne kliknięcia myszki na współrzędne planszy – określa, które pole kliknięto i na której planszy.






13. receive_data()
Nasłuchuje wiadomości z serwera – obsługuje trafienia, tury, koniec gry, gotowość graczy itd. Działa w tle w osobnym wątku.



14. connect_to_server(ip)
Łączy się z serwerem po podanym IP, rozpoczyna komunikację z serwerem i uruchamia odbieranie danych.


kod Server.py
1. get_local_ip()
Pobiera lokalny adres IP komputera, aby móc go wyświetlić i użyć do połączenia klientów.



2. broadcast(message)
Wysyła podaną wiadomość do wszystkich połączonych graczy (klientów). Używane np. do przekazania: „gra rozpoczęta”, „koniec gry”, „gracze gotowi”.




4. start_server()
Uruchamia główną pętlę serwera, w której:
Oczekuje na połączenie dwóch graczy.


Przypisuje im obsługę w osobnych wątkach (handle_client).


Resetuje stan po rozłączeniu.


Obsługuje zamknięcie serwera klawiszem (Ctrl+C).



3. handle_client(client, opponent, player_id)
Główna funkcja do obsługi klienta (gracza). Odbiera dane, analizuje je i przekazuje odpowiednie informacje do przeciwnika lub obu graczy.
Działa w osobnym wątku dla każdego gracza.
Obsługuje:
gotowość do gry,


strzały i odpowiedzi (trafienie/pudło),


przełączenie tury,


zakończenie gry,


rozłączenie gracza.






6. Wnioski
Projekt pozwolił na praktyczne zastosowanie programowania sieciowego, wielowątkowości, grafiki 2D oraz obsługi zdarzeń. Dzięki połączeniu interaktywnego GUI z komunikacją w czasie rzeczywistym, gra jest dynamiczna, intuicyjna i wciągająca.

