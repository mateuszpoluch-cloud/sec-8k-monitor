# Kontekst projektu — Szkic ogrodu

## Właściciel i zastosowanie

Projekt rozwijany dla Ekoos jako narzędzie pomocnicze do przygotowania podkładu pod projekt automatycznego nawadniania.

Użytkownikiem może być:

- klient wykonujący szkic własnego ogrodu,
- pracownik Ekoos wykonujący pomiar na miejscu,
- projektant przygotowujący koncepcję rozmieszczenia zraszaczy.

## Główne założenie

Aplikacja ma być prostsza niż rozbudowane narzędzia pomiarowe typu CamToPlan. Ma obsługiwać wyłącznie ogród i przygotowanie poligonu trawnika lub innego obszaru.

Priorytety:

1. prosta obsługa jedną ręką,
2. czytelny bieżący pomiar,
3. możliwość pracy mimo przeszkód w ogrodzie,
4. łatwe domknięcie obszaru,
5. czytelny plan 2D w skali,
6. eksport przydatny projektantowi nawadniania.

## Oczekiwany przepływ użytkownika

1. Uruchom pomiar AR.
2. Skieruj telefon na widoczne podłoże.
3. Dodaj P1.
4. Przejdź do kolejnych narożników i dodawaj punkty.
5. Korzystaj z bieżącej długości, linijki oraz podpowiedzi kąta.
6. Przy przeszkodzie włącz tryb wyliczania punktu na płaszczyźnie gruntu.
7. Przy dużej liczbie punktów wyłącz napisy zapisanych boków.
8. Wróć w okolice P1.
9. Gdy aplikacja pokaże miękkie domknięcie, kliknij „Zamknij obszar”.
10. Na ekranie wyniku popraw orientację, skalę, format i widoczność wymiarów.
11. Eksportuj PDF lub dane do dalszego projektu.

## Decyzje UX

### Celownik

Celownik musi znajdować się nad dolnym panelem i pozostawać czytelny na tle obrazu z kamery.

### Bieżąca miarka

Miarka bieżącego odcinka ma pozostawać widoczna również wtedy, gdy poprzedni punkt wyjdzie poza ekran. Nie może powielać standardowej miarki, gdy oba punkty są widoczne.

### Pomiar przez przeszkodę

Telefon nie widzi przez obiekt. Aplikacja przedłuża kierunek celownika do zapamiętanej płaszczyzny gruntu. Punkty wyliczone powinny być oznaczane kolorem bursztynowym.

### Podgląd na żywo

Pierwszy odcinek P1→P2 jest ustawiany pionowo. Dzięki temu użytkownik widzi kształt jak na rysunku technicznym, a nie zgodnie z przypadkową orientacją telefonu.

### Kątomierz

Po zapisaniu co najmniej dwóch punktów aplikacja pokazuje kąt w ostatnim wierzchołku. Wyróżniane są wartości bliskie 45°, 90°, 135° i 180°. Kąt ma pomagać, ale obecnie nie przyciąga punktu automatycznie.

### Domykanie do P1

Domykanie ma być miękkie:

- wcześniejsza informacja o zbliżaniu do P1,
- przycisk dopiero około 25 cm od P1,
- brak automatycznego przeskoku celownika,
- dokładne domknięcie dopiero po kliknięciu.

### Napisy na poligonie

Przełącznik „Aa” ukrywa długości zapisanych boków oraz oznaczenia P1, P2 itd. Nie ukrywa bieżącego pomiaru, kąta ani samego obrysu.

## Wynik i arkusz

Plan wynikowy powinien:

- być centrowany na arkuszu,
- mieć najdłuższy bok poziomo albo P1→P2 poziomo,
- pozwalać na obrót o 90°,
- pozwalać wyłączyć wymiary,
- mieć podziałkę liniową,
- obsługiwać A4 i A3,
- obsługiwać orientację pionową i poziomą,
- zachowywać rzeczywistą skalę,
- ostrzegać, gdy wybrana skala nie mieści rysunku.

## Eksport

Aktualnie:

- PDF — arkusz wektorowy,
- SVG — arkusz wektorowy,
- JSON — dane poligonu,
- XML — dane poligonu.

Docelowo warto dodać eksport kompatybilny bezpośrednio z modułem projektowania Ekoos-Ai.

## Znane problemy techniczne

1. Kod jest podzielony między plik bazowy i kolejne skrypty wersji.
2. Brakuje automatycznych testów geometrii i interfejsu.
3. WebXR nie da się wiarygodnie testować bez urządzenia z ARCore.
4. Długie trasy mogą mieć dryf.
5. Kątomierz jest pomocniczy i nie wymusza geometrii.
6. Brakuje zapisu rozpoczętego pomiaru po zamknięciu karty.
7. Brakuje obsługi wielu osobnych obszarów na jednym projekcie.

## Najbliższy zalecany etap

Przed dalszym dodawaniem funkcji:

1. scalić `v8.html` i skrypty v10–v21 do uporządkowanego katalogu `src`,
2. oddzielić moduły: AR, geometria, podgląd, eksport i UI,
3. dodać prosty zestaw testów geometrii,
4. dodać tryb demonstracyjny bez AR,
5. utrzymywać jedną wersję produkcyjną zamiast kolejnych loaderów.

## Pomysły na dalszy rozwój

- kilka poligonów: trawnik, dom, rabata, kostka, taras,
- oznaczenie źródła wody i skrzynki elektrozaworów,
- automatyczne prostowanie odcinków bliskich 90° jako opcja,
- zapis projektu lokalnie i wznowienie pomiaru,
- wysyłka szkicu bezpośrednio do biura projektowego,
- eksport do formatu wejściowego agenta projektującego zraszacze,
- zdjęcia dokumentacyjne przypisane do punktów lub obszarów.
