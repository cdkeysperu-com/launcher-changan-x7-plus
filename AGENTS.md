# 🤖 PROTOCOLO DE TRABAJO - OSHAN X7 VIRTUAL

> **Proyecto:** ${pName}  
> **Protocolo:** Memoria Viva ACTIVE_CONTEXT.md y Checkpoints Git  
> **Objetivo:** Cero redundancia, mínimo consumo de tokens, arranque instantáneo y memoria persistente.

---

## ⚡ Regla 1: Protocolo de Arranque (Fast Bootstrap)
1. Al iniciar cualquier sesión de trabajo en este proyecto, lee **ÚNICAMENTE** `ACTIVE_CONTEXT.md`.
2. **NUNCA** leas carpetas `.historico/` ni logs antiguos a menos que el usuario lo solicite expresamente.
3. Verifica el estado del repositorio Git con `git status -s` o el último commit.

---

## 🛑 Regla 2: Prohibición de Informes Acumulativos
* **PROHIBIDO** crear archivos como `informe_faseX.md`, `resumen_hoy.md` o crear carpetas de `avances/` o `informes/`.
* Todo progreso, decisión técnica, resolución de bugs y tareas pendientes se registra **sobrescribiendo y actualizando directamente `ACTIVE_CONTEXT.md`**.

---

## 🧠 Regla 3: Auditoría de Errores (Caminos Resueltos vs Descartados)
Cuando resuelvas un problema técnico complejo o descubras un enfoque que no funciona en OSHAN X7 VIRTUAL:
* **✅ Resuelto:** Regístralo en la sección de errores resueltos con su causa raíz y solución blindada.
* **❌ Camino Descartado:** Qué se probó y por qué es una mala idea (para que ni tú ni futuras sesiones vuelvan a tropezar con la misma piedra).

---

## 🛡️ Regla 4: Ensayo y Error Autónomo (Git Guardrails)
1. Antes de realizar cambios destructivos o probar soluciones experimentales, asegura un commit o punto de control limpio.
2. Si un intento de refactorización o prueba genera errores insalvables, **haz rollback de inmediato (`git checkout .` o `git reset --hard`)**. No dejes código roto ni escribas informes narrando el fallo.
3. Si el cambio funciona y supera las pruebas, haz commit descriptivo y actualiza `ACTIVE_CONTEXT.md`.
