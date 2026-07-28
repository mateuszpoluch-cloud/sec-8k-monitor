(() => {
  const history = [];
  let enabled = false;
  let drag = null;

  function points() {
    try {
      return Array.isArray(pts) ? pts : [];
    } catch {
      return [];
    }
  }

  function snapshot() {
    return points().map(point => ({ ...point }));
  }

  function restore(saved) {
    const target = points();
    target.splice(0, target.length, ...saved.map(point => ({ ...point })));
  }

  function segmentsCross(a, b, c, d) {
    const orient = (p, q, r) =>
      Math.sign((q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x));
    return orient(a, b, c) !== orient(a, b, d) &&
      orient(c, d, a) !== orient(c, d, b);
  }

  function isSimplePolygon(poly) {
    if (poly.length < 3) return false;
    for (let i = 0; i < poly.length; i++) {
      const a = poly[i];
      const b = poly[(i + 1) % poly.length];
      if (Math.hypot(b.x - a.x, b.y - a.y) < 0.03) return false;
      for (let j = i + 1; j < poly.length; j++) {
        if (j === i || j === i + 1 || (i === 0 && j === poly.length - 1)) continue;
        const c = poly[j];
        const d = poly[(j + 1) % poly.length];
        if (segmentsCross(a, b, c, d)) return false;
      }
    }
    return true;
  }

  function angleAt(poly, index) {
    const p = poly[index];
    const before = poly[(index - 1 + poly.length) % poly.length];
    const after = poly[(index + 1) % poly.length];
    const ax = before.x - p.x;
    const ay = before.y - p.y;
    const bx = after.x - p.x;
    const by = after.y - p.y;
    const den = Math.hypot(ax, ay) * Math.hypot(bx, by);
    if (!den) return 0;
    return Math.acos(Math.max(-1, Math.min(1, (ax * bx + ay * by) / den))) * 180 / Math.PI;
  }

  function liveDescription(index) {
    const poly = points();
    const p = poly[index];
    const before = poly[(index - 1 + poly.length) % poly.length];
    const after = poly[(index + 1) % poly.length];
    const previousLength = Math.hypot(p.x - before.x, p.y - before.y);
    const nextLength = Math.hypot(after.x - p.x, after.y - p.y);
    return `P${index + 1} • kąt ${angleAt(poly, index).toFixed(1).replace('.', ',')}° • boki ${previousLength.toFixed(2).replace('.', ',')} m / ${nextLength.toFixed(2).replace('.', ',')} m`;
  }

  function svgPoint(svg, clientX, clientY) {
    const point = svg.createSVGPoint();
    point.x = clientX;
    point.y = clientY;
    return point.matrixTransform(svg.getScreenCTM().inverse());
  }

  function transformFromRendered(poly, vertices) {
    let first = -1;
    let second = -1;
    for (let i = 0; i < poly.length && first < 0; i++) {
      for (let j = i + 1; j < poly.length; j++) {
        if (Math.hypot(poly[j].x - poly[i].x, poly[j].y - poly[i].y) > 0.001) {
          first = i;
          second = j;
          break;
        }
      }
    }
    if (first < 0 || !vertices[first] || !vertices[second]) return null;
    const dx = poly[second].x - poly[first].x;
    const dy = poly[second].y - poly[first].y;
    const du = Number(vertices[second].getAttribute('cx')) - Number(vertices[first].getAttribute('cx'));
    const dv = Number(vertices[second].getAttribute('cy')) - Number(vertices[first].getAttribute('cy'));
    const denominator = dx * dx + dy * dy;
    const A = (du * dx - dv * dy) / denominator;
    const B = (du * dy + dv * dx) / denominator;
    const scaleSquared = A * A + B * B;
    return scaleSquared > 0 ? { A, B, scaleSquared } : null;
  }

  function rerenderPreservingScroll() {
    const top = window.scrollY;
    if (typeof renderResult === 'function') renderResult();
    requestAnimationFrame(() => window.scrollTo(0, top));
  }

  function updateDirectPreview(dx, dy) {
    if (!drag) return;
    const { vertex, handle, label, path, rendered, index } = drag;
    const nextX = drag.startVertex.x + dx;
    const nextY = drag.startVertex.y + dy;
    vertex.setAttribute('cx', nextX);
    vertex.setAttribute('cy', nextY);
    handle.setAttribute('cx', nextX);
    handle.setAttribute('cy', nextY);
    if (label) {
      label.setAttribute('x', nextX + 2.3);
      label.setAttribute('y', nextY - 2.3);
    }
    rendered[index] = { x: nextX, y: nextY };
    path?.setAttribute(
      'd',
      rendered.map((point, i) =>
        `${i ? 'L' : 'M'}${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(' ') + ' Z',
    );
  }

  function onPointerDown(event) {
    if (!enabled || event.button > 0) return;
    const handle = event.target.closest('.plan-edit-handle');
    if (!handle) return;
    const svg = handle.ownerSVGElement;
    const vertices = [...svg.querySelectorAll('circle.vertex:not(.plan-edit-handle)')];
    const poly = snapshot();
    const transform = transformFromRendered(poly, vertices);
    const index = Number(handle.dataset.index);
    if (!transform || !poly[index] || !vertices[index]) return;

    event.preventDefault();
    handle.setPointerCapture(event.pointerId);
    handle.classList.add('dragging');
    const startSvg = svgPoint(svg, event.clientX, event.clientY);
    const labels = [...svg.querySelectorAll('text.point')];
    drag = {
      pointerId: event.pointerId,
      svg,
      handle,
      vertex: vertices[index],
      label: labels[index],
      path: svg.querySelector('path.shape'),
      rendered: vertices.map(vertex => ({
        x: Number(vertex.getAttribute('cx')),
        y: Number(vertex.getAttribute('cy')),
      })),
      startVertex: {
        x: Number(vertices[index].getAttribute('cx')),
        y: Number(vertices[index].getAttribute('cy')),
      },
      startSvg,
      transform,
      index,
      before: poly,
      changed: false,
    };
    document.querySelector('#planEditInfo').textContent = liveDescription(index);
  }

  function onPointerMove(event) {
    if (!drag || event.pointerId !== drag.pointerId) return;
    event.preventDefault();
    const current = svgPoint(drag.svg, event.clientX, event.clientY);
    const du = current.x - drag.startSvg.x;
    const dv = current.y - drag.startSvg.y;
    const { A, B, scaleSquared } = drag.transform;
    const dx = (A * du + B * dv) / scaleSquared;
    const dy = (B * du - A * dv) / scaleSquared;
    const start = drag.before[drag.index];
    points()[drag.index] = { ...start, x: start.x + dx, y: start.y + dy };
    drag.changed = drag.changed || Math.hypot(dx, dy) > 0.002;
    updateDirectPreview(du, dv);
    document.querySelector('#planEditInfo').textContent = liveDescription(drag.index);
  }

  function finishDrag(event) {
    if (!drag || event.pointerId !== drag.pointerId) return;
    const completed = drag;
    completed.handle.classList.remove('dragging');
    drag = null;
    if (!completed.changed) return;

    if (!isSimplePolygon(points())) {
      restore(completed.before);
      try {
        toast('Nie można skrzyżować boków ani połączyć dwóch punktów.');
      } catch {}
    } else {
      history.push(completed.before);
      if (history.length > 20) history.shift();
      try {
        toast(`P${completed.index + 1} poprawiony`);
      } catch {}
    }
    rerenderPreservingScroll();
    updateUndoButton();
  }

  function decoratePreview() {
    const preview = document.querySelector('#preview');
    const svg = preview?.querySelector('svg');
    if (!svg || svg.dataset.planEditorReady === '1') return;
    svg.dataset.planEditorReady = '1';
    svg.classList.toggle('plan-editing', enabled);
    const vertices = [...svg.querySelectorAll('circle.vertex')];
    vertices.forEach((vertex, index) => {
      const handle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      handle.setAttribute('cx', vertex.getAttribute('cx'));
      handle.setAttribute('cy', vertex.getAttribute('cy'));
      handle.setAttribute('r', '4.8');
      handle.setAttribute('class', 'plan-edit-handle');
      handle.dataset.index = String(index);
      svg.appendChild(handle);
    });
    svg.addEventListener('pointerdown', onPointerDown);
    svg.addEventListener('pointermove', onPointerMove);
    svg.addEventListener('pointerup', finishDrag);
    svg.addEventListener('pointercancel', finishDrag);
  }

  function updateUndoButton() {
    const button = document.querySelector('#planEditUndo');
    if (button) button.disabled = history.length === 0;
  }

  function install() {
    const preview = document.querySelector('#preview');
    if (!preview) return setTimeout(install, 80);
    if (document.querySelector('#planEditTools')) return;

    const tools = document.createElement('div');
    tools.id = 'planEditTools';
    tools.innerHTML = `
      <div>
        <strong>Korekta kształtu na arkuszu</strong>
        <span id="planEditInfo">Włącz edycję i przeciągnij zielony punkt palcem.</span>
      </div>
      <div class="plan-edit-actions">
        <button id="planEditToggle" class="btn secondary" type="button" aria-pressed="false">Popraw wierzchołki</button>
        <button id="planEditUndo" class="btn ghost" type="button" disabled>↶ Cofnij korektę</button>
      </div>`;
    preview.before(tools);

    const style = document.createElement('style');
    style.textContent = `
      #planEditTools{display:flex;justify-content:space-between;gap:12px;align-items:center;margin:12px 0 9px;padding:12px 14px;border:1px solid var(--line);border-radius:15px;background:#f5faf7}
      #planEditTools strong,#planEditTools span{display:block}
      #planEditTools span{margin-top:3px;color:var(--mut);font-size:.78rem}
      .plan-edit-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
      .plan-edit-actions .btn{min-height:40px;padding:8px 12px}
      #planEditToggle.active{background:#173f35;color:#fff;border-color:#173f35}
      #preview svg .plan-edit-handle{display:none;fill:#dfff73;fill-opacity:.9;stroke:#173f35;stroke-width:.8;vector-effect:non-scaling-stroke;cursor:grab;pointer-events:all}
      #preview svg.plan-editing{touch-action:none;user-select:none}
      #preview svg.plan-editing .plan-edit-handle{display:block}
      #preview svg.plan-editing .plan-edit-handle.dragging{fill:#fff;stroke:#e09a26;stroke-width:1.3;cursor:grabbing}
      @media(max-width:700px){#planEditTools{align-items:stretch;flex-direction:column}.plan-edit-actions{justify-content:stretch}.plan-edit-actions .btn{flex:1}}
    `;
    document.head.appendChild(style);

    document.querySelector('#planEditToggle').addEventListener('click', event => {
      enabled = !enabled;
      event.currentTarget.classList.toggle('active', enabled);
      event.currentTarget.setAttribute('aria-pressed', String(enabled));
      event.currentTarget.textContent = enabled ? 'Zakończ poprawianie' : 'Popraw wierzchołki';
      document.querySelector('#planEditInfo').textContent = enabled
        ? 'Przeciągnij zielony punkt. Wymiary przeliczą się po puszczeniu.'
        : 'Włącz edycję i przeciągnij zielony punkt palcem.';
      preview.querySelector('svg')?.classList.toggle('plan-editing', enabled);
    });

    document.querySelector('#planEditUndo').addEventListener('click', () => {
      const previous = history.pop();
      if (!previous) return;
      restore(previous);
      rerenderPreservingScroll();
      updateUndoButton();
      try {
        toast('Cofnięto ostatnią korektę');
      } catch {}
    });

    new MutationObserver(decoratePreview).observe(preview, { childList: true });
    decoratePreview();
  }

  install();
})();
