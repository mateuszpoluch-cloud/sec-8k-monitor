# Szkic ogrodu — Ekoos

Mobilna aplikacja webowa do wykonywania szkicu ogrodu na potrzeby projektu automatycznego nawadniania.

## Aktualna wersja

- Wersja produkcyjna: **v22**
- Punkt wejścia: `garden-sketch/index.html`
- GitHub Pages: `https://mateuszpoluch-cloud.github.io/sec-8k-monitor/garden-sketch/`
- Bezpośredni adres wersji: `https://mateuszpoluch-cloud.github.io/sec-8k-monitor/garden-sketch/v22.html?v=22`

## Cel produktu

Użytkownik chodzi telefonem po granicy trawnika i zapisuje kolejne wierzchołki. Aplikacja tworzy zamknięty poligon, pokazuje wymiary, powierzchnię i obwód, a następnie generuje skalowany arkusz projektu.

To nie jest narzędzie geodezyjne. Ma tworzyć wystarczająco dokładny podkład do koncepcji i projektu systemu nawadniania.

## Najważniejsze funkcje

- pomiar punktów przez WebXR i ARCore,
- bieżąca odległość między ostatnim punktem a celownikiem,
- wirtualna taśma pomiarowa także wtedy, gdy poprzedni punkt wychodzi poza ekran,
- pomiar punktów zasłoniętych przez przeszkody na zapamiętanej płaszczyźnie gruntu,
- podgląd obrysu na żywo z P1→P2 ustawionym pionowo,
- bieżący kąt w narożniku i podpowiedzi 45°, 90°, 135° i 180°,
- miękkie domykanie poligonu do P1,
- przełącznik napisów na już zapisanym poligonie,
- edycja i usuwanie punktów po pomiarze,
- kalibracja całego szkicu jednym znanym wymiarem,
- automatyczne prostowanie i centrowanie rzutu,
- arkusz A4 lub A3, pionowo albo poziomo,
- skala automatyczna lub ręczna,
- podziałka liniowa,
- włączanie i wyłączanie wymiarów,
- eksport PDF, SVG, JSON i XML.

## Uruchomienie lokalne

Aplikacji AR nie należy uruchamiać przez zwykłe otwarcie pliku `index.html`.

WebXR wymaga bezpiecznego kontekstu:

- HTTPS, albo
- `localhost` podczas pracy lokalnej.

Najprostszy test w VS Code:

1. Sklonuj repozytorium.
2. Otwórz katalog `garden-sketch`.
3. Uruchom lokalny serwer, np. rozszerzeniem Live Server.
4. Interfejs 2D można testować na komputerze.
5. Pomiar AR trzeba sprawdzać na telefonie z Androidem, Chrome i obsługą ARCore.

Do testowania telefonu w tej samej sieci lokalnej zwykły adres HTTP komputera może nie wystarczyć. Najpewniejsze jest wdrożenie na GitHub Pages lub lokalny serwer HTTPS.

## Obecna architektura

Projekt jest statyczną aplikacją HTML/CSS/JavaScript bez systemu budowania.

Aktualna wersja jest składana z:

- `v8.html` — podstawowy interfejs i główna logika aplikacji,
- `v10-fix.js` — poprawki wyznaczania punktu i celownika,
- `v17-tape.js` — dodatkowa taśma dla punktu poza ekranem,
- `v20-soft-snap.js` — miękkie domykanie do P1,
- `v18-plan.js` — arkusz A4/A3, skala i PDF,
- `v19-drafting.js` — pionowy podgląd i kątomierz,
- `v21-labels.js` — przełącznik napisów,
- `v22-pan-rysownik.js` — przekazanie poligonu do edytora Pan Rysownik,
- `v22.html` — loader aktualnej wersji,
- `index.html` — przekierowanie do aktualnej wersji.

Integracja z Panem Rysownikiem działa w środowisku lokalnym i pozostaje ukryta
na GitHub Pages do czasu wdrożenia prywatnego edytora.

Ta architektura powstała podczas szybkiego prototypowania. Przed większą rozbudową warto scalić funkcje do jednej uporządkowanej wersji źródłowej.

## Dane punktu

Punkt ma współrzędne lokalne w metrach:

```js
{
  x: 4.25,
  y: 7.10,
  projected: false
}
```

W trybie AR punkt może dodatkowo zawierać współrzędne świata WebXR:

```js
{
  wx: 1.23,
  wy: -0.84,
  wz: -3.11
}
```

`projected: true` oznacza punkt wyliczony na zapamiętanej płaszczyźnie gruntu, a nie uzyskany bezpośrednio z hit-testu ARCore.

## Ważne ograniczenia

- dokładność zależy od telefonu, oświetlenia, tekstury podłoża i jakości śledzenia AR,
- długie pomiary mogą mieć dryf,
- pomiar przez przeszkodę zakłada płaski grunt,
- eksport PDF jest generowany bezpośrednio w przeglądarce,
- testy kamery i WebXR wymagają fizycznego telefonu.

## Dokumentacja uzupełniająca

- `PROJECT_CONTEXT.md` — wymagania produktu, decyzje i dalszy kierunek,
- `CHANGELOG.md` — historia wersji prototypu,
- `AGENTS.md` — zasady pracy dla programisty lub agenta kodującego.
