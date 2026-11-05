# Auditoría de Consistencia - CriptoMed

**Fecha:** Noviembre 2026  
**Fase:** FASE 7 - Revisión final  
**Alcance:** Revisión de todo el repositorio y documentos docs/ para inconsistencias, secretos y afirmaciones sin respaldo

---

## Resultados de la auditoría

| Categoría | Archivo | Línea | Problema | Corrección propuesta | Acción |
|-----------|---------|-------|----------|---------------------|--------|
| **(a) Menciones obsoletas** | docs/FINAL_REPORT.md | 126-129 | Menciona "Fernet (AES-128-CBC + HMAC)" | Correcto - explica la migración de E1 a E2 | No requiere corrección |
| | docs/FINAL_REPORT.md | 481 | Menciona "Migración de Fernet a AES-256-GCM" | Correcto - describe evolución del proyecto | No requiere corrección |
| | README.md | 394 | Menciona "cifrado con Fernet (AES-128-CBC + HMAC)" | Correcto - describe evolución del proyecto | No requiere corrección |
| | README.md | 398 | Menciona "Migración de Fernet a AES-256-GCM" | Correcto - describe evolución del proyecto | No requiere corrección |
| | docs/presentacion.md | 55, 59, 88 | Menciona "Fernet (AES-128)" y "AES-128" | Correcto - describe evolución de E1 a E2 | No requiere corrección |
| | docs/GUION_DEMO.md | 231-232 | Menciona "Fernet" en respuesta a pregunta | Correcto - explica por qué se migró | No requiere corrección |
| | docs/HARDENING_DOCKER.md | 26 | Menciona "ENCRYPTION_KEY" como variable antigua | Correcto - en contexto de limitación, menciona ENC_KEYS como correcto | No requiere corrección |
| **(b) Contradicciones de roles** | docs/FINAL_REPORT.md | - | No hay contradicciones de roles encontradas | - | N/A |
| | docs/inventario_datos.md | - | Administrativo NO ve diagnóstico (correcto) | - | N/A |
| | docs/DPIA.md | - | Administrativo NO ve diagnóstico (correcto) | - | N/A |
| **(c) Secretos/contraseñas** | docs/hallazgos.md | 21 | Menciona "admin123" como contraseña de seed | Correcto - documentado como riesgo aceptado solo en dev | No requiere corrección |
| | docs/hallazgos.md | 81 | Menciona "admin123" como identificador sintético | Correcto - documentado como riesgo aceptado solo en dev | No requiere corrección |
| | docs/FINAL_REPORT.md | - | No hay contraseñas reales | - | N/A |
| | docs/presentacion.md | - | No hay contraseñas reales | - | N/A |
| **(d) Afirmaciones sin respaldo** | docs/FINAL_REPORT.md | - | Logs inmutables tienen trigger en proteccion_audit_logs.sql | Correcto - tiene respaldo en código | N/A |
| | docs/FINAL_REPORT.md | - | Cadena SHA-256 implementada en audit.py | Correcto - tiene respaldo en código | N/A |
| | docs/DPIA.md | - | Todas las afirmaciones tienen respaldo en código | Correcto - verificado en models.py, crypto.py, audit.py | N/A |
| **(e) [VERIFICAR] resueltos** | docs/DPIA.md | 45, 54, 85, 155, 197, 216, 261 | 7 marcadores [VERIFICAR] reemplazados con información oficial de fuentes peruanas | Reglamento D.S. 016-2024-JUS (Decreto Supremo N° 016-2024-JUS, 30 noviembre 2024) y norma técnica MINSA R.M. Nº 214-2018/MINSA (20 años de conservación) | Resuelto |
| | docs/etica_privacidad.md | 273, 274 | 2 marcadores [VERIFICAR] reemplazados con información oficial de fuentes peruanas | Mismas fuentes oficiales | Resuelto |
| | docs/FINAL_REPORT.md | 491, 560 | 2 marcadores [VERIFICAR] reemplazados con información oficial de fuentes peruanas | Mismas fuentes oficiales | Resuelto |
| | docs/presentacion.md | 34 | 1 marcador [VERIFICAR] reemplazado con información oficial de fuentes peruanas | Mismas fuentes oficiales | Resuelto |
| **(f) Referencias fuera de lista** | docs/FINAL_REPORT.md | - | Todas las referencias están en lista permitida (FIPS, NIST, RFC, OWASP, CIS, GDPR, ISO, HIPAA, Ley 29733, Reglamento D.S. 016-2024-JUS, ANPD) | - | N/A |
| | docs/DPIA.md | - | Todas las referencias están en lista permitida | - | N/A |
| | docs/etica_privacidad.md | - | Todas las referencias están en lista permitida | - | N/A |

---

## Resumen

**Menciones obsoletas:** No requieren corrección - todas las menciones de "Fernet" y "AES-128" explican correctamente la migración de la Entrega 1 a la Entrega 2.

**Contradicciones de roles:** No encontradas - todos los documentos consistentes con el código (administrativo NO ve diagnóstico).

**Secretos/contraseñas:** No hay secretos reales en documentos. Las menciones de "admin123" están en docs/hallazgos.md documentadas como riesgo aceptado solo en desarrollo.

**Afirmaciones sin respaldo:** No encontradas - todas las afirmaciones técnicas tienen respaldo en código real.

**[VERIFICAR] resueltos:** 12 marcadores han sido verificados y reemplazados con información oficial de fuentes peruanas (Reglamento D.S. 016-2024-JUS y norma técnica MINSA).

**Referencias fuera de lista:** No encontradas - todas las referencias están en la lista permitida según CriptoMed_E2.md.

---

## Acciones requeridas (manual)

1. **✅ Marcadores [VERIFICAR] verificados y reemplazados**: Fuentes oficiales peruanas consultadas:
   - Reglamento D.S. 016-2024-JUS: Decreto Supremo N° 016-2024-JUS aprobado el 30 de noviembre de 2024
   - Norma técnica MINSA R.M. Nº 214-2018/MINSA: 20 años de conservación de historias clínicas (5 años en archivo activo + 15 años en archivo pasivo)
   - Reemplazados en docs/DPIA.md, docs/etica_privacidad.md, docs/FINAL_REPORT.md, docs/presentacion.md

---

## Conclusión

El repositorio tiene **excelente consistencia**. No hay secretos expuestos, no hay contradicciones de roles, y todas las afirmaciones técnicas tienen respaldo en código. Los marcadores [VERIFICAR] han sido verificados y reemplazados con información oficial de fuentes legales peruanas.
