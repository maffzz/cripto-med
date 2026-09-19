import { Outlet, useNavigate, useLocation } from 'react-router-dom'; // hooks de navegacion
import { useAuth } from '../context/AuthContext'; // hook de autenticacion

const Layout = () => { // componente de layout
  const { user, logout } = useAuth(); // usuario y funcion de logout del contexto
  const navigate = useNavigate(); // funcion de navegacion
  const location = useLocation(); // ubicacion actual

  return ( // retorna el layout con navbar
    <div>
      <nav style={{ backgroundColor: '#343a40', padding: '15px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ color: 'white', margin: 0, fontSize: '24px' }}>criptomed</h1>
        </div>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <button
            onClick={() => navigate('/dashboard')}
            style={{ backgroundColor: 'transparent', color: 'white', border: 'none', cursor: 'pointer', fontSize: '16px', textDecoration: location.pathname === '/dashboard' ? 'underline' : 'none' }}
          >
            dashboard
          </button>
          {(user?.rol === 'admin' || user?.rol === 'auditor') && ( // solo admin y auditor ven logs
            <button
              onClick={() => navigate('/audit-logs')}
              style={{ backgroundColor: 'transparent', color: 'white', border: 'none', cursor: 'pointer', fontSize: '16px', textDecoration: location.pathname === '/audit-logs' ? 'underline' : 'none' }}
            >
              logs de auditoría
            </button>
          )}
          <button
            onClick={logout}
            style={{ padding: '8px 16px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            cerrar sesión
          </button>
        </div>
      </nav>
      <main style={{ padding: '20px' }}>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout; // exporta el componente
