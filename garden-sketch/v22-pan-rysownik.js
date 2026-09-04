(() => {
  const CONTRACT = 'ekoos.garden-polygon';

  function currentPolygon() {
    try {
      const geometry = window.ekoosPlanApi?.geometry?.();
      const sourcePoints = Array.isArray(geometry?.p) && geometry.p.length >= 3 ? geometry.p : pts;
      return Array.isArray(sourcePoints)
        ? sourcePoints
            .map(point => ({ x: Number(point.x), y: Number(point.y) }))
            .filter(point => Number.isFinite(point.x) && Number.isFinite(point.y))
        : [];
    } catch {
      return [];
    }
  }

  function openInPanRysownik() {
    const polygon = currentPolygon();
    if (polygon.length < 3) {
      window.alert('Najpierw zakończ pomiar ogrodu (minimum 3 punkty).');
      return;
    }
    const payload = {
      contract: CONTRACT,
      version: 1,
      unit: 'm',
      source: 'garden-sketch',
      polygon,
      metadata: { orientation: 'garden-sketch-plan' },
    };
    const target = new URL('../pan-rysownik/index.html', window.location.href);
    target.hash = `garden-sketch=${encodeURIComponent(JSON.stringify(payload))}`;
    window.open(target.href, '_blank', 'noopener');
  }

  function install() {
    // Pan Rysownik remains private/local for now, so do not expose a dead
    // integration button in the public GitHub Pages build.
    if (window.location.hostname.endsWith('github.io')) return;

    const result = document.querySelector('#result');
    if (!result) return window.setTimeout(install, 80);
    if (document.querySelector('#openPanRysownik')) return;

    const section = document.createElement('div');
    section.className = 'section';
    section.innerHTML = `
      <h3>Dalsza edycja</h3>
      <p class="muted">Przenieś obrys w rzeczywistej skali do edytora planu.</p>
      <button id="openPanRysownik" class="btn primary" type="button">
        Edytuj w Panu Rysowniku
      </button>`;
    result.appendChild(section);
    section.querySelector('#openPanRysownik').addEventListener('click', openInPanRysownik);
  }

  install();
})();
