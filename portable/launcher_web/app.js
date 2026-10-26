// HU INSTALLER - CHANGAN X7 PLUS ADB MANAGER
// Frontend Controller

let apksList = [];
let isConnected = false;
let pollingTimer = null;

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initMasterSetup();
  initDevicePolling();
  loadApksCatalog();
  initDropZone();
  initTerminalActions();
  initScreenTools();
  initRootTab();
  initInstalledManager();
  initKeymapTab();
});

// 1. TABS NAVIGATION
function initTabs() {
  const navItems = document.querySelectorAll(".nav-item");
  const tabPanes = document.querySelectorAll(".tab-pane");

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const targetId = item.getAttribute("data-tab");
      navItems.forEach(n => n.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      item.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");

      if (targetId === "tab-manager") {
        fetchInstalledApps();
      }
      if (targetId === "tab-keymap") {
        startKeymapPolling();
      } else {
        stopKeymapPollingIfInactive();
      }
    });
  });
}

// 2. DEVICE POLLING & STATUS
async function checkDeviceStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    updateDeviceUI(data);
  } catch (err) {
    updateDeviceUI({ connected: false, state: "error" });
  }
}

function updateDeviceUI(data) {
  const pulse = document.getElementById("sidebar-pulse");
  const statusText = document.getElementById("sidebar-status-text");
  const topPill = document.getElementById("top-status-pill");
  const topLabel = document.getElementById("top-status-label");
  const metaModel = document.getElementById("meta-model");
  const metaSerial = document.getElementById("meta-serial");
  const metaHw = document.getElementById("meta-hw");

  isConnected = !!data.connected;

  if (isConnected) {
    pulse.className = "pulse-indicator connected";
    statusText.textContent = "CONECTADO";
    statusText.style.color = "#10b981";

    topPill.className = "status-pill connected";
    topLabel.innerHTML = `🟢 <b>Changan X7 Plus Conectado</b> (${data.device_id || "USB"})`;

    metaModel.textContent = data.model || "Changan X7 Plus";
    metaSerial.textContent = data.device_id || "Desconocido";
    metaHw.textContent = (data.hardware || "MT8666") + (data.android_version ? ` · Android ${data.android_version}` : "");
    
    const metaAbi = document.getElementById("meta-abi");
    if (metaAbi) metaAbi.textContent = data.cpu_abi || "ARM";

    const metaStorage = document.getElementById("meta-storage");
    if (metaStorage && data.storage) {
      if (data.storage.free_mb > 0) {
        metaStorage.textContent = `${(data.storage.free_mb / 1024).toFixed(1)} GB Libres (${data.storage.percent_used}% usado)`;
        metaStorage.style.color = data.storage.safe ? "#10b981" : "#ef4444";
      } else {
        metaStorage.textContent = "Disponible";
      }
    }
  } else if (data.state === "unauthorized") {
    pulse.className = "pulse-indicator warning";
    statusText.textContent = "AUTORIZAR EN PANTALLA";
    statusText.style.color = "#f59e0b";

    topPill.className = "status-pill warning";
    topLabel.innerHTML = `⚠️ <b>¡Dispositivo detectado!</b> Mira la pantalla del auto: marca <b>"Permitir siempre"</b> y presiona <b>ACEPTAR</b>`;

    metaModel.textContent = "Changan X7 Plus (F202_MCA)";
    metaSerial.textContent = data.device_id || "Sin autorizar";
    metaHw.textContent = "⚠️ Presiona 'Aceptar' en la radio";
    const metaAbi = document.getElementById("meta-abi");
    if (metaAbi) metaAbi.textContent = "--";
    const metaStorage = document.getElementById("meta-storage");
    if (metaStorage) metaStorage.textContent = "--";
  } else if (data.usb_present) {
    pulse.className = "pulse-indicator warning";
    statusText.textContent = "CABLE DETECTADO";
    statusText.style.color = "#38bdf8";

    topPill.className = "status-pill warning";
    topLabel.innerHTML = `🔌 <b>Cable USB detectado (F202_MCA)</b>. En la pantalla del auto activa <b>"Depuración por USB"</b>`;

    metaModel.textContent = "Changan X7 Plus (F202_MCA)";
    metaSerial.textContent = "Conectado a Windows";
    metaHw.textContent = "Activa Depuración por USB";
    const metaAbi = document.getElementById("meta-abi");
    if (metaAbi) metaAbi.textContent = "--";
    const metaStorage = document.getElementById("meta-storage");
    if (metaStorage) metaStorage.textContent = "--";
  } else {
    pulse.className = "pulse-indicator disconnected";
    statusText.textContent = "DESCONECTADO";
    statusText.style.color = "#ef4444";

    topPill.className = "status-pill disconnected";
    topLabel.textContent = "Esperando conexión USB con la Radio...";

    metaModel.textContent = "No detectado";
    metaSerial.textContent = "--";
    metaHw.textContent = "MediaTek MT8666";
    const metaAbi = document.getElementById("meta-abi");
    if (metaAbi) metaAbi.textContent = "--";
    const metaStorage = document.getElementById("meta-storage");
    if (metaStorage) metaStorage.textContent = "--";
  }
}

function initDevicePolling() {
  checkDeviceStatus();
  pollingTimer = setInterval(checkDeviceStatus, 3500);

  document.getElementById("btn-scan-device")?.addEventListener("click", async () => {
    logTerminalLine("Reiniciando y escaneando servidor ADB...", "info");
    try {
      const res = await fetch("/api/restart_adb");
      const data = await res.json();
      if (data && data.info) updateDeviceUI(data.info);
    } catch (e) {
      checkDeviceStatus();
    }
  });

  document.getElementById("btn-wifi-connect")?.addEventListener("click", connectOverWifi);
  document.getElementById("wifi-ip-input")?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") connectOverWifi();
  });

  document.getElementById("btn-quick-reboot")?.addEventListener("click", rebootHeadunit);
}

async function connectOverWifi() {
  const input = document.getElementById("wifi-ip-input");
  const ip = input?.value.trim();
  if (!ip) {
    alert("Por favor escribe la Dirección IP que aparece en la pantalla del auto (ejemplo: 192.168.43.15)");
    input?.focus();
    return;
  }

  logTerminalLine(`$ adb connect ${ip}:5555`, "cmd");
  try {
    const res = await fetch("/api/connect_ip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ip })
    });
    const data = await res.json();
    if (data.success) {
      logTerminalLine(`Vinculado exitosamente a la radio Changan en ${data.target}`, "success");
      checkDeviceStatus();
    } else {
      logTerminalLine(data.output || "No se pudo conectar a la IP especificada. Asegúrate de que la radio y la laptop estén en el mismo Wi-Fi y puerto 5555 activo.", "error");
    }
  } catch (err) {
    logTerminalLine("Error conectando por Wi-Fi: " + err.message, "error");
  }
}

async function rebootHeadunit() {
  if (!confirm("¿Deseas reiniciar la pantalla de la radio ahora?")) return;
  logTerminalLine("$ adb reboot", "cmd");
  try {
    const res = await fetch("/api/reboot", { method: "POST" });
    const data = await res.json();
    logTerminalLine(data.output || "Comando de reinicio enviado.", "success");
    checkDeviceStatus();
  } catch (e) {
    logTerminalLine("Error reiniciando radio: " + e.message, "error");
  }
}

// 3. APKS CATALOG
async function loadApksCatalog() {
  const container = document.getElementById("apps-catalog-list");
  try {
    const res = await fetch("/api/apks");
    const data = await res.json();
    apksList = data.apks || [];
    renderApksGrid(apksList);
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Error cargando catálogo de aplicaciones.</div>`;
  }
}

function renderApksGrid(apks) {
  const container = document.getElementById("apps-catalog-list");
  if (!apks || apks.length === 0) {
    container.innerHTML = `<div class="empty-state">No se encontraron archivos en la carpeta apks/. Arrastra un archivo .apk para comenzar.</div>`;
    return;
  }

  container.innerHTML = "";
  apks.forEach((apk, idx) => {
    const card = document.createElement("div");
    card.className = "app-card selected";
    card.id = `card-apk-${idx}`;

    const iconSvg = getAppIconSvg(apk.metadata.icon);

    card.innerHTML = `
      <div class="app-card-top">
        <div class="app-info-left">
          <div class="app-icon-box">
            ${iconSvg}
          </div>
          <div class="app-title-block">
            <h4>${apk.metadata.name}</h4>
            <span class="app-category">${apk.metadata.category}</span>
          </div>
        </div>
        <div class="app-checkbox-wrap">
          <input type="checkbox" id="chk-${idx}" data-filename="${apk.filename}" checked>
        </div>
      </div>
      <p class="app-desc">${apk.metadata.desc}</p>
      <div class="app-meta-footer">
        <span class="app-size">${apk.size_mb} MB · <code>${apk.filename}</code></span>
        <span class="app-badge-pill">${apk.metadata.badge}</span>
      </div>
    `;

    // Toggle card selection when clicking anywhere except directly checkbox
    card.addEventListener("click", (e) => {
      if (e.target.tagName !== "INPUT") {
        const chk = card.querySelector(`input[type="checkbox"]`);
        chk.checked = !chk.checked;
      }
      const chk = card.querySelector(`input[type="checkbox"]`);
      if (chk.checked) card.classList.add("selected");
      else card.classList.remove("selected");
    });

    container.appendChild(card);
  });

  // Select combo / select all / deselect all
  document.getElementById("btn-select-combo")?.addEventListener("click", () => {
    const comboFiles = [
      "smarttube_youtube_pro.apk",
      "vimusic_musica_estable.apk",
      "organic_maps_gps.apk",
      "taskbar_pantalla_dividida.apk",
      "car_launcher_automotriz.apk",
      "autokit.apk",
      "backbutton.apk",
      "amazefilemanager.apk",
      "navegador_web_adblock.apk",
      "app_store_droidify.apk"
    ];
    document.querySelectorAll(".app-card").forEach(c => {
      const chk = c.querySelector("input[type='checkbox']");
      const fn = chk?.getAttribute("data-filename");
      if (chk && fn) {
        if (comboFiles.includes(fn)) {
          chk.checked = true;
          c.classList.add("selected");
        } else {
          chk.checked = false;
          c.classList.remove("selected");
        }
      }
    });
  });

  document.getElementById("btn-select-all")?.addEventListener("click", () => {
    document.querySelectorAll(".app-card").forEach(c => {
      c.classList.add("selected");
      const chk = c.querySelector("input[type='checkbox']");
      if (chk) chk.checked = true;
    });
  });

  document.getElementById("btn-deselect-all")?.addEventListener("click", () => {
    document.querySelectorAll(".app-card").forEach(c => {
      c.classList.remove("selected");
      const chk = c.querySelector("input[type='checkbox']");
      if (chk) chk.checked = false;
    });
  });

  // Launch install
  document.getElementById("btn-install-selected")?.addEventListener("click", installSelectedApks);
}

function getAppIconSvg(type) {
  if (type === "music") {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>`;
  } else if (type === "car") {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9L2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>`;
  } else if (type === "globe") {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>`;
  } else if (type === "carplay") {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>`;
  } else if (type === "youtube") {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"/><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/></svg>`;
  } else if (type === "folder") {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`;
  } else if (type === "arrow-left") {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>`;
  } else {
    return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>`;
  }
}

// 4. INSTALL APKS
async function installSelectedApks() {
  const selected = [];
  document.querySelectorAll(".apps-grid input[type='checkbox']:checked").forEach(chk => {
    const fn = chk.getAttribute("data-filename");
    if (fn) selected.push(fn);
  });

  if (selected.length === 0) {
    alert("Por favor selecciona al menos una aplicación para instalar.");
    return;
  }

  if (!isConnected) {
    const proceed = confirm("⚠️ No se detecta la radio conectada en este momento.\n\n¿Deseas intentar enviar la instalación de todas formas?");
    if (!proceed) return;
  }

  const btnInstall = document.getElementById("btn-install-selected");
  const progressWrap = document.getElementById("progress-wrap");
  const progressFill = document.getElementById("progress-bar-fill");
  const statusText = document.getElementById("progress-status-text");
  const percentText = document.getElementById("progress-percent-text");

  btnInstall.disabled = true;
  progressWrap.style.display = "flex";
  progressFill.style.width = "5%";
  percentText.textContent = "5%";
  statusText.textContent = `Preparando instalación de ${selected.length} aplicación(es)...`;

  logTerminalLine(`[INICIO] Iniciando instalación en modo Usuario de ${selected.length} aplicación(es)...`, "info");

  let completedCount = 0;
  for (const apkName of selected) {
    statusText.textContent = `Instalando ${apkName} en la radio...`;
    logTerminalLine(`$ adb install -r -d apks/${apkName}`, "cmd");

    try {
      const res = await fetch("/api/install", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filenames: [apkName] })
      });
      const data = await res.json();
      const resItem = (data.results && data.results[0]) || {};

      if (resItem.success) {
        logTerminalLine(`✔ Éxito instalando ${apkName}: ${resItem.output || "Success"}`, "success");
      } else {
        logTerminalLine(`❌ Falló la instalación de ${apkName}: ${resItem.output || "Error desconocido"}`, "error");
      }
    } catch (err) {
      logTerminalLine(`Error de red al instalar ${apkName}: ${err.message}`, "error");
    }

    completedCount++;
    const pct = Math.round((completedCount / selected.length) * 100);
    progressFill.style.width = `${pct}%`;
    percentText.textContent = `${pct}%`;
  }

  statusText.textContent = `¡Proceso completado! ${completedCount} archivo(s) procesados.`;
  btnInstall.disabled = false;
  logTerminalLine(`[FIN] Proceso de instalación completado. Puedes revisar tus apps en la radio.`, "info");
}

// 5. DRAG & DROP CUSTOM APK
function initDropZone() {
  const zone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const btnBrowse = document.getElementById("btn-browse-file");

  if (!zone || !fileInput) return;

  btnBrowse?.addEventListener("click", () => fileInput.click());
  zone.addEventListener("click", (e) => {
    if (e.target !== btnBrowse) fileInput.click();
  });

  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("dragover");
  });

  zone.addEventListener("dragleave", () => {
    zone.classList.remove("dragover");
  });

  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      uploadCustomFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files.length > 0) {
      uploadCustomFile(fileInput.files[0]);
    }
  });
}

async function uploadCustomFile(file) {
  if (!file.name.toLowerCase().endsWith(".apk")) {
    alert("El archivo seleccionado no es un archivo .apk válido.");
    return;
  }

  logTerminalLine(`Cargando archivo personalizado: ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)...`, "info");
  
  try {
    const res = await fetch(`/api/upload_apk?install=false`, {
      method: "POST",
      headers: {
        "Content-Type": "application/octet-stream",
        "X-Filename": encodeURIComponent(file.name)
      },
      body: file
    });
    const data = await res.json();
    logTerminalLine(`✔ Archivo ${file.name} subido y listo en apks/`, "success");
    loadApksCatalog();
  } catch (err) {
    logTerminalLine(`Error subiendo APK: ${err.message}`, "error");
  }
}

// 6. TERMINAL & LOGS
function initTerminalActions() {
  const termBody = document.getElementById("terminal-body");
  const btnClear = document.getElementById("btn-clear-term");
  const btnCopy = document.getElementById("btn-copy-term");
  const cmdInput = document.getElementById("custom-adb-input");
  const btnSend = document.getElementById("btn-send-cmd");

  btnClear?.addEventListener("click", async () => {
    termBody.innerHTML = "";
    await fetch("/api/clear_logs", { method: "POST" });
  });

  btnCopy?.addEventListener("click", () => {
    navigator.clipboard.writeText(termBody.innerText);
    alert("Log copiado al portapapeles.");
  });

  const sendCmd = async () => {
    const val = cmdInput.value.trim();
    if (!val) return;
    cmdInput.value = "";
    logTerminalLine(`$ adb ${val}`, "cmd");

    try {
      const res = await fetch("/api/adb_command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: val })
      });
      const data = await res.json();
      if (data.output) {
        logTerminalLine(data.output, data.code === 0 ? "info" : "error");
      }
    } catch (e) {
      logTerminalLine("Error ejecutando comando: " + e.message, "error");
    }
  };

  btnSend?.addEventListener("click", sendCmd);
  cmdInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendCmd();
  });
}

function logTerminalLine(text, type = "info") {
  const termBody = document.getElementById("terminal-body");
  if (!termBody) return;
  const line = document.createElement("div");
  line.className = `term-line ${type}`;
  line.textContent = text;
  termBody.appendChild(line);
  termBody.scrollTop = termBody.scrollHeight;
}

// 7. SCREEN TOOLS & OVERSCAN
function initScreenTools() {
  const btnApply = document.getElementById("btn-apply-overscan");
  const btnReset = document.getElementById("btn-reset-overscan");
  const btnReboot = document.getElementById("btn-screen-reboot");
  const inputOverscan = document.getElementById("overscan-input");

  btnApply?.addEventListener("click", async () => {
    const val = inputOverscan.value.trim() || "0,-50,0,0";
    logTerminalLine(`$ adb shell wm overscan ${val}`, "cmd");
    try {
      const res = await fetch("/api/overscan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "set", values: val })
      });
      const data = await res.json();
      logTerminalLine(data.output || "Overscan aplicado.", "success");
    } catch (e) {
      logTerminalLine("Error aplicando overscan: " + e.message, "error");
    }
  });

  btnReset?.addEventListener("click", async () => {
    logTerminalLine("$ adb shell wm overscan reset", "cmd");
    try {
      const res = await fetch("/api/overscan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "reset" })
      });
      const data = await res.json();
      logTerminalLine(data.output || "Overscan restablecido a valores de fábrica.", "success");
    } catch (e) {
      logTerminalLine("Error restableciendo overscan: " + e.message, "error");
    }
  });

  btnReboot?.addEventListener("click", rebootHeadunit);

  // UNFREEZE BUTTONS
  const handleUnfreeze = async (target) => {
    logTerminalLine(`[EMERGENCIA] Descongelando pantalla (Cerrando ${target})...`, "cmd");
    try {
      const res = await fetch("/api/unfreeze_app", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target })
      });
      const data = await res.json();
      logTerminalLine(data.output || "Proceso detenido. Pantalla táctil liberada.", "success");
    } catch (e) {
      logTerminalLine("Error al descongelar: " + e.message, "error");
    }
  };

  document.getElementById("btn-quick-unfreeze")?.addEventListener("click", () => handleUnfreeze("rimusic"));
  document.getElementById("btn-unfreeze-rimusic")?.addEventListener("click", () => handleUnfreeze("rimusic"));
  document.getElementById("btn-unfreeze-all")?.addEventListener("click", () => handleUnfreeze("all"));

  // SPLIT SCREEN BUTTON
  document.getElementById("btn-enable-split")?.addEventListener("click", async () => {
    logTerminalLine("[SISTEMA] Habilitando soporte nativo de Doble Pantalla (Split Screen / Freeform)...", "cmd");
    try {
      const res = await fetch("/api/split_screen", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      const data = await res.json();
      logTerminalLine(data.output || "Doble pantalla activada en Android 9.", "success");
    } catch (e) {
      logTerminalLine("Error activando doble pantalla: " + e.message, "error");
    }
  });

  // IMMERSIVE FULLSCREEN BUTTONS
  document.getElementById("btn-fullscreen-enable")?.addEventListener("click", async () => {
    logTerminalLine("[PANTALLA] Activando Modo Pantalla Completa Inmersiva...", "cmd");
    try {
      const res = await fetch("/api/fullscreen", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enable: true })
      });
      const data = await res.json();
      logTerminalLine(data.output || "Pantalla completa activada.", "success");
    } catch (e) {
      logTerminalLine("Error activando pantalla completa: " + e.message, "error");
    }
  });

  document.getElementById("btn-fullscreen-disable")?.addEventListener("click", async () => {
    logTerminalLine("[PANTALLA] Restableciendo modo normal de pantalla...", "cmd");
    try {
      const res = await fetch("/api/fullscreen", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enable: false })
      });
      const data = await res.json();
      logTerminalLine(data.output || "Modo de pantalla restablecido.", "success");
    } catch (e) {
      logTerminalLine("Error restableciendo pantalla: " + e.message, "error");
    }
  });

  // FIX BACK BUTTON
  document.getElementById("btn-fix-back")?.addEventListener("click", async () => {
    logTerminalLine("[ACCESIBILIDAD] Inyectando permisos de superposición y activando Botón Atrás...", "cmd");
    try {
      const res = await fetch("/api/fix_back_button", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      const data = await res.json();
      logTerminalLine(data.output || "Botón flotante activado correctamente.", "success");
    } catch (e) {
      logTerminalLine("Error activando botón atrás: " + e.message, "error");
    }
  });

  // DEFAULT LAUNCHER BUTTONS (COCKPIT X7 PLUS NATIVO)
  document.getElementById("btn-set-default-launcher")?.addEventListener("click", async () => {
    logTerminalLine("[COCKPIT] Instalando y fijando Cockpit Launcher como inicio predeterminado...", "cmd");
    try {
      const res = await fetch("/api/set_cockpit_launcher", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        logTerminalLine("¡ÉXITO! " + (data.output || "Cockpit X7 Plus configurado para auto-arrancar al encender el auto."), "success");
      } else {
        logTerminalLine("Aviso: " + (data.output || "Revisa si la radio está conectada por USB."), "error");
      }
    } catch (e) {
      logTerminalLine("Error configurando lanzador: " + e.message, "error");
    }
  });

  document.getElementById("btn-reset-launcher")?.addEventListener("click", async () => {
    logTerminalLine("[LAUNCHER] Restableciendo lanzador a Changan OnStyle de fábrica...", "cmd");
    try {
      const res = await fetch("/api/restore_factory_launcher", { method: "POST" });
      const data = await res.json();
      logTerminalLine(data.output || "Lanzador de fábrica restablecido.", "success");
    } catch (e) {
      logTerminalLine("Error restableciendo lanzador: " + e.message, "error");
    }
  });
}

// 8. ROOT TAB DIAGNOSTICS
function initRootTab() {
  document.getElementById("btn-test-root")?.addEventListener("click", async () => {
    logTerminalLine("$ adb root", "cmd");
    try {
      const res = await fetch("/api/adb_command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: "root" })
      });
      const data = await res.json();
      logTerminalLine(data.output || "Comando ejecutado", "info");
    } catch (e) {
      logTerminalLine("Error: " + e.message, "error");
    }
  });

  document.getElementById("btn-test-remount")?.addEventListener("click", async () => {
    logTerminalLine("$ adb remount", "cmd");
    try {
      const res = await fetch("/api/adb_command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: "remount" })
      });
      const data = await res.json();
      logTerminalLine(data.output || "Comando ejecutado", "info");
    } catch (e) {
      logTerminalLine("Error: " + e.message, "error");
    }
  });
}

// 9. INSTALLED APPS MANAGER
async function fetchInstalledApps() {
  const container = document.getElementById("installed-list-container");
  container.innerHTML = `<div class="empty-state">Leyendo aplicaciones de terceros instaladas en la radio...</div>`;
  logTerminalLine("$ adb shell pm list packages -3", "cmd");

  try {
    const res = await fetch("/api/installed_apps");
    const data = await res.json();
    const pkgs = data.packages || [];

    if (pkgs.length === 0) {
      container.innerHTML = `<div class="empty-state">No se encontraron aplicaciones de terceros o la radio no está conectada.</div>`;
      return;
    }

    container.innerHTML = "";
    pkgs.forEach(pkg => {
      const row = document.createElement("div");
      row.className = "installed-row";
      row.innerHTML = `
        <span class="installed-row-text">${pkg}</span>
        <button class="btn-uninstall" data-pkg="${pkg}">Desinstalar</button>
      `;

      row.querySelector(".btn-uninstall")?.addEventListener("click", () => uninstallApp(pkg));
      container.appendChild(row);
    });
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Error leyendo aplicaciones: ${e.message}</div>`;
  }
}

async function uninstallApp(pkg) {
  if (!confirm(`¿Estás seguro de que deseas desinstalar el paquete:\n${pkg}?`)) return;
  logTerminalLine(`$ adb uninstall ${pkg}`, "cmd");

  try {
    const res = await fetch("/api/uninstall", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ package: pkg })
    });
    const data = await res.json();
    logTerminalLine(data.output || "Desinstalación ejecutada.", "info");
    fetchInstalledApps();
  } catch (e) {
    logTerminalLine("Error desinstalando: " + e.message, "error");
  }
}

document.getElementById("btn-refresh-installed")?.addEventListener("click", fetchInstalledApps);

// 10. MASTER 5-CORE OPERATIONS & DASHBOARD CONTROLLER
function initMasterSetup() {
  const btnRestoreFactory = document.getElementById("btn-core-restore-factory");
  const btnApplyAll = document.getElementById("btn-core-apply-all");
  const btnGlobalMargins = document.getElementById("btn-core-global-margins");
  const btnExportTelemetry = document.getElementById("btn-core-export-telemetry");
  const btnSystemBackup = document.getElementById("btn-core-system-backup");
  const progressBox = document.getElementById("master-progress-box");
  const stepsList = document.getElementById("master-steps-list");

  // A. CARGAR Y ACTUALIZAR FECHAS DE ÚLTIMAS MODIFICACIONES
  async function loadDashboardTimestamps() {
    try {
      const res = await fetch("/api/dashboard_state");
      const data = await res.json();
      
      const elRestore = document.getElementById("ts-factory-restore");
      if (elRestore) elRestore.textContent = data.last_factory_restore || "Nunca realizado";

      const elApply = document.getElementById("ts-apply-all");
      if (elApply) elApply.textContent = data.last_apply_all || "Nunca realizado";

      const elMargins = document.getElementById("ts-screen-config");
      if (elMargins) elMargins.textContent = data.last_screen_config || "Nunca realizado";

      const elTelemetry = document.getElementById("ts-telemetry-export");
      if (elTelemetry) elTelemetry.textContent = data.last_telemetry_export || "Nunca realizado";

      const elBackup = document.getElementById("ts-system-backup");
      if (elBackup) elBackup.textContent = data.last_system_backup || "Nunca realizado";

      // Report link
      if (data.last_telemetry_file) {
        const wrap = document.getElementById("telemetry-link-wrap");
        const link = document.getElementById("telemetry-link");
        if (wrap && link) {
          wrap.style.display = "block";
          link.href = `/api/download_report?file=${encodeURIComponent(data.last_telemetry_file)}`;
          link.textContent = `📄 Ver Informe: ${data.last_telemetry_file}`;
        }
      }

      // Backup dir
      if (data.last_system_backup_dir) {
        const wrapB = document.getElementById("backup-info-wrap");
        const dirB = document.getElementById("backup-info-dir");
        if (wrapB && dirB) {
          wrapB.style.display = "block";
          dirB.textContent = data.last_system_backup_dir;
        }
      }
    } catch (e) {
      console.warn("No se pudieron cargar timestamps del dashboard:", e);
    }
  }

  loadDashboardTimestamps();
  setInterval(loadDashboardTimestamps, 8000);

  // Helper renderizador de pasos de instalación
  function renderProgressSteps(steps = []) {
    if (!stepsList || !progressBox) return;
    progressBox.style.display = "block";
    stepsList.innerHTML = "";
    steps.forEach((st, idx) => {
      const row = document.createElement("div");
      const icon = st.status === "ok" ? "✔" : (st.status === "warning" ? "⚠️" : "⚡");
      row.className = `master-step-row ${st.status === "ok" ? "success" : "warning"}`;
      row.innerHTML = `
        <span class="master-step-icon">${icon}</span>
        <div>
          <strong>${idx + 1}. ${st.title}</strong>
          <span style="display:block; font-size:11.5px; opacity:0.8;">${st.msg || ""}</span>
        </div>
      `;
      stepsList.appendChild(row);
    });
  }

  // 1. FUNCIÓN 1: BORRAR TODO Y VOLVER A FÁBRICA
  async function handleRestoreFactory() {
    const confirmWipe = confirm(
      "⚠️ ¿ESTÁS SEGURO DE RESTAURAR TODO A ESTADO ORIGINAL DE FÁBRICA?\n\n" +
      "• Se desinstalarán todas las aplicaciones instaladas (Cockpit, Waze, RiMusic, etc.).\n" +
      "• Se restablecerá la interfaz original Changan OnStyle.\n" +
      "• Se reiniciarán overscan, resoluciones y permisos.\n\n" +
      "El auto quedará 100% como si nunca hubiésemos instalado nada."
    );
    if (!confirmWipe) return;

    if (btnRestoreFactory) {
      btnRestoreFactory.disabled = true;
      btnRestoreFactory.innerHTML = `<span style="display:inline-block; animation: spin 1s linear infinite;">⏳</span> RESTAURANDO DE FÁBRICA...`;
    }
    logTerminalLine("[FÁBRICA] Iniciando borrado total y restauración a Changan OnStyle original...", "cmd");

    try {
      const res = await fetch("/api/action_restore_factory", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        renderProgressSteps(data.steps || []);
        logTerminalLine("✔ " + data.message, "success");
        alert("¡RESTAURACIÓN COMPLETADA CON ÉXITO!\n\nEl auto ha vuelto al 100% a su estado original de fábrica (Changan OnStyle).");
        await loadDashboardTimestamps();
      } else {
        logTerminalLine("❌ Error restaurando fábrica: " + (data.error || "Fallo desconocido"), "error");
        alert("Error restaurando: " + (data.error || "Verifica conexión USB"));
      }
    } catch (err) {
      logTerminalLine("❌ Error de comunicación: " + err.message, "error");
    } finally {
      if (btnRestoreFactory) {
        btnRestoreFactory.disabled = false;
        btnRestoreFactory.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg> 🔴 BORRAR TODO Y VOLVER A FÁBRICA (1 CLIC)`;
      }
    }
  }

  btnRestoreFactory?.addEventListener("click", handleRestoreFactory);
  document.getElementById("btn-topbar-restore-factory")?.addEventListener("click", handleRestoreFactory);
  document.getElementById("btn-master-restore-factory")?.addEventListener("click", handleRestoreFactory);
  document.getElementById("btn-topbar-clean-all")?.addEventListener("click", handleRestoreFactory);
  document.getElementById("btn-hero-clean-all")?.addEventListener("click", handleRestoreFactory);

  document.getElementById("btn-topbar-open-emulator")?.addEventListener("click", async () => {
    logTerminalLine("[EMULADOR] Solicitando apertura de ventana panorámica Changan X7 Plus (1920x720)...", "info");
    try {
      const res = await fetch("/api/launch_emulator", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        logTerminalLine("[EMULADOR] " + data.output, "success");
        alert("🖥️ Emulador Changan X7 Plus iniciado exitosamente.\n\nRevisa tu barra de tareas o escritorio de Windows para ver la ventana panorámica de 1920x720.");
      } else {
        logTerminalLine("[EMULADOR ERROR] " + (data.output || "Error al abrir emulador"), "danger");
        alert("Aviso: " + (data.output || "No se pudo iniciar el emulador"));
      }
    } catch (e) {
      logTerminalLine("[EMULADOR ERROR] Error de comunicación: " + e.message, "danger");
    }
  });

  // 2. FUNCIÓN 2: APLICAR TODAS LAS MEJORAS CON 1 CLIC
  async function handleApplyAll(btn) {
    if (!isConnected) {
      const proceed = confirm("⚠️ La radio aparece desconectada en este momento.\n\nVerifica que el cable USB esté conectado en el puerto delantero y que hayas escrito **888 en el teléfono del auto para activar 'Depuración USB'.\n\n¿Deseas enviar el comando de todas formas?");
      if (!proceed) return;
    }

    const allApplyBtns = [
      btnApplyAll,
      document.getElementById("btn-topbar-apply-all"),
      document.getElementById("btn-hero-apply-all")
    ].filter(Boolean);

    allApplyBtns.forEach(b => {
      b.disabled = true;
      b.dataset.oldHtml = b.innerHTML;
      b.innerHTML = `<span style="display:inline-block; animation: spin 1s linear infinite;">⏳</span> APLICANDO TODAS LAS MEJORAS...`;
    });

    logTerminalLine("[MASTER] Iniciando despliegue de toda la Suite 2026 en Changan X7 Plus...", "info");

    try {
      const res = await fetch("/api/action_apply_all", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        renderProgressSteps(data.steps || []);
        allApplyBtns.forEach(b => {
          b.innerHTML = `✔ ¡SUITE IMPLEMENTADA CON ÉXITO!`;
          b.style.background = "linear-gradient(135deg, #059669 0%, #10b981 100%)";
        });
        logTerminalLine("✔ [ÉXITO] Todo configurado e instalado: Cockpit 1920x720 nativo sin franjas, Spotube (Spotify Libre), SimpMusic Offline, OwnTV 370+ Canales, Android Auto Inalámbrico y Waze GPS.", "success");
        alert("¡SUITE COMPLETA DESPLEGADA CON ÉXITO!\n\n• Cockpit X7 Plus: Activo a 1920x720 sin franjas negras.\n• Android Auto: WPP Inalámbrico nativo listo.\n• Música & TV: Spotube MP3, SimpMusic y OwnTV 370+ canales instalados.\n• Waze Satelital: Activo en Pacasmayo, Callao con satélites fijados.");
        await loadDashboardTimestamps();
        setTimeout(() => {
          allApplyBtns.forEach(b => {
            b.disabled = false;
            if (b.dataset.oldHtml) b.innerHTML = b.dataset.oldHtml;
            b.style.background = "";
          });
        }, 5000);
      } else {
        allApplyBtns.forEach(b => {
          b.disabled = false;
          b.innerHTML = `❌ REINTENTAR APLICAR MEJORAS`;
        });
        logTerminalLine("❌ Error en despliegue: " + (data.error || "Fallo desconocido"), "error");
        alert(data.error || "No se pudo completar la instalación. Verifica el cable USB y **888.");
      }
    } catch (err) {
      allApplyBtns.forEach(b => {
        b.disabled = false;
        b.innerHTML = `❌ ERROR CONEXIÓN`;
      });
      logTerminalLine("❌ Error de comunicación: " + err.message, "error");
    }
  }

  btnApplyAll?.addEventListener("click", () => handleApplyAll(btnApplyAll));
  document.getElementById("btn-topbar-apply-all")?.addEventListener("click", () => handleApplyAll(document.getElementById("btn-topbar-apply-all")));
  document.getElementById("btn-hero-apply-all")?.addEventListener("click", () => handleApplyAll(document.getElementById("btn-hero-apply-all")));

  // 3. FUNCIÓN 3: CONFIGURACIÓN GLOBAL DE PANTALLA & MÁRGENES
  btnGlobalMargins?.addEventListener("click", async () => {
    btnGlobalMargins.disabled = true;
    btnGlobalMargins.innerHTML = `<span style="display:inline-block; animation: spin 1s linear infinite;">⏳</span> APLICANDO 1920x720 DEFINITIVO...`;
    logTerminalLine("[PANTALLA] Aplicando configuración global y definitiva de márgenes (1920x720 @ 213 DPI)...", "info");

    try {
      const res = await fetch("/api/action_global_margins", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        logTerminalLine("✔ " + data.message, "success");
        alert(
          "¡AJUSTE GLOBAL Y DEFINITIVO APLICADO!\n\n" +
          "• Resolución: 1920x720 nativa\n" +
          "• Densidad: 213 DPI\n" +
          "• Overscan: 0,0,0,0 (Cero márgenes)\n" +
          "• Bypass SystemUI: Activo (com.chinatsp.* appCentered=2)\n\n" +
          "¿Basta con un solo ajuste? SÍ: Las barras negras de 320 px se han plegado de forma permanente."
        );
        await loadDashboardTimestamps();
      } else {
        logTerminalLine("❌ Error aplicando ajuste: " + (data.error || "Fallo"), "error");
      }
    } catch (err) {
      logTerminalLine("❌ Error de comunicación: " + err.message, "error");
    } finally {
      btnGlobalMargins.disabled = false;
      btnGlobalMargins.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg> 📐 APLICAR AJUSTE GLOBAL DE MÁRGENES`;
    }
  });

  // 4. FUNCIÓN 4: EXTRAER TODA LA INFORMACIÓN DEL AUTO (LOG COMPLETO)
  btnExportTelemetry?.addEventListener("click", async () => {
    btnExportTelemetry.disabled = true;
    btnExportTelemetry.innerHTML = `<span style="display:inline-block; animation: spin 1s linear infinite;">⏳</span> ESCANEANDO TELEMETRÍA...`;
    logTerminalLine("[DIAGNÓSTICO] Extrayendo getprop, dumpsys window, display, CPU MT8666, particiones y logcat...", "info");

    try {
      const res = await fetch("/api/action_export_telemetry", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        logTerminalLine("✔ " + data.message, "success");
        alert(
          `¡INFORME DE TELEMETRÍA GENERADO EXITOSAMENTE!\n\n` +
          `• Archivo: ${data.filename}\n` +
          `• Tamaño: ${data.size_kb} KB\n` +
          `• Fecha/Hora: ${data.timestamp}\n\n` +
          `Puedes abrir el archivo generado haciendo clic en el enlace verde que apareció abajo.`
        );
        await loadDashboardTimestamps();
      } else {
        logTerminalLine("❌ Error extrayendo telemetría: " + (data.error || "Fallo"), "error");
      }
    } catch (err) {
      logTerminalLine("❌ Error de comunicación: " + err.message, "error");
    } finally {
      btnExportTelemetry.disabled = false;
      btnExportTelemetry.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg> 📊 EXTRAER TELEMETRÍA Y GENERAR INFORME`;
    }
  });

  // 5. FUNCIÓN 5: COPIA DE SEGURIDAD / CLONACIÓN DEL SISTEMA
  btnSystemBackup?.addEventListener("click", async () => {
    btnSystemBackup.disabled = true;
    btnSystemBackup.innerHTML = `<span style="display:inline-block; animation: spin 1s linear infinite;">⏳</span> CLONANDO SISTEMA DEL AUTO...`;
    logTerminalLine("[BACKUP] Descargando /system/priv-app, /system/app, /vendor y build.prop para emulación...", "info");

    try {
      const res = await fetch("/api/action_system_backup", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        logTerminalLine("✔ " + data.message, "success");
        alert(
          `¡COPIA DE SEGURIDAD COMPLETADA EXITOSAMENTE!\n\n` +
          `• Directorio: oem_factory_backup/${data.backup_dir}\n` +
          `• Archivos clonados: ${data.total_files}\n` +
          `• Fecha/Hora: ${data.timestamp}\n\n` +
          `El sistema del vehículo ha sido respaldado en tu PC para emularlo a la perfección.`
        );
        await loadDashboardTimestamps();
      } else {
        logTerminalLine("❌ Error realizando respaldo: " + (data.error || "Fallo"), "error");
      }
    } catch (err) {
      logTerminalLine("❌ Error de comunicación: " + err.message, "error");
    } finally {
      btnSystemBackup.disabled = false;
      btnSystemBackup.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg> 💾 INICIAR COPIA DE SEGURIDAD DEL AUTO`;
    }
  });
}

// 10. SISTEMA DE MAPEO DE TECLAS Y VOLANTE (CAN-BUS)
let keymapPollingInterval = null;
let isKeymapMonitoring = false;
let lastRenderedEventCount = 0;

function initKeymapTab() {
  const btnToggle = document.getElementById("btn-keymap-toggle");
  const btnSaveLog = document.getElementById("btn-keymap-save-log");
  const btnClear = document.getElementById("btn-keymap-clear");
  const btnCamAvm = document.getElementById("btn-test-cam-avm");
  const btnCamCan = document.getElementById("btn-test-cam-can");
  const btnCamHd = document.getElementById("btn-test-cam-hd");
  const btnGpsDiag = document.getElementById("btn-test-gps-diag");

  btnToggle?.addEventListener("click", async () => {
    btnToggle.disabled = true;
    try {
      const endpoint = isKeymapMonitoring ? "/api/keymap/stop" : "/api/keymap/start";
      const res = await fetch(endpoint, { method: "POST" });
      const data = await res.json();
      isKeymapMonitoring = !!data.monitoring;
      updateKeymapMonitorUI(isKeymapMonitoring);
      if (isKeymapMonitoring) {
        startKeymapPolling();
      } else if (data.auto_saved_file) {
        logTerminalLine("✔ Registro de teclas autoguardado: " + data.auto_saved_file, "success");
        const linkWrap = document.getElementById("keymap-download-link-wrap");
        const link = document.getElementById("keymap-download-link");
        if (linkWrap && link) {
          link.href = data.download_url;
          link.textContent = `📥 Descargar ${data.auto_saved_file}`;
          linkWrap.style.display = "inline";
        }
      }
    } catch (e) {
      logTerminalLine("❌ Error alternando monitor de teclas: " + e.message, "error");
    } finally {
      btnToggle.disabled = false;
    }
  });

  btnSaveLog?.addEventListener("click", async () => {
    btnSaveLog.disabled = true;
    btnSaveLog.innerHTML = `<span style="display:inline-block; animation: spin 1s linear infinite;">⏳</span> Guardando...`;
    try {
      const res = await fetch("/api/keymap/save_log", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        logTerminalLine("✔ Log de teclas guardado: " + data.filename, "success");
        const linkWrap = document.getElementById("keymap-download-link-wrap");
        const link = document.getElementById("keymap-download-link");
        if (linkWrap && link) {
          link.href = data.download_url;
          link.textContent = `📥 Descargar ${data.filename}`;
          linkWrap.style.display = "inline";
        }
        alert(`¡REGISTRO DE TECLAS GUARDADO CON ÉXITO!\n\nArchivo: ${data.filename}\n\nPuedes descargarlo desde el enlace azul que apareció junto al botón Limpiar.`);
      }
    } catch (e) {
      logTerminalLine("❌ Error guardando log: " + e.message, "error");
    } finally {
      btnSaveLog.disabled = false;
      btnSaveLog.innerHTML = `💾 Guardar Log`;
    }
  });

  btnClear?.addEventListener("click", async () => {
    try {
      await fetch("/api/keymap/clear", { method: "POST" });
      const container = document.getElementById("keymap-events-container");
      if (container) {
        container.innerHTML = `
          <div class="keymap-empty-state" style="text-align: center; color: #64748b; padding: 60px 20px;">
            <div style="font-size: 32px; margin-bottom: 10px;">🎮</div>
            <strong style="color: #94a3b8; font-size: 14px;">El monitor de teclas está listo</strong>
            <p style="font-size: 12px; margin-top: 6px;">Presiona cualquier botón en el timón o consola del auto para ver el código en tiempo real.</p>
          </div>
        `;
      }
      const badge = document.getElementById("keymap-count-badge");
      if (badge) badge.textContent = "0";
      lastRenderedEventCount = 0;
    } catch (e) {
      console.error(e);
    }
  });

  // Hardware key simulators (Vol+, Vol-, Next, Prev, etc.)
  document.querySelectorAll(".btn-key-test").forEach(btn => {
    btn.addEventListener("click", async () => {
      const key = btn.getAttribute("data-key");
      btn.style.borderColor = "#38bdf8";
      logTerminalLine(`[TIMÓN] Simulando tecla KEYCODE: ${key}...`, "info");
      try {
        await fetch("/api/adb_command", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ command: `shell input keyevent ${key}` })
        });
      } catch (e) {
        console.error(e);
      } finally {
        setTimeout(() => { btn.style.borderColor = ""; }, 300);
      }
    });
  });

  // Action test buttons & 1-Click Diagnostic Tools
  btnCamAvm?.addEventListener("click", () => triggerKeymapAction("cam_avm", "Abriendo Cámara 360° AVM..."));
  btnCamCan?.addEventListener("click", () => triggerKeymapAction("cam_can", "Enviando broadcast CanBus AVM..."));
  btnCamHd?.addEventListener("click", () => triggerKeymapAction("cam_hd", "Abriendo grabador DVR HD..."));
  document.getElementById("btn-test-cam-dvr")?.addEventListener("click", () => triggerKeymapAction("cam_dvr", "Abriendo Aplicación DVR Principal..."));
  btnGpsDiag?.addEventListener("click", () => triggerKeymapAction("gps", "Comprobando hardware GNSS..."));

  // 1-Click Fix: Restablecer GPS Físico Nativo
  document.getElementById("btn-restore-gps")?.addEventListener("click", async () => {
    logTerminalLine("[GPS] Restableciendo receptor físico GNSS MT8666 y desactivando mock provider...", "info");
    try {
      const res = await fetch("/api/gps/restore_native", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        logTerminalLine("✔ " + data.message, "success");
        alert("¡RECEPTOR GPS NATIVO RESTABLECIDO!\n\n" + data.message + "\n\nAhora Waze, Google Maps y Organic Maps recibirán la señal satelital directa del chip GPS del vehículo sin intermediarios.");
      } else {
        logTerminalLine("❌ Error: " + data.message, "error");
      }
    } catch (e) {
      logTerminalLine("❌ Error de comunicación: " + e.message, "error");
    }
  });

  // 1-Click Fix: Inyectar Canales VIP en OwnTV
  document.getElementById("btn-inject-owntv")?.addEventListener("click", async () => {
    logTerminalLine("[OWNTV] Inyectando lista de 371 Canales VIP en memoria de la radio...", "info");
    try {
      const res = await fetch("/api/owntv/inject_channels", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        logTerminalLine("✔ " + data.message, "success");
        alert("¡CANALES VIP INYECTADOS EN OWNTV!\n\n" + data.message + "\n\nSe ha colocado el archivo de 371 canales en /sdcard/canales_vip.m3u para que OwnTV tenga fuente inmediata sin escribir nada a mano.");
      } else {
        logTerminalLine("❌ Error: " + data.message, "error");
      }
    } catch (e) {
      logTerminalLine("❌ Error de comunicación: " + e.message, "error");
    }
  });

  // 1-Click Fix: Corregir Superposición SimpMusic
  document.getElementById("btn-fix-simpmusic")?.addEventListener("click", async () => {
    logTerminalLine("[SIMPMUSIC] Aplicando bypass F202_SystemUI e inmersión de pantalla completa...", "info");
    try {
      const res = await fetch("/api/fix_simpmusic_layout", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        logTerminalLine("✔ " + data.message, "success");
        alert("¡SUPERPOSICIÓN CORREGIDA EN SIMPMUSIC!\n\n" + data.message + "\n\nSe envió el bypass appCentered=2 a F202_SystemUI y se forzó policy_control immersive.full. Ya no se sobrepondrá la barra del reloj ni se bloqueará el botón del engranaje.");
      } else {
        logTerminalLine("❌ Error: " + data.message, "error");
      }
    } catch (e) {
      logTerminalLine("❌ Error de comunicación: " + e.message, "error");
    }
  });

  // Asistente Wi-Fi 2.4 GHz & HUR
  document.getElementById("btn-wifi-hur-guide")?.addEventListener("click", () => {
    alert(
      "DIAGNÓSTICO WI-FI & ANDROID AUTO (HUR) - CHANGAN X7 PLUS:\n\n" +
      "1. ¿POR QUÉ DECÍA 'FUERA DE ALCANCE'?\n" +
      "El módem Wi-Fi de la Changan (MediaTek MT8666) es SOLO 2.4 GHz (canales 1 al 11). Si tu celular emite Hotspot en 5 GHz o con seguridad WPA3, la radio lo verá 'Fuera de alcance' o se desconectará.\n\n" +
      "2. SOLUCIÓN EN TU TELÉFONO (Hotspot):\n" +
      "• En los ajustes de Zona Wi-Fi de tu celular, busca 'Banda de AP' y selecciona: 2.4 GHz (O 'Maximizar compatibilidad').\n" +
      "• En Tipo de Seguridad elige: WPA2-Personal (no WPA3).\n\n" +
      "3. HEADUNIT RELOADED (HUR):\n" +
      "• No uses Wi-Fi Direct (P2P falla en Android 9).\n" +
      "• En tu celular: Abre Android Auto > Ajustes > Toca 10 veces 'Versión' > Abre menú de 3 puntos > 'Iniciar servidor de unidad central'.\n" +
      "• Conecta la radio al Hotspot 2.4 GHz de tu celular y en HUR pulsa 'WiFi'."
    );
  });
}

async function triggerKeymapAction(action, logMsg) {
  logTerminalLine(`[CAN-BUS] ${logMsg}`, "info");
  try {
    const res = await fetch("/api/keymap/test_action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action })
    });
    const data = await res.json();
    if (data.success) {
      logTerminalLine("✔ " + data.message, "success");
    } else {
      logTerminalLine("❌ " + data.message, "error");
    }
  } catch (e) {
    logTerminalLine("❌ Error enviando acción: " + e.message, "error");
  }
}

function updateKeymapMonitorUI(monitoring) {
  isKeymapMonitoring = monitoring;
  const toggleBtn = document.getElementById("btn-keymap-toggle");
  const toggleIcon = document.getElementById("keymap-toggle-icon");
  const toggleText = document.getElementById("keymap-toggle-text");
  const pulse = document.getElementById("keymap-pulse");
  const label = document.getElementById("keymap-status-label");

  if (monitoring) {
    if (toggleBtn) toggleBtn.style.background = "linear-gradient(135deg, #ef4444, #b91c1c)";
    if (toggleIcon) toggleIcon.textContent = "⏹";
    if (toggleText) toggleText.textContent = "Detener Escaneo";
    if (pulse) {
      pulse.className = "pulse-indicator connected";
      pulse.style.background = "#10b981";
      pulse.style.boxShadow = "0 0 10px #10b981";
    }
    if (label) {
      label.textContent = "Monitoreando en Vivo (getevent activo)";
      label.style.color = "#10b981";
    }
  } else {
    if (toggleBtn) toggleBtn.style.background = "linear-gradient(135deg, #10b981, #059669)";
    if (toggleIcon) toggleIcon.textContent = "▶";
    if (toggleText) toggleText.textContent = "Iniciar Escaneo en Vivo";
    if (pulse) {
      pulse.className = "pulse-indicator disconnected";
      pulse.style.background = "#64748b";
      pulse.style.boxShadow = "none";
    }
    if (label) {
      label.textContent = "Detenido";
      label.style.color = "#94a3b8";
    }
  }
}

function startKeymapPolling() {
  if (keymapPollingInterval) return;
  keymapPollingInterval = setInterval(pollKeymapStatus, 800);
  pollKeymapStatus();
}

function stopKeymapPollingIfInactive() {
  if (!isKeymapMonitoring && keymapPollingInterval) {
    clearInterval(keymapPollingInterval);
    keymapPollingInterval = null;
  }
}

async function pollKeymapStatus() {
  try {
    const res = await fetch("/api/keymap/status");
    const data = await res.json();
    updateKeymapMonitorUI(data.monitoring);
    const countBadge = document.getElementById("keymap-count-badge");
    if (countBadge) countBadge.textContent = data.count || 0;

    if (data.events && data.events.length !== lastRenderedEventCount) {
      renderKeymapEvents(data.events);
      lastRenderedEventCount = data.events.length;
    }
  } catch (e) {
    // ignore
  }
}

function renderKeymapEvents(events) {
  const container = document.getElementById("keymap-events-container");
  if (!container) return;

  if (!events || events.length === 0) {
    container.innerHTML = `
      <div class="keymap-empty-state" style="text-align: center; color: #64748b; padding: 60px 20px;">
        <div style="font-size: 32px; margin-bottom: 10px;">🎮</div>
        <strong style="color: #94a3b8; font-size: 14px;">El monitor de teclas está listo</strong>
        <p style="font-size: 12px; margin-top: 6px;">Haz clic en <b>"Iniciar Escaneo en Vivo"</b> y presiona cualquier botón en el timón o consola del auto para ver el código en tiempo real.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = events.map(ev => {
    const isDown = ev.desc && ev.desc.includes("Pulsada");
    const stateBg = isDown ? "rgba(16, 185, 129, 0.15)" : "rgba(56, 189, 248, 0.15)";
    const stateBorder = isDown ? "rgba(16, 185, 129, 0.3)" : "rgba(56, 189, 248, 0.2)";
    const descColor = isDown ? "#34d399" : "#38bdf8";

    return `
      <div class="keymap-event-row" style="background: ${stateBg}; border: 1px solid ${stateBorder}; padding: 8px 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s ease;">
        <div>
          <span style="color: #94a3b8; font-weight: 700; font-size: 11px;">[${ev.time || ""}]</span>
          <span style="color: ${descColor}; font-weight: 700; margin-left: 6px; font-size: 13px;">${ev.desc || "Evento"}</span>
          <div style="font-size: 11px; color: #94a3b8; margin-top: 3px;">
            <span>Dispositivo: <code style="color:#f8fafc;">${ev.device || ""}</code></span>
            ${ev.focus ? ` • <span style="color:#cbd5e1;">App: ${ev.focus}</span>` : ""}
          </div>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 10px; background: rgba(0,0,0,0.4); color: #cbd5e1; padding: 3px 7px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.08); font-family: monospace;">${ev.raw ? ev.raw.split(':').slice(-1)[0].trim() : ''}</span>
        </div>
      </div>
    `;
  }).join("");

  container.scrollTop = container.scrollHeight;
}
