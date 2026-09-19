# Procedimientos de Notificación - CriptoMed

## Resumen Ejecutivo
Este documento describe los procedimientos de notificación en caso de incidentes de seguridad o fugas de datos en el sistema CriptoMed.

## 1. Marco Legal

### 1.1 Ley Peruana N° 29733
- Artículo 10: Notificación de incidentes de seguridad a la Autoridad de Protección de Datos Personales (ARDA)
- Plazo: 72 horas desde el conocimiento del incidente
- Contenido mínimo: Descripción del incidente, medidas tomadas, medidas propuestas

### 1.2 ISO 27001
- Control A.16.1.5: Comunicación de incidentes de seguridad
- Debe haber procedimientos formales de notificación
- Debe documentarse a quién, cuándo y cómo notificar

### 1.3 Otros Marcos (si aplica)
- HIPAA (EE.UU.): Notificación dentro de 60 días
- GDPR (UE): Notificación dentro de 72 horas
- Ley de Protección de Datos de otros países (si aplica)

## 2. Categorías de Notificación

### 2.1 Notificación Interna
**A quién:**
- Equipo de respuesta a incidentes
- Dirección de la organización
- Personal de seguridad
- Personal legal

**Cuándo:**
- Inmediatamente al detectar el incidente
- Durante el proceso de contención
- Al finalizar la recuperación

**Cómo:**
- Email urgente (prioridad alta)
- Llamada telefónica para incidentes críticos
- Reunión de emergencia para incidentes de nivel 1-2

### 2.2 Notificación a Autoridades
**A quién:**
- ARDA (Autoridad de Protección de Datos Personales - Perú)
- Fiscalía si hay evidencia de delito
- Policía si hay evidencia de robo de datos
- Reguladores sectoriales (Ministerio de Salud, etc.)

**Cuándo:**
- ARDA: Dentro de 72 horas
- Fiscalía/Policía: Inmediatamente si hay evidencia de delito
- Reguladores: Según normativa específica

**Cómo:**
- Email formal a ARDA
- Denuncia formal a Fiscalía/Policía
- Informe técnico y legal

### 2.3 Notificación a Pacientes Afectados
**A quién:**
- Pacientes cuyos datos fueron comprometidos
- Familiares si aplica
- Representantes legales si aplica

**Cuándo:**
- Sin demora indebida (idealmente dentro de 48-72 horas)
- Según regulación aplicable

**Cómo:**
- Email (prioridad alta)
- Carta certificada (si no hay email)
- Llamada telefónica (para incidentes críticos)
- Aviso en sitio web (para incidentes masivos)

### 2.4 Notificación a Stakeholders
**A quién:**
- Junta directiva
- Inversionistas (si aplica)
- Proveedores afectados
- Partes interesadas

**Cuándo:**
- Después de contención inicial
- Según gravedad del incidente

**Cómo:**
- Email formal
- Reunión de briefing
- Informe ejecutivo

### 2.5 Notificación Pública
**A quién:**
- Medios de comunicación
- Público general
- Comunidad médica

**Cuándo:**
- Solo si el incidente es de conocimiento público
- Según estrategia de comunicación

**Cómo:**
- Comunicado de prensa
- Aviso en sitio web
- Conferencia de prensa (si aplica)

## 3. Plantillas de Notificación

### 3.1 Plantilla de Notificación a ARDA

**Asunto:** Notificación de Incidente de Seguridad - CriptoMed - [Fecha]

**Para:** incidentes@ard.gob.pe

**Contenido:**

```
ARDA - Autoridad de Protección de Datos Personales

Notificación de Incidente de Seguridad - Ley N° 29733

1. Identificación del Responsable:
   - Nombre: [Nombre de la organización]
   - RUC: [RUC]
   - Dirección: [Dirección]
   - Contacto: [Email, Teléfono]

2. Descripción del Incidente:
   - Tipo de incidente: [Fuga de datos / Acceso no autorizado / Ransomware / Otro]
   - Fecha de detección: [Fecha y hora]
   - Fecha de inicio del incidente: [Fecha y hora estimada]
   - Causa raíz: [Descripción]
   - Datos afectados: [Tipos de datos afectados]

3. Categoría de Datos Afectados:
   - Datos sensibles de salud: [Sí/No]
   - Datos personales: [Sí/No]
   - Cantidad de registros afectados: [Número]

4. Personas Afectadas:
   - Número aproximado de personas afectadas: [Número]
   - Grupos específicos afectados: [Descripción]

5. Medidas Tomadas:
   - Contención: [Descripción]
   - Erradicación: [Descripción]
   - Recuperación: [Descripción]
   - Medidas para evitar recurrencia: [Descripción]

6. Medidas Propuestas:
   - [Descripción de mejoras adicionales]

7. Evidencia:
   - [Anexar logs, informes técnicos, etc.]

8. Contacto para Seguimiento:
   - Nombre: [Nombre del contacto]
   - Email: [Email]
   - Teléfono: [Teléfono]

Atentamente,

[Nombre del responsable]
[Cargo]
[Fecha]
```

### 3.2 Plantilla de Notificación a Pacientes

**Asunto:** Información Importante sobre Seguridad de sus Datos Personales - CriptoMed

**Para:** [Email del paciente]

**Contenido:**

```
Estimado/a [Nombre del paciente],

Le escribimos para informarle sobre un incidente de seguridad que ha afectado sus datos personales en el sistema CriptoMed.

1. Qué sucedió:
   El [fecha], detectamos un incidente de seguridad que comprometió [descripción de datos afectados].

2. Qué datos fueron afectados:
   - [Tipo de datos 1]
   - [Tipo de datos 2]
   - [Otros datos]

3. Qué estamos haciendo:
   - Hemos contenido el incidente
   - Hemos revocado las credenciales comprometidas
   - Hemos implementado medidas adicionales de seguridad
   - Estamos cooperando con las autoridades

4. Qué puede hacer usted:
   - Estar atento a comunicaciones sospechosas
   - Monitorear sus cuentas bancarias si datos financieros fueron afectados
   - Reportar cualquier actividad sospechosa

5. Recursos disponibles:
   - Línea de ayuda: [Teléfono]
   - Email: [Email]
   - Horario: [Horario]

6. Sus derechos:
   - Tiene derecho a solicitar más información sobre el incidente
   - Tiene derecho a solicitar corrección de datos si aplica
   - Tiene derecho a presentar reclamo a ARDA

Lamentamos profundamente este incidente y nos comprometemos a tomar todas las medidas necesarias para proteger sus datos.

Atentamente,

[Nombre del responsable]
[Cargo]
CriptoMed
[Fecha]
```

### 3.3 Plantilla de Notificación Interna

**Asunto:** INCIDENTE DE SEGURIDAD - [Nivel de Severidad] - [Fecha]

**Para:** Equipo de Respuesta a Incidentes

**Contenido:**

```
INCIDENTE DE SEGURIDAD DETECTADO

Nivel de Severidad: [1-Crítico / 2-Alto / 3-Medio / 4-Bajo / 5-Informativo]

Fecha de Detección: [Fecha y hora]
Tipo de Incidente: [Fuga de datos / Acceso no autorizado / Ransomware / Otro]

Descripción:
[Descripción detallada del incidente]

Impacto Estimado:
- Número de pacientes afectados: [Número]
- Tipos de datos afectados: [Descripción]
- Servicios afectados: [Descripción]

Acciones Inmediatas:
[Lista de acciones tomadas]

Próximos Pasos:
[Lista de próximas acciones]

Contacto de Emergencia:
- IRM: [Nombre, Email, Teléfono]
- Technical Lead: [Nombre, Email, Teléfono]
- Legal Counsel: [Nombre, Email, Teléfono]

Confirmar recepción de este email inmediatamente.
```

### 3.4 Plantilla de Comunicado de Prensa

**Título:** CriptoMed Notifica Incidente de Seguridad y Toma Medidas Inmediatas

**Contenido:**

```
[CIUDAD], [Fecha] - CriptoMed anuncia hoy que ha detectado un incidente de seguridad que ha afectado datos personales de pacientes.

Detalles del Incidente:
El [fecha], detectamos [descripción del incidente]. Estamos investigando activamente la situación y cooperando con las autoridades.

Datos Afectados:
El incidente afectó [número] pacientes e incluyó [tipos de datos].

Medidas Tomadas:
- Hemos contenido el incidente inmediatamente
- Hemos notificado a las autoridades correspondientes
- Estamos notificando a los pacientes afectados
- Hamos implementado medidas adicionales de seguridad

Compromiso con la Seguridad:
La seguridad de los datos de nuestros pacientes es nuestra máxima prioridad. Estamos tomando todas las medidas necesarias para proteger la información y evitar que incidentes similares ocurran en el futuro.

Contacto para Prensa:
[Nombre]
[Email]
[Teléfono]

### About CriptoMed
[Breve descripción de la organización]
```

## 4. Procedimiento de Notificación

### 4.1 Flujo de Notificación

**Paso 1: Detección (0-2 horas)**
- Detectar incidente
- Clasificar severidad
- Notificar a IRM (Incident Response Manager)

**Paso 2: Contención (2-6 horas)**
- Contener incidente
- Notificar a equipo de respuesta
- Iniciar investigación

**Paso 3: Evaluación (6-24 horas)**
- Determinar alcance del incidente
- Identificar pacientes afectados
- Preparar notificaciones

**Paso 4: Notificación (24-72 horas)**
- Notificar a autoridades (72 horas)
- Notificar a pacientes (48-72 horas)
- Notificar a stakeholders (según severidad)

**Paso 5: Seguimiento (72 horas+)**
- Proporcionar actualizaciones
- Responder preguntas
- Documentar lecciones aprendidas

### 4.2 Árbol de Decisión de Notificación

```
¿El incidente compromete datos personales?
├─ Sí
│  ├─ ¿Más de 1000 pacientes afectados?
│  │  ├─ Sí → Notificar a autoridades, pacientes, prensa
│  │  └─ No → Notificar a autoridades, pacientes
│  └─ ¿Hay evidencia de mal uso?
│     ├─ Sí → Notificar a Fiscalía/Policía además de autoridades
│     └─ No → Notificar solo a autoridades
└─ No → Notificación interna únicamente
```

## 5. Cronograma de Notificación

| Evento | Tiempo | Responsable |
|--------|--------|-------------|
| Detección de incidente | 0h | Cualquier usuario |
| Notificación a IRM | 0-2h | Detector |
| Notificación a equipo de respuesta | 2-4h | IRM |
| Notificación a dirección | 4-6h | IRM |
| Notificación a autoridades | 48-72h | Legal Counsel |
| Notificación a pacientes | 48-72h | Communications Lead |
| Notificación a stakeholders | 72h+ | Communications Lead |
| Notificación pública (si aplica) | 72h+ | Communications Lead |

## 6. Canales de Comunicación

### 6.1 Canales Internos
- Email: seguridad@criptomed.utec.edu.pe
- Slack: #incident-response
- Teléfono: [Número interno]
- Reunión: Sala de emergencias

### 6.2 Canales Externos
- ARDA: incidentes@ard.gob.pe
- Fiscalía: [Email específico]
- Pacientes: comunicaciones@criptomed.utec.edu.pe
- Prensa: prensa@criptomed.utec.edu.pe

## 7. Registro de Notificaciones

### 7.1 Log de Notificaciones
Todas las notificaciones deben registrarse en un log que incluya:
- Fecha y hora de notificación
- Destinatario
- Canal de comunicación
- Contenido de la notificación
- Confirmación de recepción
- Respuesta recibida

### 7.2 Evidencia
Preservar evidencia de notificaciones:
- Copias de emails enviados
- Registros de llamadas
- Acuses de recibo
- Respuestas recibidas

## 8. Capacitación

### 8.1 Capacitación sobre Notificación
- Todo el personal debe conocer procedimientos de notificación
- IRM y Communications Lead deben tener capacitación avanzada
- Simulacros de notificación cada 6 meses

### 8.2 Checklist de Notificación
- [ ] Identificar incidente
- [ ] Clasificar severidad
- [ ] Notificar a IRM
- [ ] Notificar a equipo de respuesta
- [ ] Determinar alcance
- [ ] Identificar pacientes afectados
- [ ] Preparar notificaciones
- [ ] Notificar a autoridades
- [ ] Notificar a pacientes
- [ ] Notificar a stakeholders
- [ ] Registrar notificaciones
- [ ] Seguimiento

---

## Resumen Ejecutivo

**Objetivo:** Notificar incidentes de seguridad de forma oportuna y completa

**Principios:**
- Notificación a autoridades dentro de 72 horas (Ley N° 29733)
- Notificación a pacientes sin demora indebida
- Notificación interna inmediata
- Preservación de evidencia de notificaciones

**Métricas:**
- Tiempo de notificación a autoridades: < 72 horas
- Tiempo de notificación a pacientes: < 72 horas
- Porcentaje de pacientes notificados: 100%
