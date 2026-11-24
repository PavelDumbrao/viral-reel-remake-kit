const ICONS = (() => {
  let rays = "";
  for (let k = 0; k < 12; k++) rays += `<rect x="46" y="6" width="8" height="40" rx="4" fill="#D97757" transform="rotate(${k * 30} 50 50)"/>`;
  return {
    claude: `<svg viewBox="0 0 100 100">${rays}<circle cx="50" cy="50" r="9" fill="#D97757"/></svg>`,
    obsidian: `<svg viewBox="0 0 100 100"><polygon points="50,4 82,30 74,86 40,96 20,60 32,22" fill="#7C3AED"/><polygon points="50,4 58,48 40,96 20,60 32,22" fill="#A78BFA"/><polygon points="58,48 82,30 74,86 40,96" fill="#5B21B6"/></svg>`,
    playwright: `<svg viewBox="0 0 100 100"><ellipse cx="38" cy="52" rx="30" ry="34" fill="#2EAD33"/><ellipse cx="62" cy="48" rx="30" ry="34" fill="#E2574C"/><circle cx="52" cy="40" r="6" fill="#fff"/><circle cx="72" cy="40" r="6" fill="#fff"/><path d="M52 60 Q62 70 74 60" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="26" cy="46" r="5" fill="#fff"/><circle cx="44" cy="46" r="5" fill="#fff"/></svg>`,
    codex: `<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="#111"/><path d="M30 36 L46 50 L30 64" stroke="#fff" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/><rect x="52" y="60" width="22" height="8" rx="4" fill="#fff"/></svg>`,
    telegram: `<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="48" fill="#2AABEE"/><path d="M22 49 L76 28 L67 74 L50 62 L41 71 L42 58 L68 36 L36 55 Z" fill="#fff"/></svg>`,
    vps: `<svg viewBox="0 0 100 100"><rect x="14" y="12" width="72" height="22" rx="6" fill="#2B2F36"/><rect x="14" y="39" width="72" height="22" rx="6" fill="#2B2F36"/><rect x="14" y="66" width="72" height="22" rx="6" fill="#2B2F36"/><circle cx="26" cy="23" r="4" fill="#3FB950"/><circle cx="26" cy="50" r="4" fill="#3FB950"/><circle cx="26" cy="77" r="4" fill="#F2F24A"/><rect x="40" y="21" width="36" height="4" rx="2" fill="#6B7280"/><rect x="40" y="48" width="36" height="4" rx="2" fill="#6B7280"/><rect x="40" y="75" width="36" height="4" rx="2" fill="#6B7280"/></svg>`,
    banana: `<svg viewBox="0 0 100 100"><path d="M18 30 Q22 78 74 80 Q88 79 84 70 Q46 70 34 28 Q30 18 22 22 Z" fill="#FACC15"/><path d="M18 30 Q14 22 20 18 L26 22 Z" fill="#6B4F12"/><path d="M34 36 Q44 64 76 72" stroke="#EAB308" stroke-width="4" fill="none"/></svg>`,
    kling: `<svg viewBox="0 0 100 100"><defs><linearGradient id="klg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22D3EE"/><stop offset="1" stop-color="#6366F1"/></linearGradient></defs><rect x="8" y="8" width="84" height="84" rx="24" fill="url(#klg)"/><path d="M40 32 L70 50 L40 68 Z" fill="#fff"/></svg>`,
    terminal: `<svg viewBox="0 0 100 100"><rect x="6" y="14" width="88" height="72" rx="12" fill="#111"/><path d="M24 40 L38 50 L24 60" stroke="#3FB950" stroke-width="7" fill="none" stroke-linecap="round"/><rect x="44" y="56" width="26" height="6" rx="3" fill="#fff"/></svg>`,
    check: `<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="#3FB950"/><path d="M28 52 L44 67 L73 36" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    arrowUp: `<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="48" fill="#3B82F6"/><path d="M50 74 L50 28 M30 46 L50 26 L70 46" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    cursor: `<svg viewBox="0 0 100 100"><path d="M20 10 L20 82 L38 66 L50 92 L62 86 L50 61 L74 61 Z" fill="#fff" stroke="#000" stroke-width="5" stroke-linejoin="round"/></svg>`,
  };
})();
