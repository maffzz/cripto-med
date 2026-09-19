import { useState, useEffect } from 'react'; // hooks de react
import { useParams, useNavigate } from 'react-router-dom'; // hooks de navegacion
import axios from 'axios'; // cliente http

const PacienteDetalle = () => { // componente de detalle de paciente
  const { id } = useParams(); // obtiene id de la url
  const navigate = useNavigate(); // funcion de navegacion
  const [paciente, setPaciente] = useState(null); // estado del paciente
  const [loading, setLoading] = useState(true); // estado de carga
  const [error, setError] = useState(''); // estado de error

  useEffect(() => { // efecto al cargar
    const fetchPaciente = async () => { // funcion asincrona para obtener paciente
      try {
        const response = await axios.get(`http://127.0.0.1:8000/pacientes/${id}`); // llama al endpoint de paciente
        setPaciente(response.data); // guarda paciente en estado
      } catch (err) { // captura error
        console.error('error al obtener paciente:', err); // log error
        setError('error al cargar paciente'); // muestra error
      } finally {
        setLoading(false); // marca como no cargando
      }
    };
    fetchPaciente(); // ejecuta funcion
  }, [id]);

  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>cargando...</div>; // muestra cargando
  if (error) return <div style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>{error}</div>; // muestra error
  if (!paciente) return <div style={{ textAlign: 'center', marginTop: '50px' }}>paciente no encontrado</div>; // paciente no encontrado

  return ( // retorna el detalle del paciente
    <div style={{ padding: '20px' }}>
      <button onClick={() => navigate('/dashboard')} style={{ marginBottom: '20px', padding: '8px 16px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}> // boton volver
        volver al dashboard
      </button>

      <h1>detalle del paciente</h1>

      <div style={{ border: '1px solid #dee2e6', borderRadius: '8px', padding: '20px', marginTop: '20px' }}> // tarjeta de informacion
        <h2>información personal</h2>
        <p><strong>nombre:</strong> {paciente.nombre_descifrado}</p> // nombre descifrado
        <p><strong>edad:</strong> {paciente.edad}</p> // edad
        <p><strong>genero:</strong> {paciente.genero}</p> // genero
        <p><strong>tipo de sangre:</strong> {paciente.tipo_sangre}</p> // tipo de sangre

        <h2 style={{ marginTop: '20px' }}>información médica</h2>
        <p><strong>diagnóstico:</strong> {paciente.diagnostico_descifrado}</p> // diagnostico descifrado
        <p><strong>código cie-10:</strong> {paciente.codigo_cie10}</p> // codigo cie10
        <p><strong>medicación:</strong> {paciente.medicacion_descifrado}</p> // medicacion descifrado
        <p><strong>resultado de test:</strong> {paciente.resultado_test_descifrado}</p> // resultado descifrado

        <h2 style={{ marginTop: '20px' }}>información de admisión</h2>
        <p><strong>fecha de admisión:</strong> {new Date(paciente.fecha_admision).toLocaleDateString()}</p> // fecha formateada
        <p><strong>fecha de alta:</strong> {paciente.fecha_alta ? new Date(paciente.fecha_alta).toLocaleDateString() : 'pendiente'}</p> // fecha alta o pendiente
        <p><strong>tipo de admisión:</strong> {paciente.tipo_admision}</p> // tipo de admision
        <p><strong>número de habitación:</strong> {paciente.numero_habitacion}</p> // numero de habitacion

        <h2 style={{ marginTop: '20px' }}>información administrativa</h2>
        <p><strong>hospital:</strong> {paciente.hospital}</p> // hospital
        <p><strong>proveedor de seguro:</strong> {paciente.proveedor_seguro}</p> // proveedor de seguro
        <p><strong>monto facturado:</strong> ${paciente.monto_facturado_descifrado}</p> // monto descifrado
      </div>
    </div>
  );
};

export default PacienteDetalle; // exporta el componente
