(function () {
  "use strict";

  let initialized = false;
  function initialize() {
  if (initialized) return;
  const root = document.getElementById("nh-juno-proton");
  if (!root) return;
  initialized = true;
  const gallery = document.getElementById("juno-sources-and-signals");

  if (gallery) {
    const pauseHiddenVideos = () => {
      gallery.querySelectorAll("video").forEach(video => {
        const panel = video.closest('[id^="tabset-"]');
        if (panel && panel.hidden) video.pause();
      });
      const protonPanel = root.closest('[id^="tabset-"]');
      if (protonPanel && protonPanel.hidden) reset();
    };
    gallery.querySelectorAll('.tab-content > [id^="tabset-"]').forEach(panel => {
      new MutationObserver(pauseHiddenVideos).observe(panel, {
        attributes: true,
        attributeFilter: ["hidden"]
      });
    });
    if (window.Reveal && typeof Reveal.on === "function") {
      Reveal.on("slidechanged", event => {
        if (!event.currentSlide.contains(gallery)) {
          gallery.querySelectorAll("video").forEach(video => video.pause());
        }
      });
    }
  }

  const stage = root.querySelector("[data-juno-phase]");
  const age = root.querySelector("[data-juno-age]");
  const longHand = root.querySelector('[data-juno-hand="long"]');
  const shortHand = root.querySelector('[data-juno-hand="short"]');
  const status = root.querySelector("[data-juno-status]");
  const eventLabel = root.querySelector(".nh-juno-event-label");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const duration = 6500;
  let frameId = null;
  let startedAt = null;
  let candidateRun = false;

  function draw(progress) {
    const fraction = Math.max(0, Math.min(1, progress));
    age.textContent = `${(13.8 * fraction).toFixed(1)} billion years`;
    longHand.style.transform = `rotate(${-90 + 900 * fraction}deg)`;
    shortHand.style.transform = `rotate(${-135 + 180 * fraction}deg)`;
  }

  function stop() {
    if (frameId !== null) cancelAnimationFrame(frameId);
    frameId = null;
    startedAt = null;
  }

  function reset() {
    stop();
    stage.dataset.junoPhase = "ready";
    draw(0);
    eventLabel.textContent = "No proton decay has been observed";
    status.textContent = "Run the cosmic clock: the proton remains. The candidate button then illustrates a possible signal.";
  }

  function complete() {
    stop();
    draw(1);
    if (candidateRun) {
      stage.dataset.junoPhase = "decay";
      eventLabel.textContent = "Hypothetical candidate in JUNO";
      status.textContent = "Illustrative event: a prompt kaon signal, a short-delayed daughter, then a Michel positron. Their spacing is not to scale.";
    } else {
      stage.dataset.junoPhase = "stable";
      eventLabel.textContent = "The proton remains";
      status.textContent = "The clock has crossed 13.8 billion years. No decay is implied by this sweep.";
    }
  }

  function tick(now) {
    if (startedAt === null) startedAt = now;
    const progress = Math.min(1, (now - startedAt) / duration);
    draw(progress);
    if (progress >= 1) complete();
    else frameId = requestAnimationFrame(tick);
  }

  function run(showCandidate) {
    reset();
    candidateRun = showCandidate;
    stage.dataset.junoPhase = "running";
    status.textContent = showCandidate
      ? "Compressing cosmic time before an intentionally triggered hypothetical event."
      : "Compressing one age of the Universe while the proton remains visible.";
    if (reducedMotion.matches) complete();
    else frameId = requestAnimationFrame(tick);
  }

  root.querySelector('[data-juno-action="clock"]').addEventListener("click", () => run(false));
  root.querySelector('[data-juno-action="candidate"]').addEventListener("click", () => run(true));
  root.querySelector('[data-juno-action="reset"]').addEventListener("click", reset);

  if (window.Reveal && typeof Reveal.on === "function") {
    Reveal.on("slidechanged", event => {
      if (!event.currentSlide.contains(root)) reset();
    });
  }
  reset();
  }

  if (window.Reveal && typeof Reveal.on === "function") {
    Reveal.on("ready", initialize);
    if (Reveal.isReady()) initialize();
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, {once: true});
  } else initialize();
})();
