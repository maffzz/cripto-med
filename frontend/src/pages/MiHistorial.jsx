import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { API_CONFIG } from '../config';
import { User, Activity, FileText, Calendar, CreditCard, Building2, Stethoscope, Syringe, TestTube, RefreshCw, ArrowRight } from 'lucide-react';

const MiHistorial = () => {
  const { user } = useAuth();
  const [paciente, setPaciente] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [doctores, setDoctores] = useState([]);
  const [nuevoDoctorId, setNuevoDoctorId] = useState('');
  const [transfiriendo, setTransfiriendo] = useState(false);
  const [mensajeExito, setMensajeExito] = useState('');

  useEffect(() => {
    fetchMiHistorial();
    fetchDoctores();
  }, []);

  const fetchMiHistorial = async () => {
    try {
      const response = await axios.get(`${API_CONFIG.URL}/pacientes/me`);
      setPaciente(response.data);
    } catch (err) {
      console.error('Error al obtener historial:', err);
      setError('Error al cargar historial');
    } finally {
      setLoading(false);
    }
  };

  const fetchDoctores = async () => {
    try {
      const response = await axios.get(`${API_CONFIG.URL}/pacientes/doctores`);
      setDoctores(response.data);
    } catch (err) {
      console.error('Error al obtener doctores:', err);
    }
  };

  const transferirDoctor = async () => {
    if (!nuevoDoctorId) {
      setError('Selecciona un doctor');
      return;
    }

    setTransfiriendo(true);
    setError(null);
    setMensajeExito('');

    try {
      await axios.patch(`${API_CONFIG.URL}/pacientes/${paciente.id}/transferir-doctor`, {
        nuevo_doctor_id: nuevoDoctorId
      });

      setMensajeExito('Historial transferido correctamente al nuevo doctor');
      setNuevoDoctorId('');
      // Recargar historial para ver el nuevo doctor
      await fetchMiHistorial();
    } catch (err) {
      console.error('Error al transferir doctor:', err);
      setError('Error al transferir doctor');
    } finally {
      setTransfiriendo(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="animate-spin text-4xl text-blue-600" />
      </div>
    );
  }

  if (error && !paciente) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  const doctorActual = doctores.find(d => d.id === paciente?.doctor_id);

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Mi Historial Médico</h1>
        <p className="text-gray-600 mt-2">Bienvenido, {user?.nombre}</p>
      </div>

      {mensajeExito && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <p className="text-green-800">{mensajeExito}</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {paciente && (
        <div className="space-y-6">
          {/* Información del doctor actual */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Stethoscope className="w-5 h-5" />
              Doctor Actual
            </h2>
            {doctorActual ? (
              <div className="text-gray-700">
                <p className="font-medium text-lg">{doctorActual.nombre}</p>
                <p className="text-sm text-gray-500">{doctorActual.email}</p>
              </div>
            ) : (
              <p className="text-gray-500">No tienes doctor asignado</p>
            )}
          </div>

          {/* Transferir a otro doctor */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <RefreshCw className="w-5 h-5" />
              Transferir mi historial a otro doctor
            </h2>
            <p className="text-gray-600 mb-4">
              Puedes transferir tu historial médico a otro doctor si lo deseas. Esta acción quedará registrada en el log de auditoría.
            </p>
            <div className="flex gap-4">
              <select
                value={nuevoDoctorId}
                onChange={(e) => setNuevoDoctorId(e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Selecciona un doctor...</option>
                {doctores.filter(d => d.id !== paciente.doctor_id).map(doctor => (
                  <option key={doctor.id} value={doctor.id}>
                    {doctor.nombre} ({doctor.email})
                  </option>
                ))}
              </select>
              <button
                onClick={transferirDoctor}
                disabled={transfiriendo || !nuevoDoctorId}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {transfiriendo ? (
                  <>
                    <RefreshCw className="animate-spin w-4 h-4" />
                    Transfiriendo...
                  </>
                ) : (
                  <>
                    Transferir
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Información personal */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <User className="w-5 h-5" />
              Información Personal
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Nombre</p>
                <p className="font-medium">{paciente.nombre_descifrado}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Edad</p>
                <p className="font-medium">{paciente.edad} años</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Género</p>
                <p className="font-medium">{paciente.genero}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Tipo de Sangre</p>
                <p className="font-medium">{paciente.tipo_sangre}</p>
              </div>
            </div>
          </div>

          {/* Información médica */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Información Médica
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Diagnóstico</p>
                <p className="font-medium">{paciente.diagnostico_descifrado}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Medicación</p>
                <p className="font-medium">{paciente.medicacion_descifrado}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Resultado de Test</p>
                <p className="font-medium">{paciente.resultado_test_descifrado}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Fecha de Admisión</p>
                <p className="font-medium">{new Date(paciente.fecha_admision).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          {/* Información administrativa */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Información Administrativa
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Hospital</p>
                <p className="font-medium">{paciente.hospital}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Número de Habitación</p>
                <p className="font-medium">{paciente.numero_habitacion}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Tipo de Admisión</p>
                <p className="font-medium">{paciente.tipo_admision}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Proveedor de Seguro</p>
                <p className="font-medium">{paciente.proveedor_seguro}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Monto Facturado</p>
                <p className="font-medium">${paciente.monto_facturado_descifrado}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Estado</p>
                <p className="font-medium">
                  {paciente.fecha_alta ? (
                    <span className="text-red-600">Dado de Alta</span>
                  ) : (
                    <span className="text-green-600">Activo</span>
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MiHistorial;
