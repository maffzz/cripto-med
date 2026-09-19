import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'; // componentes de routing
import { AuthProvider, useAuth } from './context/AuthContext'; // proveedor y hook de autenticacion
import Login from './pages/Login'; // componente de login
import Dashboard from './pages/Dashboard'; // componente de dashboard
import PacienteDetalle from './pages/PacienteDetalle'; // componente de detalle de paciente
import AuditLog from './pages/AuditLog'; // componente de logs de auditoria
import MiHistorial from './pages/MiHistorial'; // componente de historial del paciente
import Layout from './components/Layout'; // componente de layout

// componente protegido que requiere autenticacion
const ProtectedRoute = () => { // componente de ruta protegida
  const { user, loading } = useAuth(); // usuario y estado de carga del contexto

  if (loading) return <div className="flex items-center justify-center h-64">cargando...</div>; // muestra cargando
  if (!user) return <Navigate to="/" replace />; // redirige a login si no esta autenticado

  return <Outlet />; // retorna outlet para rutas hijas
};

// componente que redirige según el rol
const RoleBasedRedirect = () => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/" replace />;

  // Redirigir según el rol
  if (user.rol === 'paciente') {
    return <Navigate to="/mi-historial" replace />;
  }
  return <Navigate to="/dashboard" replace />;
};

function App() { // componente principal
  return ( // retorna el router con todas las rutas
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/mi-historial" element={<MiHistorial />} />
              <Route path="/paciente/:id" element={<PacienteDetalle />} />
              <Route path="/audit-logs" element={<AuditLog />} />
              <Route path="/redirect" element={<RoleBasedRedirect />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App; // exporta el componente
