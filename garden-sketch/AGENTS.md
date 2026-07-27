# Instrukcje rozwoju — Szkic ogrodu

Ten plik jest przeznaczony dla programisty lub agenta kodującego otwierającego projekt w VS Code.

## Najpierw przeczytaj

1. `README.md`
2. `PROJECT_CONTEXT.md`
3. `CHANGELOG.md`

## Aktualna wersja

- Produkcja: `v22.html`
- Wejście publiczne: `index.html`
- Podstawa aplikacji: `v8.html`

Nie traktuj starszych wersji jako osobnych produktów. Są historią szybkiego prototypowania.

## Obecny stos

- HTML,
- CSS,
- JavaScript bez frameworka,
- WebXR,
- ARCore przez Chrome na Androidzie,
- GitHub Pages.

Brak npm, bundlera i kompilacji.

## Najważniejsza zasada

Nie dodawaj kolejnych warstw poprawek bez sprawdzenia, czy dana funkcja istnieje już w innym module. W projekcie występowały problemy z:

- dwiema nakładającymi się miarkami,
- kilkoma wrapperami tej samej funkcji,
- obserwatorami powodującymi pętle,
- loaderami wersji nakładającymi skrypty na `v8.html`.

Przed większą zmianą zalecana jest konsolidacja.

## Zalecana docelowa struktura

```text
garden-sketch/
  index.html
  src/
    app.js
    ar-session.js
    measurement.js
    geometry.js
    live-preview.js
    drafting-guides.js
    result-editor.js
    export-pdf.js
    export-data.js
    ui.js
  styles/
    app.css
    ar.css
    result.css
  docs/
  tests/
```

## Zachowanie, którego nie wolno zepsuć

### Pomiar

- Dodanie punktu nie może zawieszać interfejsu.
- Bieżąca odległość ma aktualizować się na żywo.
- Gdy poprzedni punkt wychodzi poza ekran, taśma ma dochodzić do krawędzi ekranu.
- Gdy poprzedni punkt jest widoczny, nie wolno rysować drugiej nakładającej się taśmy.

### Celownik

- Musi być widoczny nad dolnym panelem.
- Obliczenia promienia muszą odpowiadać jego faktycznej pozycji na ekranie.

### Przeszkody

- Tryb standardowy używa hit-testu, jeśli jest dostępny.
- Przy braku hit-testu może użyć zapamiętanej płaszczyzny gruntu.
- Punkty wyliczone muszą mieć `projected: true` i bursztynowe oznaczenie.

### Domknięcie

- Od około 80 cm może pojawić się podpowiedź.
- Przycisk zamknięcia pojawia się około 25 cm od P1.
- Nie wolno automatycznie podmieniać bieżącego `hit` na P1.
- Dopiero kliknięcie domyka poligon.

### Podgląd i kąty

- P1→P2 jest pionowo w podglądzie na żywo.
- Kąt jest liczony w ostatnim zapisanym wierzchołku.
- Podpowiedzi kąta są informacyjne, bez automatycznego przyciągania.

### Napisy

- Przełącznik `Aa` ukrywa wyłącznie tekst zapisanych boków i punktów.
- Nie może ukrywać bieżącej odległości, kątomierza ani obrysu.

### Wynik i eksport

- Obrys jest centrowany na arkuszu.
- Skala PDF jest rzeczywista.
- Jeśli rysunek nie mieści się w wybranej skali, pokaż błąd zamiast zmieniać skalę po cichu.
- Podziałka liniowa musi odpowiadać skali.

## Testowanie

### Testy na komputerze

Sprawdź:

- tryb ręczny,
- obliczanie powierzchni i obwodu,
- obrót i centrowanie planu,
- dobór skali,
- A4/A3,
- włączanie wymiarów,
- eksport SVG/JSON/XML/PDF.

### Testy na telefonie

Sprawdź na fizycznym Androidzie z ARCore:

1. wykrycie podłoża,
2. dodanie 5–10 punktów,
3. przejście punktu poza ekran,
4. tryb za przeszkodą,
5. kątomierz,
6. przełącznik napisów,
7. powrót do P1 i miękkie domknięcie,
8. zakończenie i eksport.

## Zasady wersjonowania podczas obecnego prototypu

Dopóki nie nastąpi konsolidacja:

1. nie edytuj działającej wersji produkcyjnej bez zachowania kopii,
2. nową wersję testową nazwij kolejnym numerem,
3. po sprawdzeniu zaktualizuj `index.html`,
4. uzupełnij `CHANGELOG.md`,
5. nie ładuj równocześnie starego i nowego modułu realizującego tę samą funkcję.

## Bezpieczeństwo zmian

- Nie zmieniaj repozytorium na prywatne bez uzgodnienia, bo GitHub Pages może przestać działać.
- Nie usuwaj starszych wersji przed konsolidacją i testem nowej wersji.
- Nie zakładaj, że symulacja desktopowa potwierdza działanie WebXR.
