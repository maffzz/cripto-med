import { useState } from 'react'; // hook de estado
import { useNavigate } from 'react-router-dom'; // hook de navegacion
import { useAuth } from '../context/AuthContext'; // hook de autenticacion

const Login = () => { // componente de login
  const [email, setEmail] = useState(''); // estado del email
  const [password, setPassword] = useState(''); // estado del password
  const [error, setError] = useState(''); // estado del error
  const [loading, setLoading] = useState(false); // estado de carga
  const { login } = useAuth(); // funcion de login del contexto
  const navigate = useNavigate(); // funcion de navegacion

  const handleSubmit = async (e) => { // manejador del formulario
    e.preventDefault(); // previene comportamiento por defecto
    setError(''); // limpia error
    setLoading(true); // marca como cargando

    const result = await login(email, password); // intenta login
    if (result.success) { // si exitoso
      navigate('/dashboard'); // navega al dashboard
    } else { // si falla
      setError(result.error); // muestra error
    }
    setLoading(false); // marca como no cargando
  };

  return ( // retorna el formulario de login
    <div style={{ maxWidth: '400px', margin: '100px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2 style={{ textAlign: 'center' }}>login - criptomed</h2> // titulo
      <form onSubmit={handleSubmit}> // formulario
        <div style={{ marginBottom: '15px' }}> // campo email
          <label style={{ display: 'block', marginBottom: '5px' }}>email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}> // campo password
          <label style={{ display: 'block', marginBottom: '5px' }}>contraseña:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
          />
        </div>
        {error && <p style={{ color: 'red', marginBottom: '10px' }}>{error}</p>} // mensaje de error
        <button
          type="submit"
          disabled={loading}
          style={{ width: '100%', padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          {loading ? 'cargando...' : 'iniciar sesión'} // boton
        </button>
      </form>
      <div style={{ marginTop: '20px', fontSize: '12px', color: '#666' }}> // informacion de usuarios de prueba
        <p><strong>usuarios de prueba:</strong></p>
        <p>admin: admin@criptomed.com / admin123</p>
        <p>doctor: doctor@criptomed.com / doctor123</p>
        <p>administrativo: admin@clinica.com / admin123</p>
        <p>auditor: auditor@criptomed.com / auditor123</p>
      </div>
    </div>
  );
};

export default Login; // exporta el componente
