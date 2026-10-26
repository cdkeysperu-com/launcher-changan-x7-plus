# -*- coding: utf-8 -*-
import os

APP_JS_PATH = os.path.join(os.path.dirname(__file__), "launcher_web", "app.js")

new_master_controller = '''// 10. MASTER 5-CORE OPERATIONS & DASHBOARD CONTROLLER
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
      "⚠️ ¿ESTÁS SEGURO DE RESTAURAR TODO A ESTADO ORIGINAL DE FÁBRICA?\\n\\n" +
      "• Se desinstalarán todas las aplicaciones instaladas (Cockpit, Waze, RiMusic, etc.).\\n" +
      "• Se restablecerá la interfaz original Changan OnStyle.\\n" +
      "• Se reiniciarán overscan, resoluciones y permisos.\\n\\n" +
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
        alert("¡RESTAURACIÓN COMPLETADA CON ÉXITO!\\n\\nEl auto ha vuelto al 100% a su estado original de fábrica (Changan OnStyle).");
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

  // 2. FUNCIÓN 2: APLICAR TODAS LAS MEJORAS CON 1 CLIC
  btnApplyAll?.addEventListener("click", async () => {
    if (!isConnected) {
      const proceed = confirm("⚠️ La radio aparece desconectada en este momento.\\n\\nVerifica que el cable USB esté conectado en el puerto delantero y que hayas escrito **888 en el teléfono del auto para activar 'Depuración USB'.\\n\\n¿Deseas enviar el comando de todas formas?");
      if (!proceed) return;
    }

    btnApplyAll.disabled = true;
    btnApplyAll.innerHTML = `<span style="display:inline-block; animation: spin 1s linear infinite;">⏳</span> APLICANDO TODAS LAS MEJORAS...`;
    logTerminalLine("[MASTER] Iniciando despliegue de toda la Suite 2026 en Changan X7 Plus...", "info");

    try {
      const res = await fetch("/api/action_apply_all", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        renderProgressSteps(data.steps || []);
        btnApplyAll.innerHTML = `✔ ¡TODAS LAS MEJORAS APLICADAS!`;
        btnApplyAll.style.background = "linear-gradient(135deg, #059669 0%, #10b981 100%)";
        logTerminalLine("✔ [ÉXITO] Todo configurado e instalado: Cockpit 1920x720 nativo sin franjas, Waze GPS Callao con satélites, YouTube, RiMusic y CarPlay/AA.", "success");
        alert("¡SUITE COMPLETA DESPLEGADA CON ÉXITO!\\n\\n• Cockpit X7 Plus: Activo a 1920x720 sin franjas negras.\\n• Waze Satelital: Activo en Pacasmayo, Callao con satélites fijados.\\n• Apps complementarias instaladas y listas.");
        await loadDashboardTimestamps();
        setTimeout(() => {
          btnApplyAll.disabled = false;
          btnApplyAll.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> ⚡ APLICAR TODAS LAS MEJORAS (1 CLIC)`;
          btnApplyAll.style.background = "";
        }, 5000);
      } else {
        btnApplyAll.disabled = false;
        btnApplyAll.innerHTML = `❌ REINTENTAR APLICAR MEJORAS`;
        logTerminalLine("❌ Error en despliegue: " + (data.error || "Fallo desconocido"), "error");
        alert(data.error || "No se pudo completar la instalación. Verifica el cable USB y **888.");
      }
    } catch (err) {
      btnApplyAll.disabled = false;
      btnApplyAll.innerHTML = `❌ ERROR CONEXIÓN`;
      logTerminalLine("❌ Error de comunicación: " + err.message, "error");
    }
  });

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
          "¡AJUSTE GLOBAL Y DEFINITIVO APLICADO!\\n\\n" +
          "• Resolución: 1920x720 nativa\\n" +
          "• Densidad: 213 DPI\\n" +
          "• Overscan: 0,0,0,0 (Cero márgenes)\\n" +
          "• Bypass SystemUI: Activo (com.chinatsp.* appCentered=2)\\n\\n" +
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
          `¡INFORME DE TELEMETRÍA GENERADO EXITOSAMENTE!\\n\\n` +
          `• Archivo: ${data.filename}\\n` +
          `• Tamaño: ${data.size_kb} KB\\n` +
          `• Fecha/Hora: ${data.timestamp}\\n\\n` +
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
          `¡COPIA DE SEGURIDAD COMPLETADA EXITOSAMENTE!\\n\\n` +
          `• Directorio: oem_factory_backup/${data.backup_dir}\\n` +
          `• Archivos clonados: ${data.total_files}\\n` +
          `• Fecha/Hora: ${data.timestamp}\\n\\n` +
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
'''

with open(APP_JS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '// 10. MASTER 1-CLICK SETUP CONTROLLER'
start_idx = content.find(start_marker)

if start_idx != -1:
    new_content = content[:start_idx] + new_master_controller
    with open(APP_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS: app.js updated with 5 Core Dashboard operations controller!")
else:
    print(f"FAILED: marker not found")
