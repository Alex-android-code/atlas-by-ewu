(function () {
  const storageKey = "atlas_language";
  const conversationStorageKey = "atlas_conversation_language";
  const supportedLanguages = ["pl", "uk", "ru", "en", "de", "es", "pt"];
  const defaultLanguage = "pl";
  const state = {
    languages: [],
    translations: {},
    currentLanguage: "",
    uiLanguage: "",
    conversationLanguage: "",
  };

  function normalizeLanguageCode(input) {
    if (!input) return "";
    const code = String(input).trim().toLowerCase().split("-")[0].split("_")[0];
    return supportedLanguages.includes(code) ? code : "";
  }

  function isSupportedLanguage(lang) {
    return Boolean(normalizeLanguageCode(lang));
  }

  function getLanguageFromUrl(pathname, searchParams) {
    const path = pathname || window.location.pathname || "/";
    const prefix = normalizeLanguageCode(path.replace(/^\/+/, "").split("/")[0]);
    if (prefix) return prefix;
    const params = searchParams || new URLSearchParams(window.location.search);
    return normalizeLanguageCode(params.get("lang"));
  }

  function getBrowserLanguage() {
    const languages = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""];
    for (const language of languages) {
      const code = normalizeLanguageCode(language);
      if (code) return code;
    }
    return "";
  }

  function getSavedLanguage() {
    return normalizeLanguageCode(localStorage.getItem(storageKey));
  }

  function saveLanguage(lang) {
    const code = normalizeLanguageCode(lang);
    if (code) localStorage.setItem(storageKey, code);
    return code;
  }

  function detectInitialUiLanguage(options = {}) {
    const urlLanguage = normalizeLanguageCode(options.urlLanguage || getLanguageFromUrl(options.pathname, options.searchParams));
    const savedLanguage = normalizeLanguageCode(options.savedLanguage || getSavedLanguage());
    const browserLanguage = normalizeLanguageCode(options.browserLanguage || getBrowserLanguage());
    return urlLanguage || savedLanguage || browserLanguage || defaultLanguage;
  }

  function detectConversationLanguageFromText(text) {
    if (!text) return "unknown";
    const value = String(text).toLowerCase();
    if (/[\u0456\u0457\u0454\u0491]/.test(value) || ["потріб", "шукаю", "працю", "зварюв"].some((word) => value.includes(word))) return "uk";
    if (["работ", "нужн", "ищу", "сотрудник", "сварщик", "зарплат"].some((word) => value.includes(word))) return "ru";
    if (/[\u0105\u0107\u0119\u0142\u0144\u00f3\u015b\u017a\u017c]/.test(value) || ["praca", "pracownik", "spawacz", "potrzeb", "wynagrodz"].some((word) => value.includes(word))) return "pl";
    if (/[\u00e4\u00f6\u00fc\u00df]/.test(value) || ["arbeit", "mitarbeiter", "lohn"].some((word) => value.includes(word))) return "de";
    if (/[\u00f1\u00e1\u00e9\u00ed\u00f3\u00fa]/.test(value) || ["trabajo", "empleados", "salario"].some((word) => value.includes(word))) return "es";
    if (/[\u00e3\u00f5\u00e7]/.test(value) || ["trabalho", "funcion\u00e1rios", "funcionarios", "sal\u00e1rio", "salario"].some((word) => value.includes(word))) return "pt";
    if (["job", "work", "employees", "workers", "salary", "documents"].some((word) => value.includes(word))) return "en";
    return "unknown";
  }
  function t(key, fallback) {
    return state.translations[key] || fallback || key;
  }

  function applyTranslations(root) {
    const scope = root || document;
    scope.querySelectorAll("[data-i18n]").forEach((element) => {
      const key = element.getAttribute("data-i18n");
      element.textContent = t(key);
    });
    scope.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      const key = element.getAttribute("data-i18n-placeholder");
      element.setAttribute("placeholder", t(key));
    });
    scope.querySelectorAll("[data-i18n-title]").forEach((element) => {
      const key = element.getAttribute("data-i18n-title");
      element.setAttribute("title", t(key));
    });
    scope.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
      const key = element.getAttribute("data-i18n-aria-label");
      element.setAttribute("aria-label", t(key));
    });
    scope.querySelectorAll("[data-i18n-value]").forEach((element) => {
      const key = element.getAttribute("data-i18n-value");
      element.setAttribute("value", t(key));
    });
    const titleKey = document.querySelector("meta[name='atlas-title-key']")?.getAttribute("content");
    if (titleKey) document.title = t(titleKey, document.title);
  }

  function renderLanguageSelector(root) {
    const scope = root || document;
    scope.querySelectorAll("[data-language-selector]").forEach((selector) => {
      const button = selector.querySelector("[data-language-button]");
      const menu = selector.querySelector("[data-language-menu]");
      const current = selector.querySelector("[data-language-current]");
      if (!button || !menu || !current) return;

      current.textContent = state.currentLanguage.toUpperCase();
      menu.innerHTML = state.languages.map((language) => `
        <button class="language-option ${language.code === state.currentLanguage ? "active" : ""}" type="button" data-language-code="${language.code}" role="menuitem">
          <span>${language.flag || ""}</span>
          <span>${language.native_name || language.name || language.code}</span>
        </button>
      `).join("");

      if (!button.dataset.i18nBound) {
        button.dataset.i18nBound = "true";
        button.addEventListener("click", () => {
          const isOpen = menu.classList.toggle("open");
          button.setAttribute("aria-expanded", String(isOpen));
        });
      }

      menu.querySelectorAll("[data-language-code]").forEach((option) => {
        option.addEventListener("click", async () => {
          const code = option.getAttribute("data-language-code");
          await setLanguage(code);
          menu.classList.remove("open");
          button.setAttribute("aria-expanded", "false");
        });
      });
    });
  }

  async function fetchBootstrap(language) {
    const params = new URLSearchParams({ browser_language: navigator.language || "" });
    const code = normalizeLanguageCode(language);
    if (code) params.set("selected_language", code);
    const response = await fetch(`/api/i18n/bootstrap?${params.toString()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`i18n bootstrap failed: ${response.status}`);
    return response.json();
  }

  async function load(selectedLanguage, options = {}) {
    const requested = normalizeLanguageCode(selectedLanguage) || detectInitialUiLanguage();
    const data = await fetchBootstrap(requested);
    state.languages = data.languages || [];
    state.translations = data.translations || {};
    state.currentLanguage = normalizeLanguageCode(data.current_language) || requested || defaultLanguage;
    state.uiLanguage = state.currentLanguage;
    state.conversationLanguage = state.uiLanguage;
    if (options.persist !== false) saveLanguage(state.currentLanguage);
    localStorage.setItem(conversationStorageKey, state.conversationLanguage);
    document.documentElement.lang = state.uiLanguage;
    applyTranslations(document);
    renderLanguageSelector(document);
    document.dispatchEvent(new CustomEvent("atlas:i18n", { detail: { ...state } }));
    return state;
  }

  async function setLanguage(language) {
    const code = normalizeLanguageCode(language);
    if (!code) return state;
    saveLanguage(code);
    return load(code);
  }

  function init() {
    return load(detectInitialUiLanguage()).catch((error) => {
      console.warn(error);
      applyTranslations(document);
      return state;
    });
  }

  if (!window.ATLAS_DISABLE_AUTO_I18N) {
    document.addEventListener("click", (event) => {
      if (!event.target.closest("[data-language-selector]")) {
        document.querySelectorAll("[data-language-menu].open").forEach((menu) => menu.classList.remove("open"));
        document.querySelectorAll("[data-language-button]").forEach((button) => button.setAttribute("aria-expanded", "false"));
      }
    });
  }

  window.AtlasI18n = {
    init,
    load,
    setLanguage,
    setUiLanguage: setLanguage,
    t,
    isSupportedLanguage,
    normalizeLanguageCode,
    getLanguageFromUrl,
    getBrowserLanguage,
    getSavedLanguage,
    saveLanguage,
    detectInitialUiLanguage,
    detectConversationLanguageFromText,
    setConversationLanguage(lang) {
      const code = normalizeLanguageCode(lang);
      state.conversationLanguage = code || "unknown";
      if (code) localStorage.setItem(conversationStorageKey, code);
      return state.conversationLanguage;
    },
    supportedLanguages,
    defaultLanguage,
    applyTranslations,
    renderLanguageSelector,
    state,
  };
})();
