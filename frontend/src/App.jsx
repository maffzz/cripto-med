import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'; // componentes de routing
import { AuthProvider, useAuth } from './context/AuthContext'; // proveedor y hook de autenticacion
import Login from './pages/Login'; // componente de login
import Dashboard from './pages/Dashboard'; // componente de dashboard
import PacienteDetalle from './pages/PacienteDetalle'; // componente de detalle de paciente
import AuditLog from './pages/AuditLog'; // componente de logs de auditoria
import Layout from './components/Layout'; // componente de layout

// componente protegido que requiere autenticacion
const ProtectedRoute = ({ children }) => { // componente de ruta protegida
  const { user, loading } = useAuth(); // usuario y estado de carga del contexto
  
  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>cargando...</div>; // muestra cargando
  if (!user) return <Navigate to="/" replace />; // redirige a login si no esta autenticado
  
  return <Layout>{children}</Layout>; // retorna layout con hijos
};

function App() { // componente principal
  return ( // retorna el router con todas las rutas
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route // ruta protegida de dashboard
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route // ruta protegida de detalle de paciente
            path="/paciente/:id"
            element={
              <ProtectedRoute>
                <PacienteDetalle />
              </ProtectedRoute>
            }
          />
          <Route // ruta protegida de logs de auditoria
            path="/audit-logs"
            element={
              <ProtectedRoute>
                <AuditLog />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App; // exporta el componente
