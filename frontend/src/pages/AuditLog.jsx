import { useState, useEffect } from 'react'; // hooks de react
import { useAuth } from '../context/AuthContext'; // hook de autenticacion
import axios from 'axios'; // cliente http

const AuditLog = () => { // componente de logs de auditoria
  const { user, logout } = useAuth(); // usuario y funcion de logout del contexto
  const [logs, setLogs] = useState([]); // estado de logs
  const [loading, setLoading] = useState(true); // estado de carga
  const [error, setError] = useState(''); // estado de error
  const [page, setPage] = useState(1); // estado de pagina
  const [total, setTotal] = useState(0); // estado total de registros

  useEffect(() => { // efecto al cargar
    const fetchLogs = async () => { // funcion asincrona para obtener logs
      try {
        const response = await axios.get(`http://127.0.0.1:8000/audit-logs?page=${page}&page_size=20`); // llama al endpoint de logs
        setLogs(response.data.items); // guarda logs en estado
        setTotal(response.data.total); // guarda total en estado
      } catch (err) { // captura error
        console.error('error al obtener logs:', err); // log error
        setError('error al cargar logs de auditoría'); // muestra error
      } finally {
        setLoading(false); // marca como no cargando
      }
    };
    fetchLogs(); // ejecuta funcion
  }, [page]);

  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>cargando...</div>; // muestra cargando
  if (error) return <div style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>{error}</div>; // muestra error

  return ( // retorna los logs de auditoria
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}> // header
        <h1>logs de auditoría - criptomed</h1>
        <div>
          <span style={{ marginRight: '20px' }}>usuario: {user?.nombre} ({user?.rol})</span> // muestra usuario y rol
          <button onClick={logout} style={{ padding: '8px 16px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}> // boton logout
            cerrar sesión
          </button>
        </div>
      </div>

      <div style={{ marginBottom: '20px' }}> // estadisticas
        <p>total de registros: {total}</p>
      </div>

      <div> // tabla de logs
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}> // tabla
          <thead> // encabezado
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>timestamp</th>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>usuario id</th>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>acción</th>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>recurso</th>
              <th style={{ padding: '10px', border: '1px solid #dee2e6', textAlign: 'left' }}>ip origen</th>
            </tr>
          </thead>
          <tbody> // cuerpo
            {logs.map((log) => ( // mapea logs
              <tr key={log.id}> // fila por log
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{new Date(log.timestamp).toLocaleString()}</td> // timestamp formateado
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{log.usuario_id}</td> // usuario id
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{log.accion}</td> // accion
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{log.recurso}</td> // recurso
                <td style={{ padding: '10px', border: '1px solid #dee2e6' }}>{log.ip_origen}</td> // ip origen
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: '20px' }}> // paginacion
        <button
          onClick={() => setPage(page - 1)}
          disabled={page === 1}
          style={{ padding: '8px 16px', marginRight: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: page === 1 ? 'not-allowed' : 'pointer' }}
        >
          anterior
        </button>
        <span>página {page}</span>
        <button
          onClick={() => setPage(page + 1)}
          disabled={page * 20 >= total}
          style={{ padding: '8px 16px', marginLeft: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: page * 20 >= total ? 'not-allowed' : 'pointer' }}
        >
          siguiente
        </button>
      </div>
    </div>
  );
};

export default AuditLog; // exporta el componente
