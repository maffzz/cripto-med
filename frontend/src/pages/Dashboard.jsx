import { useState, useEffect } from 'react'; // hooks de react
import { useAuth } from '../context/AuthContext'; // hook de autenticacion
import axios from 'axios'; // cliente http

const Dashboard = () => { // componente de dashboard
  const { user, logout } = useAuth(); // usuario y funcion de logout del contexto
  const [pacientes, setPacientes] = useState([]); // estado de pacientes
  const [loading, setLoading] = useState(true); // estado de carga
  const [error, setError] = useState(''); // estado de error

  useEffect(() => { // efecto al cargar
    const fetchPacientes = async () => { // funcion asincrona para obtener pacientes
      try {
        const response = await axios.get('http://127.0.0.1:8000/pacientes'); // llama al endpoint de pacientes
        setPacientes(response.data); // guarda pacientes en estado
      } catch (err) { // captura error
        console.error('error al obtener pacientes:', err); // log error
        setError('error al cargar pacientes'); // muestra error
      } finally {
        setLoading(false); // marca como no cargando
      }
    };
    fetchPacientes(); // ejecuta funcion
  }, []);

  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>cargando...</div>; // muestra cargando
  if (error) return <div style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>{error}</div>; // muestra error

  return ( // retorna el dashboard
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}> // header
        <h1>dashboard - criptomed</h1>
        <div>
          <span style={{ marginRight: '20px' }}>usuario: {user?.nombre} ({user?.rol})</span> // muestra usuario y rol
          <button onClick={logout} style={{ padding: '8px 16px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}> // boton logout
            cerrar sesión
          </button>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}> // estadisticas
        <h2>estadísticas</h2>
        <p>total de pacientes: {pacientes.length}</p>
      </div>

      <div> // tabla de pacientes
        <h2>pacientes recientes (primeros 50)</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}> // tabla
          <thead> // encabezado
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>nombre</th>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>edad</th>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>genero</th>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>diagnóstico</th>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>hospital</th>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>fecha admisión</th>
            </tr>
          </thead>
          <tbody> // cuerpo
            {pacientes.map((paciente) => ( // mapea pacientes
              <tr key={paciente.id}> // fila por paciente
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{paciente.nombre_descifrado}</td> // nombre descifrado
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{paciente.edad}</td> // edad
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{paciente.genero}</td> // genero
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{paciente.diagnostico_descifrado}</td> // diagnostico descifrado
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{paciente.hospital}</td> // hospital
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{new Date(paciente.fecha_admision).toLocaleDateString()}</td> // fecha formateada
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard; // exporta el componente
