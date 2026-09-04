# Historia zmian — Szkic ogrodu

## v27 (wersja testowa)

- Poprawiono prowadnicę domknięcia do P1: po przekroczeniu kąta prostego pokazuje wartości rozwarte powyżej 90°, zamiast ponownie je zmniejszać.
- Dodano pomiar wielu niezależnych obszarów trawnika w jednej sesji AR i wspólnym układzie współrzędnych.
- Każdy trawnik może mieć własne przeszkody, odejmowane wyłącznie od jego powierzchni.
- Dodano osobne zestawienie powierzchni trawników oraz ich sumę.
- Wszystkie trawniki są umieszczane na jednym arkuszu i przekazywane do Pana Rysownika jako osobne edytowalne poligony.

## v26 (wersja testowa)

- Dodano rysowanie neutralnych przeszkód jako osobnych poligonów wewnętrznych w tej samej sesji AR.
- Dodano odejmowanie powierzchni przeszkód od powierzchni użytkowej ogrodu.
- Dodano przeszkody do arkusza SVG i eksportu PDF.
- Dodano przeszkody do pliku roboczego JSON i importu w Panu Rysowniku jako osobne edytowalne poligony.

## v25 (wersja testowa)

- Dodano blokadę kierunku pierwszego boku P1→P2 po odejściu minimum 1 m od P1.
- Dodano podgląd bocznej korekty pierwszego boku podczas pomiaru AR.
- Dodano wizualną poziomicę osi P1→P2: odchylenie kątowe, kierunek lewo/prawo i boczną różnicę w metrach.
- Dodano odwracalne prostowanie boków zbliżonych do 90° względem P1→P2.
- Poprawiono prostowanie narożnika domykającego oraz ostatniego boku prowadzącego do P1.
- Usunięto opóźniające wygładzanie bezpośredniego hit-testu, które powodowało odskok zapisywanego punktu od celownika.
- Zrównano pozycję graficznego celownika ze środkiem promienia hit-testu WebXR, usuwając stałe pionowe przesunięcie punktu.
- Eksport do Pana Rysownika zachowuje orientację arkusza Garden Sketch, w tym poziome ustawienie najdłuższego boku.
- Dodano prowadnicę domknięcia do P1 z kierunkiem poza ekranem, odległością i kątem względem osi P1→P2.

## v24 (wersja testowa)

- Dodano przesuwanie całego obrysu na arkuszu z uwzględnieniem pozycji w PDF.
- Dodano zaznaczanie oraz usuwanie pojedynczego wierzchołka z połączeniem sąsiednich boków.
- Dodano łączenie dwóch wybranych skrajnych wierzchołków i usuwanie punktów pomiędzy nimi.
- Dodano automatyczne wykrywanie i usuwanie punktów leżących prawie na jednej prostej.
- Rozszerzono historię o cofanie zmian oraz przywracanie pierwotnego wyniku pomiaru.
- Dodano pełnoekranowy tryb edycji na telefonie, zoom przyciskami i gestem dwóch palców.
- Poprawiono przesuwanie powiększonego arkusza jednym palcem w pustym miejscu rysunku.
- Przeniesiono przesuwanie arkusza na `Pointer Events` i zmieniono klucz cache skryptów, aby telefony nie uruchamiały starszej wersji edytora.
- Dodano siatkę 5 mm z mocniejszym podziałem co 25 mm jako pomoc przy symetrii i wyrównywaniu.
- Dodano pobieranie edytowalnego pliku projektu `.ekoos.json` do importu w aplikacji Pan Rysownik.
- Dodano eksport XSF zgodny ze strukturą `Thor.Common.Designer.Scene`; zawiera poligon `Parcels` bez zraszaczy i sekcji.
- `v23` pozostaje wersją produkcyjną do czasu zakończenia testów.

## v23

- Dodano dotykową edycję wierzchołków bezpośrednio na arkuszu przed eksportem PDF.
- Przeciągnięcie punktu zmienia długości sąsiednich boków i kąt w wierzchołku.
- Po puszczeniu punktu plan, powierzchnia, obwód, wymiary i PDF są przeliczane.
- Dodano cofanie korekt oraz ochronę przed skrzyżowaniem boków.

## v22

- Dodano przycisk przekazujący zmierzony poligon do aplikacji Pan Rysownik.
- Poligon jest przekazywany w metrach przez wersjonowany kontrakt danych.
- Pan Rysownik automatycznie dobiera skalę, centruje obrys i otwiera go jako edytowalny wielokąt.
- Integracja pozostaje ukryta na GitHub Pages, dopóki Pan Rysownik nie zostanie wdrożony prywatnie.

## v21

- Dodano przełącznik `Aa` do ukrywania długości zapisanych boków i oznaczeń punktów.
- Bieżąca miarka, kątomierz i obrys pozostają widoczne.

## v20

- Zmieniono twarde przyciąganie do P1 na miękkie domykanie.
- Podpowiedź pojawia się wcześniej, ale przycisk domknięcia dopiero bardzo blisko P1.
- Usunięto automatyczne przestawianie celownika na P1.

## v19

- Podgląd obrysu na żywo ustawia P1→P2 pionowo.
- Dodano bieżący kąt w ostatnim narożniku.
- Dodano wyróżnienia dla wartości bliskich 45°, 90°, 135° i 180°.

## v18

- Dodano arkusz A4/A3.
- Dodano orientację pionową i poziomą.
- Dodano skalę automatyczną i ręczną.
- Dodano podziałkę liniową.
- Dodano centrowanie, prostowanie i obrót rzutu.
- Dodano wektorowy eksport PDF.
- Dodano przełącznik wymiarów na planie wynikowym.

## v17

- Usunięto powielanie dwóch miar, gdy poprzedni punkt jest widoczny.
- Miarka awaryjna działa tylko dla punktu poza kadrem.

## v16

- Dodano pierwszą wersję magnetycznego domykania do P1.
- Rozwiązanie zostało później złagodzone w v20.

## v15

- Dodano dodatkową taśmę AR, która pozostaje widoczna, gdy poprzedni punkt wychodzi poza ekran.

## v14

- Próba stworzenia niezależnej linijki dolnego panelu.
- Rozwiązanie pomogło rozdzielić problem dolnej skali od taśmy w przestrzeni AR.

## v13

- Uproszczono loader aplikacji i wymuszanie widoczności dolnej linijki.

## v12

- Usunięto agresywny obserwator DOM powodujący zawieszanie przy dodawaniu punktu.

## v11

- Próba stałego wymuszania linijki.
- Wersja powodowała pętlę aktualizacji i zawieszanie interfejsu.

## v10

- Poprawiono obliczanie promienia przez położenie widocznego celownika.
- Dodano podtrzymanie ostatniego pomiaru przy chwilowej utracie śledzenia.

## v9

- Przesunięto celownik nad dolny panel.
- Zmniejszono panel pomiarowy.
- Rozszerzono podtrzymanie pomiaru na zapamiętanej płaszczyźnie gruntu.

## v8

- Dodano automatyczne przejście z bezpośredniego hit-testu na zapamiętaną płaszczyznę gruntu.
- Ta wersja jest obecnie podstawą, na którą nakładane są późniejsze moduły.

## v7

- Dodano tryb pomiaru punktu za przeszkodą.
- Punkty wyliczone oznaczono kolorem bursztynowym.

## v6

- Dodano wirtualną taśmę, podgląd obrysu, zapisane odcinki i tryb poprawiania punktu.

## v4

- Dodano bieżącą linijkę i dużą wartość aktualnego odcinka.

## Pierwszy prototyp

- Pomiar kolejnych punktów WebXR.
- Ręczny tryb testowy.
- Obrys 2D, powierzchnia i obwód.
- Kalibracja znanym wymiarem.
- Eksport SVG, JSON i XML.
