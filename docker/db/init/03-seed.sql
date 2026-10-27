-- Seed de datos demo para CriptoMed
-- Se ejecuta después de crear las tablas

-- Insertar usuarios demo (contraseña: admin123 para todos - hash bcrypt real)
INSERT INTO usuarios (nombre, password_hash, rol, email) VALUES
('Admin', '$2b$12$1jZzrRpg3d9PTUCINW1nPeGXbgaRUmujE9OG2N/4JN3wYNptbuTfq', 'admin', 'admin@criptomed.local'),
('Doctor Uno', '$2b$12$1jZzrRpg3d9PTUCINW1nPeGXbgaRUmujE9OG2N/4JN3wYNptbuTfq', 'doctor', 'doctor1@criptomed.local'),
('Admin Uno', '$2b$12$1jZzrRpg3d9PTUCINW1nPeGXbgaRUmujE9OG2N/4JN3wYNptbuTfq', 'administrativo', 'admin1@criptomed.local'),
('Auditor Uno', '$2b$12$1jZzrRpg3d9PTUCINW1nPeGXbgaRUmujE9OG2N/4JN3wYNptbuTfq', 'auditor', 'auditor1@criptomed.local'),
('Paciente Uno', '$2b$12$1jZzrRpg3d9PTUCINW1nPeGXbgaRUmujE9OG2N/4JN3wYNptbuTfq', 'paciente', 'paciente1@criptomed.local')
ON CONFLICT (email) DO NOTHING;

-- Insertar pacientes demo (sin doctor_id por ahora, se actualizará después)
INSERT INTO pacientes (nombre, apellido, fecha_nacimiento, dni, diagnostico, medicacion, resultado_test) VALUES
('Juan', 'Perez', '1980-01-15', '12345678', 'Diabetes tipo 2', 'Metformina 500mg', 'Glucosa 180 mg/dL'),
('Maria', 'Garcia', '1975-05-20', '87654321', 'Hipertension arterial', 'Losartan 50mg', 'Presion 140/90 mmHg')
ON CONFLICT (dni) DO NOTHING;

-- Insertar diagnosticos CIE10 de ejemplo
INSERT INTO diagnosticos_cie10 (codigo, descripcion) VALUES
('E11', 'Diabetes mellitus tipo 2'),
('I10', 'Hipertension esencial (primaria)'),
('J00', 'Rinofaringitis aguda (resfriado comun)'),
('U07.1', 'COVID-19, virus identificado')
ON CONFLICT (codigo) DO NOTHING;

