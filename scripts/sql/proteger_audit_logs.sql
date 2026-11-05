-- ==============================================================================
-- Script de Protección e Inmutabilidad de Audit Logs en PostgreSQL
-- Estándares: NIST SP 800-92 / OWASP Logging Cheat Sheet
-- ==============================================================================

-- 1. Función y Triggers para impedir UPDATE, DELETE o TRUNCATE en audit_logs
CREATE OR REPLACE FUNCTION proteger_audit_logs_func()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'VIOLACIÓN DE SEGURIDAD (NIST SP 800-92): La tabla audit_logs es inmutable. No se permite %, registro id=%', TG_OP, OLD.id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION proteger_audit_logs_truncate_func()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'VIOLACIÓN DE SEGURIDAD (NIST SP 800-92): No se permite TRUNCATE sobre la tabla audit_logs.';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger a nivel de fila para UPDATE o DELETE
DROP TRIGGER IF EXISTS trigger_bloqueo_modificacion_audit_logs ON audit_logs;
CREATE TRIGGER trigger_bloqueo_modificacion_audit_logs
BEFORE UPDATE OR DELETE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION proteger_audit_logs_func();

-- Trigger a nivel de sentencia para TRUNCATE
DROP TRIGGER IF EXISTS trigger_bloqueo_truncate_audit_logs ON audit_logs;
CREATE TRIGGER trigger_bloqueo_truncate_audit_logs
BEFORE TRUNCATE ON audit_logs
EXECUTE FUNCTION proteger_audit_logs_truncate_func();

-- 2. Permisos y Privilegios para el Rol de Aplicación (APP_DB_USER / app_user)
-- El rol app_user solo tiene permisos INSERT y SELECT sobre audit_logs
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
        -- Tablas de negocio: permisos operativos CRUD
        GRANT SELECT, INSERT, UPDATE, DELETE ON usuarios TO app_user;
        GRANT SELECT, INSERT, UPDATE, DELETE ON pacientes TO app_user;
        GRANT SELECT, INSERT, UPDATE, DELETE ON diagnosticos_cie10 TO app_user;
        GRANT SELECT, INSERT, UPDATE, DELETE ON accesos_emergencia TO app_user;
        
        -- Tabla de auditoría: MÍNIMO PRIVILEGIO (Solo INSERT y SELECT, jamás UPDATE ni DELETE)
        GRANT SELECT, INSERT ON audit_logs TO app_user;
        REVOKE UPDATE, DELETE, TRUNCATE ON audit_logs FROM app_user;
        
        -- Secuencias requeridas para autoincrementales
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
    END IF;
END $$;
