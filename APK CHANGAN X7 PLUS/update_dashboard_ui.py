# -*- coding: utf-8 -*-
import os

HTML_PATH = os.path.join(os.path.dirname(__file__), "launcher_web", "index.html")

new_tab_master = '''          <!-- 5 OPERACIONES CLAVE DE CONTROL AUTOMOTRIZ -->
          <div class="core-ops-container">
            <div class="core-ops-header">
              <h3>
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#38bdf8" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                PANEL DE CONTROL MAESTRO · CHANGAN X7 PLUS (5 OPERACIONES CLAVE)
              </h3>
              <span style="font-size: 12px; color: #94a3b8;">Control Directo ADB USB · F202_MCA</span>
            </div>

            <div class="core-ops-grid">
              
              <!-- CARD 1: BORRAR TODO Y VOLVER A FÁBRICA -->
              <div class="core-card">
                <div>
                  <div class="core-card-header">
                    <div class="core-card-icon red">🔴</div>
                    <div class="core-card-titles">
                      <h4>1. Borrar Todo y Dejar de Fábrica</h4>
                      <span class="core-card-tag red">ESTADO VIRGEN ORIGINAL</span>
                    </div>
                  </div>
                  <p class="core-card-desc">
                    Borra absolutamente todo lo instalado (Waze, Cockpit Launcher, RiMusic, servicios de fondo), devuelve el auto a <strong>Changan OnStyle original</strong> y restablece overscan, densidades y permisos como el primer día de fábrica.
                  </p>
                </div>
                <div class="core-card-actions">
                  <button class="btn-core red" id="btn-core-restore-factory">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                    🔴 BORRAR TODO Y VOLVER A FÁBRICA (1 CLIC)
                  </button>
                  <div class="core-card-footer">
                    <span>Último borrado:</span>
                    <strong id="ts-factory-restore">Nunca realizado</strong>
                  </div>
                </div>
              </div>

              <!-- CARD 2: APLICAR TODAS LAS MEJORAS CON 1 CLIC -->
              <div class="core-card" style="border-color: rgba(56, 189, 248, 0.4); box-shadow: 0 0 20px rgba(14, 165, 233, 0.15);">
                <div>
                  <div class="core-card-header">
                    <div class="core-card-icon cyan">⚡</div>
                    <div class="core-card-titles">
                      <h4>2. Aplicar Todas las Mejoras</h4>
                      <span class="core-card-tag cyan">SUITE COMPLETA RECOMENDADA</span>
                    </div>
                  </div>
                  <p class="core-card-desc">
                    Instala <strong>Cockpit X7 Plus Nativo</strong> (1920x720 sin franjas negras), bypass F202_SystemUI, satélites Callao para Waze, YouTube sin anuncios, RiMusic Hi-Fi, CarPlay y Android Auto en un solo paso automatizado.
                  </p>
                </div>
                <div class="core-card-actions">
                  <button class="btn-core cyan" id="btn-core-apply-all">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                    ⚡ APLICAR TODAS LAS MEJORAS (1 CLIC)
                  </button>
                  <div class="core-card-footer">
                    <span>Última aplicación:</span>
                    <strong id="ts-apply-all">Nunca realizado</strong>
                  </div>
                </div>
              </div>

              <!-- CARD 3: CONFIGURACIÓN GLOBAL DE MÁRGENES Y PANTALLA -->
              <div class="core-card">
                <div>
                  <div class="core-card-header">
                    <div class="core-card-icon blue">📐</div>
                    <div class="core-card-titles">
                      <h4>3. Ajuste Global de Pantalla & Márgenes</h4>
                      <span class="core-card-tag blue">¿BASTA CON UN SOLO AJUSTE? ¡SÍ!</span>
                    </div>
                  </div>
                  <p class="core-card-desc">
                    <strong>Explicación:</strong> Las franjas de 320px son barras añadidas por <code>F202_SystemUI</code>. Este ajuste global aplica <strong>overscan 0,0,0,0</strong>, <strong>1920x720 nativo @ 213 DPI</strong> y broadcast OEM. ¡No necesitas calibrar márgenes a mano nunca más!
                  </p>
                </div>
                <div class="core-card-actions">
                  <button class="btn-core blue" id="btn-core-global-margins">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                    📐 APLICAR AJUSTE GLOBAL DE MÁRGENES
                  </button>
                  <div class="core-card-footer">
                    <span>Última calibración:</span>
                    <strong id="ts-screen-config">Nunca realizado</strong>
                  </div>
                </div>
              </div>

              <!-- CARD 4: EXTRAER TODA LA INFORMACIÓN DEL AUTO (LOG COMPLETO) -->
              <div class="core-card">
                <div>
                  <div class="core-card-header">
                    <div class="core-card-icon emerald">📊</div>
                    <div class="core-card-titles">
                      <h4>4. Extraer Toda la Información (Log)</h4>
                      <span class="core-card-tag emerald">TELEMETRÍA COMPLETA DEL VEHÍCULO</span>
                    </div>
                  </div>
                  <p class="core-card-desc">
                    Genera un reporte técnico exhaustivo con fecha y hora: SoC MediaTek MT8666, memoria RAM real, capas de SystemUI, particiones, lista completa de paquetes instalados y registro logcat de eventos.
                  </p>
                </div>
                <div class="core-card-actions">
                  <button class="btn-core emerald" id="btn-core-export-telemetry">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                    📊 EXTRAER TELEMETRÍA Y GENERAR INFORME
                  </button>
                  <div id="telemetry-link-wrap" style="display:none; margin-top: 6px;">
                    <a id="telemetry-link" href="#" target="_blank" class="badge-link">📄 Ver / Descargar Último Informe</a>
                  </div>
                  <div class="core-card-footer">
                    <span>Última extracción:</span>
                    <strong id="ts-telemetry-export">Nunca realizado</strong>
                  </div>
                </div>
              </div>

              <!-- CARD 5: COPIA DE SEGURIDAD / CLONACIÓN DEL SISTEMA -->
              <div class="core-card">
                <div>
                  <div class="core-card-header">
                    <div class="core-card-icon purple">💾</div>
                    <div class="core-card-titles">
                      <h4>5. Copia de Seguridad del Sistema</h4>
                      <span class="core-card-tag purple">CLONAR AUTO PARA EMULAR EN PC</span>
                    </div>
                  </div>
                  <p class="core-card-desc">
                    Descarga por ADB los directorios originales del auto (<code>/system/priv-app</code>, <code>/system/app</code>, <code>/vendor/app</code>, <code>/system/framework</code> y <code>build.prop</code>) a tu PC para emular el sistema del vehículo con 100% de precisión.
                  </p>
                </div>
                <div class="core-card-actions">
                  <button class="btn-core purple" id="btn-core-system-backup">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                    💾 INICIAR COPIA DE SEGURIDAD DEL AUTO
                  </button>
                  <div id="backup-info-wrap" style="display:none; margin-top: 6px; font-size:12px; color:#c084fc;">
                    <span>Copia: <strong id="backup-info-dir">--</strong> (<span id="backup-info-count">0</span> archivos)</span>
                  </div>
                  <div class="core-card-footer">
                    <span>Último respaldo:</span>
                    <strong id="ts-system-backup">Nunca realizado</strong>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <!-- LIVE STEP-BY-STEP PROGRESS BOX -->
          <div class="master-progress-box" id="master-progress-box">
            <div class="master-steps-list" id="master-steps-list">
              <!-- Injected via JavaScript -->
            </div>
          </div>'''

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '<div class="master-card">'
end_marker = '<!-- QUICK INSTRUCTIONS CARD -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_tab_master + "\n\n          " + content[end_idx:]
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS: index.html updated with 5 Core Dashboard cards!")
else:
    print(f"FAILED: start_idx={start_idx}, end_idx={end_idx}")
