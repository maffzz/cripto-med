-- Script de demostración: alterar un log de auditoría
-- Simula un atacante con privilegios de superusuario que intenta ocultar evidencia
-- Ejecutar como: docker compose exec -T db psql -U criptomed -d criptomed < scripts/demo_alterar_log.sql

-- Paso 1: Desactivar el trigger de protección de audit_logs
ALTER TABLE audit_logs DISABLE TRIGGER ALL;

-- Paso 2: Modificar el campo recurso de una fila intermedia
-- Buscamos una fila intermedia (ni la primera ni la última) para que la cadena se rompa
UPDATE audit_logs
SET recurso = 'paciente:fabricado-para-demo'
WHERE seq = (
    SELECT seq FROM audit_logs
    ORDER BY seq
    LIMIT 1 OFFSET 5
);

-- Paso 3: Volver a activar el trigger
ALTER TABLE audit_logs ENABLE TRIGGER ALL;

-- Nota: En un entorno real sin privilegios de superusuario, el trigger y los permisos
-- impedirían esta modificación. Esta demo simula un atacante que ha comprometido
-- el servidor de base de datos con privilegios elevados.
