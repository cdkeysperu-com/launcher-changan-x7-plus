# Guía de Contribución al Proyecto Changan Oshan X7 Cockpit Suite 🏎️💨

¡Muchas gracias por querer mejorar este proyecto! Este ecosistema nació para darle a todos los propietarios de **Changan Oshan X7 / X7 Plus** una experiencia de infoentretenimiento moderna, fluida y sin restricciones.

Toda la suite es **100% libre, comunitaria y Open Source**. Tu ayuda es clave para seguir expandiendo el soporte a más versiones y modelos.

---

## 🎯 ¿En qué puedes colaborar?

1. **Mapeo de Teclas del Timón y Consola (Keycodes / Scancodes):**
   * Diferentes años o versiones (Comfort, Elite, Luxury) pueden enviar códigos CAN-Bus o Linux Input distintos.
   * Si tienes una laptop conectada al auto, corre `1_MAPEAR_TECLAS_EN_VIVO.bat`, presiona los botones de tu volante y abre un Issue o Pull Request con tus códigos.
2. **Nuevos Lanzadores o Temas Visuales:**
   * Optimización de fondos de pantalla ultra-panorámicos (1920x720).
   * Nuevos widgets de clima, tacómetro, velocímetro GPS o medidores digitales.
3. **Optimización de Aplicaciones:**
   * Adaptación de reproductores de música (SimpMusic, ViMusic) o navegadores (Waze, Magic Earth) para evitar que la barra de notificaciones tape botones clave.
4. **Traducción y Soporte Multi-idioma:**
   * Soporte en inglés, árabe, ruso u otros idiomas para la comunidad internacional de Changan.
5. **Corrección de Bugs y Documentación:**
   * Reporte de incompatibilidades con versiones específicas de firmware de Changan (OnStyle / F202).

---

## 🛠️ Flujo de Trabajo para Enviar Mejoras (Pull Requests)

1. **Haz un Fork** del repositorio en GitHub.
2. **Crea una rama descriptiva** para tu mejora:
   ```bash
   git checkout -b feature/mapeo-volante-luxury-2025
   ```
3. **Realiza tus cambios y pruébalos** (puedes usar el emulador de PC o probar en tu auto).
4. **Haz commit con mensajes claros:**
   ```bash
   git commit -m "feat: agrega scancodes para botones de camara y modo en volante 2025"
   ```
5. **Haz Push a tu fork:**
   ```bash
   git push origin feature/mapeo-volante-luxury-2025
   ```
6. **Abre un Pull Request** explicando qué probaste y qué modelo de vehículo usaste.

---

## 💬 Canales de Contacto y Comunidad

* **Issues de GitHub:** Para reportar errores técnicos, pantallazos o sugerencias de código.
* **Comunidad y Soporte Oficial:** [CDKeys Perú](https://cdkeysperu.com)
* **Instalaciones Asistidas:** Si necesitas apoyo guiado o remoto, contáctanos a través de los canales comunitarios en el README.
