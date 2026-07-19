"""Personal AI agent onboarding and dashboard screens."""

AGENT_ONBOARDING_HTML = r"""
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ATLAS AI Agent Onboarding</title>
  <style>
    :root {
      --bg: #020714;
      --panel: rgba(255,255,255,0.055);
      --line: rgba(238,241,246,0.14);
      --gold: #d4af37;
      --text: #eef1f6;
      --muted: rgba(238,241,246,0.68);
      --platinum: #cfd6e6;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 20% 0%, rgba(212,175,55,0.16), transparent 28%),
        radial-gradient(circle at 80% 12%, rgba(76,154,255,0.18), transparent 30%),
        linear-gradient(180deg, #020714, #071224 58%, #020714);
    }
    main {
      width: min(960px, 100%);
      margin: 0 auto;
      padding: calc(28px + env(safe-area-inset-top)) clamp(16px, 4vw, 40px) 40px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: clamp(28px, 7vw, 72px);
    }
    .brand {
      color: var(--platinum);
      font-weight: 800;
      letter-spacing: 0.18em;
      font-size: 18px;
    }
    .badge {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--muted);
      font-size: 13px;
      background: rgba(255,255,255,0.04);
    }
    .panel {
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: clamp(22px, 5vw, 44px);
      background: linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.035));
      box-shadow: 0 32px 90px rgba(0,0,0,0.34);
    }
    .eyebrow {
      color: var(--gold);
      font-size: 13px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      margin: 0 0 14px;
    }
    h1 {
      max-width: 780px;
      margin: 0;
      font-size: clamp(34px, 8vw, 76px);
      line-height: 0.98;
      letter-spacing: 0;
    }
    .lead {
      max-width: 680px;
      margin: 20px 0 0;
      color: var(--muted);
      font-size: clamp(16px, 2.4vw, 20px);
      line-height: 1.6;
    }
    .progress {
      height: 8px;
      margin: 28px 0;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(255,255,255,0.09);
    }
    .progress span {
      display: block;
      width: 0%;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #9f7e22, #f5d56a, #b88720);
      transition: width 260ms ease;
    }
    label {
      display: block;
      margin: 0 0 10px;
      color: var(--text);
      font-size: clamp(22px, 5vw, 34px);
      font-weight: 760;
      line-height: 1.15;
    }
    .why {
      margin: 0 0 18px;
      color: var(--muted);
      line-height: 1.55;
    }
    textarea, input {
      width: 100%;
      min-height: 64px;
      border: 1px solid rgba(238,241,246,0.18);
      border-radius: 18px;
      padding: 18px;
      color: var(--text);
      background: rgba(2,7,20,0.72);
      outline: none;
      font: inherit;
      resize: vertical;
    }
    textarea:focus, input:focus {
      border-color: rgba(212,175,55,0.68);
      box-shadow: 0 0 0 4px rgba(212,175,55,0.12);
    }
    .hidden { display: none !important; }
    .upload-card {
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(212,175,55,0.34);
      border-radius: 24px;
      padding: clamp(18px, 4vw, 28px);
      background:
        radial-gradient(circle at 16% 10%, rgba(212,175,55,0.18), transparent 30%),
        linear-gradient(180deg, rgba(255,255,255,0.08), rgba(2,7,20,0.78));
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 22px 60px rgba(0,0,0,0.24);
      transition: border-color 180ms ease, transform 180ms ease, background 180ms ease;
    }
    .upload-card:hover, .upload-card.drag-over {
      border-color: rgba(245,213,106,0.82);
      transform: translateY(-1px);
      background:
        radial-gradient(circle at 16% 10%, rgba(212,175,55,0.26), transparent 34%),
        linear-gradient(180deg, rgba(255,255,255,0.1), rgba(2,7,20,0.76));
    }
    .upload-drop {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 18px;
      align-items: center;
      min-height: 156px;
      cursor: pointer;
      outline: none;
    }
    .upload-drop:focus-visible {
      box-shadow: 0 0 0 4px rgba(212,175,55,0.18);
      border-radius: 18px;
    }
    .upload-icon {
      width: 82px;
      height: 82px;
      border-radius: 22px;
      display: grid;
      place-items: center;
      color: #130f05;
      background: linear-gradient(135deg, #ffe27a, #d4af37 54%, #9f7e22);
      font-size: 34px;
      box-shadow: 0 18px 42px rgba(212,175,55,0.24);
    }
    .upload-title {
      margin: 0 0 6px;
      font-size: clamp(20px, 4vw, 30px);
      font-weight: 800;
      line-height: 1.1;
    }
    .upload-subtitle, .upload-hint, .upload-status, .upload-analysis {
      color: var(--muted);
      line-height: 1.5;
    }
    .upload-hint { margin-top: 8px; font-size: 14px; }
    .upload-file-button {
      width: max-content;
      margin-top: 16px;
      min-height: 46px;
      border-radius: 14px;
    }
    .upload-preview {
      display: grid;
      grid-template-columns: 128px 1fr;
      gap: 18px;
      align-items: center;
    }
    .upload-preview-media {
      width: 128px;
      aspect-ratio: 1;
      overflow: hidden;
      border: 1px solid rgba(238,241,246,0.16);
      border-radius: 22px;
      display: grid;
      place-items: center;
      background: rgba(2,7,20,0.7);
      color: var(--gold);
      font-size: 42px;
      font-weight: 800;
    }
    .upload-preview-media img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .upload-meta { display: grid; gap: 8px; }
    .upload-name {
      margin: 0;
      color: var(--text);
      font-weight: 800;
      overflow-wrap: anywhere;
    }
    .upload-progress {
      height: 8px;
      overflow: hidden;
      border-radius: 999px;
      background: rgba(255,255,255,0.09);
    }
    .upload-progress span {
      display: block;
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, #8db7ff, #f5d56a);
      transition: width 160ms ease;
    }
    .upload-analysis {
      margin: 6px 0 0;
      padding: 12px 14px;
      border: 1px solid rgba(238,241,246,0.12);
      border-radius: 16px;
      background: rgba(255,255,255,0.045);
    }
    .upload-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 12px;
    }
    .upload-actions button {
      min-height: 42px;
      border-radius: 12px;
      padding: 0 14px;
    }
    .upload-error {
      margin-top: 12px;
      color: #ffd0d0;
      line-height: 1.45;
    }
    .actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 20px;
    }
    button, .button {
      min-height: 54px;
      border: 0;
      border-radius: 16px;
      padding: 0 20px;
      cursor: pointer;
      font-weight: 760;
      text-decoration: none;
      display: inline-grid;
      place-items: center;
    }
    .primary {
      color: #130f05;
      background: linear-gradient(135deg, #ffe27a, #d4af37 52%, #a97818);
      box-shadow: 0 18px 45px rgba(212,175,55,0.24);
    }
    .secondary {
      color: var(--text);
      background: rgba(255,255,255,0.06);
      border: 1px solid var(--line);
    }
    .complete {
      display: none;
      margin-top: 18px;
      color: var(--platinum);
      line-height: 1.55;
    }
    @media (max-width: 520px) {
      header { align-items: flex-start; flex-direction: column; }
      .actions > * { width: 100%; }
      .upload-drop,
      .upload-preview {
        grid-template-columns: 1fr;
      }
      .upload-icon,
      .upload-preview-media {
        width: 112px;
      }
      .upload-actions {
        display: grid;
        grid-template-columns: 1fr;
      }
      .upload-actions button,
      .upload-file-button {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">ATLAS by EWU</div>
      <div class="badge" id="step-badge">1 / 15</div>
    </header>
    <section class="panel">
      <p class="eyebrow">Personal AI Agent</p>
      <h1>Створити свого AI-агента</h1>
      <p class="lead">ATLAS починає не з анкети, а з першого інтерв'ю. Ваш агент поступово формує Professional DNA і запам'ятовує важливі відповіді.</p>
      <div class="progress"><span id="progress-bar"></span></div>
      <form id="onboarding-form">
        <label id="question" for="answer"></label>
        <p class="why" id="why"></p>
        <textarea id="answer" autocomplete="off"></textarea>
        <div id="file-upload-host"></div>
        <div class="actions">
          <button class="secondary" id="back" type="button">Назад</button>
          <button class="primary" id="save-answer" type="submit">Зберегти відповідь</button>
          <a class="secondary button" href="/agent/dashboard">У мене вже є агент</a>
        </div>
      </form>
      <div class="complete" id="complete">
        Ваш AI-агент створений. Тепер він починає формувати вашу професійну карту.
        <div class="actions"><a class="primary button" href="/agent/dashboard">Відкрити dashboard агента</a></div>
      </div>
    </section>
  </main>
  <script>
    const params = new URLSearchParams(location.search);
    const language = params.get("lang") || localStorage.getItem("atlas_language") || "uk";
    const userId = localStorage.getItem("atlas_user_id") || `user-${crypto.randomUUID()}`;
    localStorage.setItem("atlas_user_id", userId);
    let fields = [];
    let index = Number(localStorage.getItem("atlas_agent_onboarding_index") || 0);
    const answers = JSON.parse(localStorage.getItem("atlas_agent_onboarding_answers") || "{}");
    const question = document.getElementById("question");
    const why = document.getElementById("why");
    const answer = document.getElementById("answer");
    const badge = document.getElementById("step-badge");
    const bar = document.getElementById("progress-bar");
    const back = document.getElementById("back");
    const complete = document.getElementById("complete");
    const form = document.getElementById("onboarding-form");
    const saveButton = document.getElementById("save-answer");
    const fileUploadHost = document.getElementById("file-upload-host");
    const fileConfigs = {
      profile_photo: {
        endpoint: "/api/onboarding/profile-photo",
        deleteEndpoint: "/api/onboarding/profile-photo",
        accept: "image/png,image/jpeg,image/heic,image/heif,.png,.jpg,.jpeg,.heic,.heif",
        extensions: [".png", ".jpg", ".jpeg", ".heic", ".heif"],
        maxBytes: 10 * 1024 * 1024,
        icon: "📷",
        title: "Перетягніть фотографію сюди",
        subtitle: "Натисніть, щоб вибрати файл",
        hint: "PNG • JPG • JPEG • HEIC • до 10 MB",
        button: "Прикріпити файл",
        previewType: "image",
        emptyError: "Додайте фото, щоб продовжити створення Professional DNA."
      },
      uploaded_cv: {
        endpoint: "/api/onboarding/cv",
        deleteEndpoint: "/api/onboarding/cv",
        accept: ".pdf,.doc,.docx,.odt,.rtf,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.oasis.opendocument.text,application/rtf,text/rtf",
        extensions: [".pdf", ".doc", ".docx", ".odt", ".rtf"],
        maxBytes: 15 * 1024 * 1024,
        icon: "📎",
        title: "Перетягніть CV сюди",
        subtitle: "Натисніть, щоб вибрати файл",
        hint: "PDF • DOC • DOCX • ODT • RTF • до 15 MB",
        button: "Прикріпити файл",
        previewType: "document",
        emptyError: "Завантажте CV, щоб ATLAS підготував дані для підтвердження."
      }
    };
    const uploadState = {};

    async function loadSchema() {
      const response = await fetch(`/api/agent/onboarding/schema?language=${encodeURIComponent(language)}`);
      const data = await response.json();
      fields = data.fields;
      render();
    }

    function render() {
      const field = fields[index];
      if (!field) return;
      question.textContent = field.question;
      why.textContent = field.why;
      answer.value = typeof answers[field.key] === "string" ? answers[field.key] : "";
      badge.textContent = `${field.step} / ${field.total}`;
      bar.style.width = `${Math.round((index / fields.length) * 100)}%`;
      back.disabled = index === 0;
      const config = fileConfigs[field.key];
      answer.classList.toggle("hidden", Boolean(config));
      fileUploadHost.innerHTML = "";
      if (config) {
        uploadState[field.key] = uploadState[field.key] || {file: answers[field.key] || null, progress: 0, status: answers[field.key] ? "success" : "idle"};
        renderUpload(field, config);
      }
      updateSaveState(field);
    }

    back.addEventListener("click", () => {
      if (index > 0) {
        index -= 1;
        localStorage.setItem("atlas_agent_onboarding_index", String(index));
        render();
      }
    });

    document.addEventListener("paste", (event) => {
      const field = fields[index];
      const config = field && fileConfigs[field.key];
      if (!config || !event.clipboardData?.files?.length) return;
      handleSelectedFile(field, config, event.clipboardData.files[0]);
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const field = fields[index];
      if (fileConfigs[field.key] && !answers[field.key]?.id) {
        renderUploadError(field, fileConfigs[field.key].emptyError);
        updateSaveState(field);
        return;
      }
      if (!fileConfigs[field.key]) {
        answers[field.key] = answer.value.trim();
      }
      localStorage.setItem("atlas_agent_onboarding_answers", JSON.stringify(answers));
      await fetch("/api/agent/onboarding/answer", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({user_id: userId, field: field.key, value: answers[field.key], language})
      });
      if (index < fields.length - 1) {
        index += 1;
        localStorage.setItem("atlas_agent_onboarding_index", String(index));
        render();
      } else {
        await fetch("/api/agent/onboarding/complete", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({user_id: userId})
        });
        bar.style.width = "100%";
        form.style.display = "none";
        complete.style.display = "block";
      }
    });

    function renderUpload(field, config) {
      const state = uploadState[field.key];
      const file = state.file;
      fileUploadHost.innerHTML = `
        <section class="upload-card" id="upload-card-${field.key}">
          <input class="hidden" id="upload-input-${field.key}" type="file" accept="${config.accept}" />
          ${file ? uploadedTemplate(field, config, state) : emptyUploadTemplate(field, config, state)}
          <div class="upload-error" id="upload-error-${field.key}">${escapeHtml(state.error || "")}</div>
        </section>
      `;
      const card = document.getElementById(`upload-card-${field.key}`);
      const input = document.getElementById(`upload-input-${field.key}`);
      const drop = card.querySelector(".upload-drop");
      const attach = card.querySelector("[data-action='attach']");
      const replace = card.querySelector("[data-action='replace']");
      const remove = card.querySelector("[data-action='delete']");
      const view = card.querySelector("[data-action='view']");
      const retry = card.querySelector("[data-action='retry']");

      [drop, attach, replace].filter(Boolean).forEach(element => {
        element.addEventListener("click", () => input.click());
        element.addEventListener("keydown", (event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            input.click();
          }
        });
      });
      input.addEventListener("change", () => {
        if (input.files?.[0]) handleSelectedFile(field, config, input.files[0]);
      });
      card.addEventListener("dragover", (event) => {
        event.preventDefault();
        card.classList.add("drag-over");
      });
      card.addEventListener("dragleave", () => card.classList.remove("drag-over"));
      card.addEventListener("drop", (event) => {
        event.preventDefault();
        card.classList.remove("drag-over");
        if (event.dataTransfer?.files?.[0]) handleSelectedFile(field, config, event.dataTransfer.files[0]);
      });
      remove?.addEventListener("click", () => deleteUploadedFile(field, config));
      view?.addEventListener("click", () => viewUploadedFile(field));
      retry?.addEventListener("click", () => {
        if (state.lastFile) handleSelectedFile(field, config, state.lastFile);
      });
    }

    function emptyUploadTemplate(field, config, state) {
      return `
        <div class="upload-drop" role="button" tabindex="0" aria-label="${escapeHtml(config.button)}">
          <div class="upload-icon">${config.icon}</div>
          <div>
            <p class="upload-title">${escapeHtml(config.title)}</p>
            <div class="upload-subtitle">${escapeHtml(config.subtitle)}</div>
            <div class="upload-hint">${escapeHtml(config.hint)}</div>
            <button class="primary upload-file-button" data-action="attach" type="button">${escapeHtml(config.button)}</button>
            ${state.status === "loading" ? progressTemplate(state.progress) : ""}
          </div>
        </div>
      `;
    }

    function uploadedTemplate(field, config, state) {
      const file = state.file;
      const preview = config.previewType === "image" && file.previewUrl
        ? `<img src="${file.previewUrl}" alt="Фото профілю" />`
        : `<span>${config.previewType === "image" ? "A" : "CV"}</span>`;
      const status = state.status === "loading" ? "Завантаження..." : "Завантажено";
      return `
        <div class="upload-preview">
          <div class="upload-preview-media">${preview}</div>
          <div class="upload-meta">
            <p class="upload-name">${escapeHtml(file.original_name || file.name || "Файл")}</p>
            <div class="upload-status">${formatBytes(file.size || 0)} • ${status}${file.created_at ? " • " + new Date(file.created_at).toLocaleDateString("uk-UA") : ""}</div>
            ${state.status === "loading" ? progressTemplate(state.progress) : ""}
            ${analysisTemplate(file.analysis)}
            <div class="upload-actions">
              <button class="secondary" data-action="view" type="button">Переглянути</button>
              <button class="secondary" data-action="replace" type="button">Замінити</button>
              <button class="secondary" data-action="delete" type="button">Видалити</button>
              ${state.status === "error" ? `<button class="secondary" data-action="retry" type="button">Повторити</button>` : ""}
            </div>
          </div>
        </div>
      `;
    }

    function progressTemplate(progress) {
      return `<div class="upload-progress" aria-label="Upload progress"><span style="width:${Math.max(8, progress || 8)}%"></span></div>`;
    }

    function analysisTemplate(analysis) {
      if (!analysis?.message) return "";
      const extracted = analysis.extracted ? Object.entries(analysis.extracted)
        .filter(([, value]) => value && (!Array.isArray(value) || value.length))
        .slice(0, 5)
        .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : value}`)
        .join(" • ") : "";
      return `<div class="upload-analysis">${escapeHtml(analysis.message)}${extracted ? `<br>${escapeHtml(extracted)}` : ""}</div>`;
    }

    async function handleSelectedFile(field, config, selectedFile) {
      const validation = validateClientFile(selectedFile, config);
      if (validation) {
        uploadState[field.key] = {...(uploadState[field.key] || {}), error: validation, status: "error", lastFile: selectedFile};
        renderUpload(field, config);
        updateSaveState(field);
        return;
      }
      const previousFileId = answers[field.key]?.id;
      const state = uploadState[field.key] = {file: localFileInfo(selectedFile, config), progress: 12, status: "loading", error: "", lastFile: selectedFile};
      renderUpload(field, config);
      updateSaveState(field);
      const timer = setInterval(() => {
        state.progress = Math.min(92, state.progress + 13);
        renderUpload(field, config);
      }, 180);
      try {
        const body = new FormData();
        body.append("file", selectedFile);
        const response = await fetch(config.endpoint, {
          method: "POST",
          headers: {"X-ATLAS-User-Id": userId},
          body
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok || !result.success) throw new Error(result.detail || "Не вдалося завантажити файл.");
        clearInterval(timer);
        state.progress = 100;
        state.status = "success";
        state.file = {...result.file, previewUrl: state.file.previewUrl, name: selectedFile.name};
        answers[field.key] = state.file;
        localStorage.setItem("atlas_agent_onboarding_answers", JSON.stringify(answers));
        if (previousFileId && previousFileId !== state.file.id) deleteServerFile(config, previousFileId);
        renderUpload(field, config);
      } catch (error) {
        clearInterval(timer);
        state.status = "error";
        state.error = error.message || "Не вдалося завантажити файл.";
        renderUpload(field, config);
      }
      updateSaveState(field);
    }

    function localFileInfo(file, config) {
      const lowerName = file.name.toLowerCase();
      const canPreview = config.previewType === "image" && !lowerName.endsWith(".heic") && !lowerName.endsWith(".heif");
      return {
        name: file.name,
        original_name: file.name,
        size: file.size,
        previewUrl: canPreview ? URL.createObjectURL(file) : "",
        analysis: {message: "Завантаження..."}
      };
    }

    async function deleteUploadedFile(field, config) {
      const fileId = answers[field.key]?.id || uploadState[field.key]?.file?.id;
      if (fileId) await deleteServerFile(config, fileId);
      delete answers[field.key];
      uploadState[field.key] = {file: null, progress: 0, status: "idle"};
      localStorage.setItem("atlas_agent_onboarding_answers", JSON.stringify(answers));
      renderUpload(field, config);
      updateSaveState(field);
    }

    async function deleteServerFile(config, fileId) {
      await fetch(`${config.deleteEndpoint}/${encodeURIComponent(fileId)}`, {
        method: "DELETE",
        headers: {"X-ATLAS-User-Id": userId}
      }).catch(() => {});
    }

    async function viewUploadedFile(field) {
      const file = answers[field.key] || uploadState[field.key]?.file;
      if (!file?.url) return;
      const response = await fetch(file.url, {headers: {"X-ATLAS-User-Id": userId}});
      if (!response.ok) return;
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      window.open(blobUrl, "_blank", "noopener");
      setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
    }

    function validateClientFile(file, config) {
      if (!file || file.size <= 0) return "Файл порожній. Прикріпіть інший файл.";
      if (file.size > config.maxBytes) return `Файл завеликий. Максимальний розмір - ${formatBytes(config.maxBytes)}.`;
      const lowerName = file.name.toLowerCase();
      if (!config.extensions.some(extension => lowerName.endsWith(extension))) {
        return `Непідтримуваний формат. Дозволено: ${config.extensions.join(", ")}.`;
      }
      return "";
    }

    function updateSaveState(field) {
      const config = fileConfigs[field.key];
      saveButton.disabled = Boolean(config) && (!answers[field.key]?.id || uploadState[field.key]?.status === "loading");
    }

    function renderUploadError(field, message) {
      uploadState[field.key] = {...(uploadState[field.key] || {}), error: message};
      renderUpload(field, fileConfigs[field.key]);
    }

    function formatBytes(bytes) {
      if (!bytes) return "0 MB";
      return `${(bytes / (1024 * 1024)).toFixed(bytes > 1024 * 1024 ? 1 : 2)} MB`;
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      })[char]);
    }

    loadSchema();
  </script>
</body>
</html>
"""


AGENT_DASHBOARD_HTML = r"""
<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ATLAS AI Agent Dashboard</title>
  <style>
    :root {
      --bg: #020714;
      --panel: rgba(255,255,255,0.06);
      --line: rgba(238,241,246,0.14);
      --gold: #d4af37;
      --text: #eef1f6;
      --muted: rgba(238,241,246,0.68);
      --platinum: #cfd6e6;
    }
    * { box-sizing: border-box; min-width: 0; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 20% -10%, rgba(212,175,55,0.15), transparent 26%),
        radial-gradient(circle at 80% 0%, rgba(76,154,255,0.13), transparent 28%),
        #020714;
    }
    main {
      width: min(1180px, 100%);
      margin: 0 auto;
      padding: calc(24px + env(safe-area-inset-top)) clamp(16px, 4vw, 40px) 40px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 26px;
    }
    .brand { color: var(--platinum); font-weight: 800; letter-spacing: 0.18em; }
    .button {
      min-height: 44px;
      border-radius: 14px;
      padding: 0 16px;
      display: inline-grid;
      place-items: center;
      color: #130f05;
      background: linear-gradient(135deg, #ffe27a, #d4af37 52%, #a97818);
      text-decoration: none;
      font-weight: 760;
    }
    .hero {
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 18px;
      align-items: stretch;
    }
    .panel, .card {
      border: 1px solid var(--line);
      border-radius: 24px;
      background: linear-gradient(180deg, rgba(255,255,255,0.085), rgba(255,255,255,0.035));
      box-shadow: 0 26px 80px rgba(0,0,0,0.28);
    }
    .panel { padding: clamp(22px, 4vw, 38px); }
    .eyebrow { color: var(--gold); text-transform: uppercase; letter-spacing: 0.16em; font-size: 12px; margin: 0 0 12px; }
    h1 { margin: 0; font-size: clamp(34px, 7vw, 72px); line-height: 1; letter-spacing: 0; }
    .lead { color: var(--muted); max-width: 680px; line-height: 1.6; font-size: clamp(16px, 2vw, 19px); }
    .meter { height: 10px; overflow: hidden; border-radius: 999px; background: rgba(255,255,255,0.09); }
    .meter span { display: block; width: 0%; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #9f7e22, #f5d56a, #b88720); }
    .status { color: var(--platinum); font-size: 18px; font-weight: 760; }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 16px;
    }
    .card { padding: 18px; }
    .card h2, .card h3 { margin: 0 0 10px; }
    .card p, li { color: var(--muted); line-height: 1.55; }
    ul { padding-left: 18px; margin: 0; }
    .tag {
      display: inline-flex;
      margin-top: 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
      color: var(--muted);
      font-size: 12px;
    }
    @media (max-width: 860px) {
      .hero, .grid { grid-template-columns: 1fr; }
      header { align-items: flex-start; flex-direction: column; }
      .button { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">ATLAS by EWU</div>
      <a class="button" href="/agent/onboarding">Продовжити інтерв'ю</a>
    </header>
    <section class="hero">
      <div class="panel">
        <p class="eyebrow">Personal AI Agent</p>
        <h1>Ваш AI-агент</h1>
        <p class="lead" id="agent-activity">Завантажую стан агента...</p>
        <p class="status" id="agent-status"></p>
        <div class="meter"><span id="dna-meter"></span></div>
        <p class="lead" id="next-action"></p>
      </div>
      <div class="panel">
        <p class="eyebrow">Professional DNA</p>
        <h2 id="dna-percent">0%</h2>
        <p class="lead">Це не CV, а цифровий професійний профіль, який агент поступово наповнює фактами, цілями, документами та рекомендаціями.</p>
        <span class="tag">Тестовий режим</span>
      </div>
    </section>
    <section class="grid" id="modules"></section>
  </main>
  <script>
    const userId = localStorage.getItem("atlas_user_id") || `user-${crypto.randomUUID()}`;
    localStorage.setItem("atlas_user_id", userId);

    async function loadDashboard() {
      const response = await fetch(`/api/agent/dashboard/${encodeURIComponent(userId)}`);
      const data = await response.json();
      document.getElementById("agent-activity").textContent = data.agent.activity;
      document.getElementById("agent-status").textContent = data.agent.status;
      document.getElementById("next-action").textContent = data.agent.next_recommended_action;
      document.getElementById("dna-percent").textContent = `${data.agent.profile_completeness}%`;
      document.getElementById("dna-meter").style.width = `${data.agent.profile_completeness}%`;
      const modules = document.getElementById("modules");
      modules.innerHTML = "";
      data.modules.forEach((module) => {
        const card = document.createElement("article");
        card.className = "card";
        card.innerHTML = `<h3>${module.title}</h3><p>${descriptionFor(module.key)}</p><span class="tag">${statusLabel(module.status)}</span>`;
        modules.appendChild(card);
      });
    }

    function statusLabel(status) {
      if (status === "active") return "Працює";
      if (status === "test_mode") return "Тестовий режим";
      return "У розробці";
    }

    function descriptionFor(key) {
      const descriptions = {
        my_ai_agent: "Статус агента, остання активність, журнал дій і можливість почати діалог.",
        professional_dna: "Професійний профіль, відсоток заповнення, відсутні дані та статус перевірки.",
        opportunities: "Рекомендовані вакансії, навчання, сертифікації та варіанти релокації.",
        documents: "CV, сертифікати, дозволи, строки дії документів і попередження.",
        career_strategy: "Поточна мета, рекомендовані кроки, прогрес і наступна дія.",
        agent_settings: "Мова, тон спілкування, країни пошуку, тип роботи і автономність агента."
      };
      return descriptions[key] || "";
    }

    loadDashboard();
  </script>
</body>
</html>
"""
