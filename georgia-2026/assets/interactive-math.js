(function () {
  "use strict";

  const timers = new WeakMap();
  const revisions = new WeakMap();

  function queueTypeset(element) {
    if (!element) return;
    const revision = (revisions.get(element) || 0) + 1;
    revisions.set(element, revision);
    element.style.visibility = "hidden";
    const previous = timers.get(element);
    if (previous) clearTimeout(previous);
    const timer = setTimeout(() => {
      timers.delete(element);
      const hub = window.MathJax && window.MathJax.Hub;
      if (hub && typeof hub.Queue === "function") {
        hub.Queue(["Typeset", hub, element], () => {
          if (revisions.get(element) === revision) element.style.visibility = "";
        });
      } else {
        element.style.visibility = "";
      }
    }, 35);
    timers.set(element, timer);
  }

  function setMath(element, tex) {
    if (!element || element.dataset.mathTex === tex) return;
    element.dataset.mathTex = tex;
    element.textContent = `\\(${tex}\\)`;
    queueTypeset(element);
  }

  function setHTML(element, html) {
    if (!element || element.dataset.mathHtml === html) return;
    element.dataset.mathHtml = html;
    element.innerHTML = html;
    queueTypeset(element);
  }

  window.NHInteractiveMath = {setMath, setHTML, queueTypeset};
})();
