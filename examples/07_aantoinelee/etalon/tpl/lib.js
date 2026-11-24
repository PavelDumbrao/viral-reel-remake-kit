// lib.js — общая библиотека сцен 07 v3 (сборщик вставляет её в каждую сцену вместо плейсхолдера LIB). Иконки — inline SVG.
// В сцене доступны: WORDS (слова сцены: {t,i,s,e} — i сквозной индекс слова голоса, s/e локальное время сцены), D (длительность хоста).
const at = (i) => { const w = WORDS.find((x) => x.i === i); if (!w) throw new Error("нет слова #" + i + " в сцене"); return w.s; };
const atEnd = (i) => { const w = WORDS.find((x) => x.i === i); if (!w) throw new Error("нет слова #" + i + " в сцене"); return w.e; };
// поп-ин как у оригинала (0,16 с, лёгкий перелёт)
function pop(tl, sel, t, from = 0.6) { tl.fromTo(sel, { opacity: 0, scale: from }, { opacity: 1, scale: 1, duration: 0.16, ease: "back.out(2.2)", immediateRender: false }, t); }
function fadeIn(tl, sel, t, y = 18, d = 0.25) { tl.fromTo(sel, { opacity: 0, y }, { opacity: 1, y: 0, duration: d, ease: "power3.out", immediateRender: false }, t); }
function hide(tl, sel, t, d = 0.1) { tl.to(sel, { opacity: 0, duration: d, ease: "power1.in" }, t); }
// рамка «рисуется»: clip-path от центра наружу за 0,22 с
function ring(tl, sel, t) { tl.fromTo(sel, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: 0.18, ease: "power2.out", immediateRender: false }, t); }
// печать текста: прокси-твин → textContent (детерминированно при перемотке)
function typeText(tl, el, text, t, cps = 30) {
  if (typeof el === "string") el = document.querySelector(el);
  const o = { n: 0 };
  tl.to(o, { n: text.length, duration: Math.max(0.05, text.length / cps), ease: "none", onUpdate: () => { el.textContent = text.slice(0, Math.round(o.n)); } }, t);
}
// курсор: перелёт к точке и клик (сжатие)
function clickAt(tl, sel, x, y, t, fly = 0.35) {
  tl.to(sel, { left: x, top: y, duration: fly, ease: "power2.inOut" }, t - fly);
  tl.to(sel, { scale: 0.82, duration: 0.07, yoyo: true, repeat: 1, ease: "power1.inOut" }, t);
}
// вставить SVG-иконку во все элементы [data-icon]
function icons(root) { (root || document).querySelectorAll("[data-icon]").forEach((el) => { if (!el.querySelector("svg")) el.insertAdjacentHTML("afterbegin", ICONS[el.dataset.icon] || ""); }); }
