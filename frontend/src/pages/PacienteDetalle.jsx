import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_CONFIG } from '../config';
import { ArrowLeft, User, Activity, FileText, Calendar, CreditCard, Building2, Stethoscope, Syringe, TestTube } from 'lucide-react';

const PacienteDetalle = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [paciente, setPaciente] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPaciente = async () => {
      try {
        const response = await axios.get(`${API_CONFIG.URL}/pacientes/${id}`);
        setPaciente(response.data);
      } catch (err) {
        console.error('error al obtener paciente:', err);
        setError('error al cargar paciente');
      } finally {
        setLoading(false);
      }
    };
    fetchPaciente();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-gray-600">
          <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <span>Cargando paciente...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-red-600 bg-red-50 px-6 py-4 rounded-lg">
          <span>{error}</span>
        </div>
      </div>
    );
  }

  if (!paciente) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Paciente no encontrado</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Volver al Dashboard</span>
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Detalle del Paciente</h1>
      </div>

      {/* Patient Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Información Personal */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <User className="w-5 h-5 text-primary-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Información Personal</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Nombre:</span>
              <span className="font-medium text-gray-900">{paciente.nombre_descifrado}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Edad:</span>
              <span className="font-medium text-gray-900">{paciente.edad}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Género:</span>
              <span className="font-medium text-gray-900">{paciente.genero}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Tipo Sangre:</span>
              <span className="font-medium text-gray-900">{paciente.tipo_sangre}</span>
            </div>
          </div>
        </div>

        {/* Información Médica */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-medical-100 rounded-lg flex items-center justify-center">
              <Stethoscope className="w-5 h-5 text-medical-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Información Médica</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Diagnóstico:</span>
              <span className="font-medium text-primary-600">{paciente.diagnostico_descifrado}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Código CIE-10:</span>
              <span className="font-medium text-gray-900">{paciente.codigo_cie10}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Medicación:</span>
              <span className="font-medium text-gray-900">{paciente.medicacion_descifrado}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Resultado Test:</span>
              <span className="font-medium text-gray-900">{paciente.resultado_test_descifrado}</span>
            </div>
          </div>
        </div>

        {/* Información de Admisión */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-purple-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Información de Admisión</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Fecha Admisión:</span>
              <span className="font-medium text-gray-900">
                {new Date(paciente.fecha_admision).toLocaleDateString()}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Fecha Alta:</span>
              <span className="font-medium text-gray-900">
                {paciente.fecha_alta ? new Date(paciente.fecha_alta).toLocaleDateString() : 'Pendiente'}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Tipo Admisión:</span>
              <span className="font-medium text-gray-900">{paciente.tipo_admision}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Habitación:</span>
              <span className="font-medium text-gray-900">{paciente.numero_habitacion}</span>
            </div>
          </div>
        </div>

        {/* Información Administrativa */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Building2 className="w-5 h-5 text-blue-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Información Administrativa</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Hospital:</span>
              <span className="font-medium text-gray-900">{paciente.hospital}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Seguro:</span>
              <span className="font-medium text-gray-900">{paciente.proveedor_seguro}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-gray-500 w-32">Monto:</span>
              <span className="font-medium text-green-600">
                ${paciente.monto_facturado_descifrado}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Status Banner */}
      <div className={`p-4 rounded-lg ${
        paciente.fecha_alta 
          ? 'bg-green-50 border border-green-200 text-green-800' 
          : 'bg-yellow-50 border border-yellow-200 text-yellow-800'
      }`}>
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5" />
          <span className="font-medium">
            Estado: {paciente.fecha_alta ? 'Alta dada' : 'Paciente activo'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default PacienteDetalle;
