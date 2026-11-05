import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { API_CONFIG } from '../config';
import toast from 'react-hot-toast';
import Skeleton from '../components/Skeleton';
import {
  User,
  Activity,
  FileText,
  Calendar,
  CreditCard,
  Building2,
  Stethoscope,
  Syringe,
  TestTube,
  RefreshCw,
  ArrowRight,
  Download,
  ShieldCheck,
  History,
  Lock,
  AlertCircle,
  CheckCircle2,
  FileCheck
} from 'lucide-react';

const MiHistorial = () => {
  const { user } = useAuth();
  const [paciente, setPaciente] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [doctores, setDoctores] = useState([]);
  const [nuevoDoctorId, setNuevoDoctorId] = useState('');
  const [transfiriendo, setTransfiriendo] = useState(false);
  
  // Accesos / Trazabilidad
  const [accesos, setAccesos] = useState([]);
  const [loadingAccesos, setLoadingAccesos] = useState(false);
  const [exportando, setExportando] = useState(false);

  // Modal de confirmación de transferencia
  const [mostrarModalConfirmacion, setMostrarModalConfirmacion] = useState(false);

  useEffect(() => {
    fetchMiHistorial();
    fetchDoctores();
    fetchAccesos();
  }, []);

  const fetchMiHistorial = async () => {
    try {
      const response = await axios.get(`${API_CONFIG.URL}/pacientes/me`);
      setPaciente(response.data);
    } catch (err) {
      console.error('Error al obtener historial:', err);
      setError('Error al cargar historial clínico');
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

  const fetchAccesos = async () => {
    setLoadingAccesos(true);
    try {
      const response = await axios.get(`${API_CONFIG.URL}/pacientes/me/accesos`);
      setAccesos(response.data.items || []);
    } catch (err) {
      console.error('Error al obtener accesos:', err);
    } finally {
      setLoadingAccesos(false);
    }
  };

  const abrirModalTransferencia = () => {
    if (!nuevoDoctorId) {
      setError('Por favor selecciona un doctor destino para transferir tu historial.');
      return;
    }
    setError(null);
    setMostrarModalConfirmacion(true);
  };

  const confirmarTransferencia = async () => {
    setTransfiriendo(true);
    setError(null);
    setMostrarModalConfirmacion(false);

    try {
      await axios.patch(`${API_CONFIG.URL}/pacientes/${paciente.id}/transferir-doctor`, {
        nuevo_doctor_id: nuevoDoctorId
      });

      const doctorDestino = doctores.find(d => d.id === nuevoDoctorId);
      toast.success(`Historial transferido exitosamente a ${doctorDestino ? doctorDestino.nombre : 'nuevo doctor'}.`);
      setNuevoDoctorId('');
      // Recargar historial y accesos para reflejar el evento en la auditoría
      await fetchMiHistorial();
      await fetchAccesos();
    } catch (err) {
      console.error('Error al transferir doctor:', err);
      toast.error('Error al procesar la transferencia del historial.');
    } finally {
      setTransfiriendo(false);
    }
  };

  const descargarMisDatos = async () => {
    setExportando(true);
    setError(null);
    try {
      const response = await axios.get(`${API_CONFIG.URL}/pacientes/me/export`);
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(response.data, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', `criptomed_historial_${paciente?.nombre_descifrado || 'paciente'}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();

      toast.success('Copia de datos personales y clínicos exportada exitosamente en formato JSON (Derecho de Portabilidad - Ley 29733 / GDPR).');
      // Recargar accesos para mostrar el registro de exportación en la tabla de auditoría
      await fetchAccesos();
    } catch (err) {
      console.error('Error al exportar datos:', err);
      toast.error('Error al generar la exportación de sus datos personales.');
    } finally {
      setExportando(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <Skeleton className="h-12 w-64" />
        <Skeleton className="h-16 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
        <Skeleton className="h-64" />
        <Skeleton className="h-64" />
        <Skeleton className="h-64" />
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
  const doctorSeleccionado = doctores.find(d => d.id === nuevoDoctorId);

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Encabezado y Acción de Descarga de Datos */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <User className="w-8 h-8 text-blue-600" />
            Mi Historial Médico y Privacidad
          </h1>
          <p className="text-gray-600 mt-1">
            Titular: <span className="font-semibold text-gray-900">{user?.nombre}</span> ({user?.email})
          </p>
        </div>
        <div>
          <button
            onClick={descargarMisDatos}
            disabled={exportando}
            className="w-full md:w-auto px-5 py-2.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium shadow-sm flex items-center justify-center gap-2 transition-colors disabled:bg-emerald-400"
          >
            {exportando ? (
              <>
                <RefreshCw className="animate-spin w-4 h-4" />
                Generando exportación...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Descargar mis datos (JSON)
              </>
            )}
          </button>
        </div>
      </div>



      {paciente && (
        <div className="space-y-6">
          {/* Banner de Consentimiento Informado (Ley 29733 / D.S. 016-2024-JUS) */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-sm p-6 border border-blue-200">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-blue-600 text-white rounded-full">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h2 className="text-lg font-semibold text-blue-900">
                    Consentimiento Informado Registrado
                  </h2>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300">
                    Versión {paciente.consentimiento_version || 'v1.0'}
                  </span>
                </div>
                <p className="text-sm text-blue-800 mt-1">
                  Autorización expresa y previa para el tratamiento confidencial de datos de salud y trazabilidad inmutable bajo la <strong>Ley N° 29733</strong> de Protección de Datos Personales del Perú.
                </p>
                <div className="mt-2 text-xs text-blue-700 flex items-center gap-2">
                  <Calendar className="w-3.5 h-3.5" />
                  Fecha de suscripción: {paciente.consentimiento_fecha ? new Date(paciente.consentimiento_fecha).toLocaleString('es-PE') : 'Registrado al alta inicial'}
                </div>
              </div>
            </div>
          </div>

          {/* Grid: Doctor Asignado y Transferencia */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Información del doctor actual */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Stethoscope className="w-5 h-5 text-blue-600" />
                Doctor Asignado Actual
              </h2>
              {doctorActual ? (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <p className="font-semibold text-lg text-gray-900">{doctorActual.nombre}</p>
                  <p className="text-sm text-gray-600">{doctorActual.email}</p>
                  <span className="inline-block mt-2 text-xs text-emerald-700 bg-emerald-100 font-medium px-2 py-0.5 rounded">
                    Acceso autorizado a su expediente clínico
                  </span>
                </div>
              ) : (
                <p className="text-gray-500 italic">Actualmente no tiene un médico asignado.</p>
              )}
            </div>

            {/* Transferir a otro doctor con diálogo explícito */}
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
              <h2 className="text-xl font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <RefreshCw className="w-5 h-5 text-purple-600" />
                Transferir Mi Historial
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Como titular de sus datos, usted puede reasignar libremente su médico tratante. La transferencia revoca el acceso del doctor anterior de inmediato.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <select
                  value={nuevoDoctorId}
                  onChange={(e) => setNuevoDoctorId(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 text-sm"
                >
                  <option value="">Selecciona nuevo doctor tratante...</option>
                  {doctores
                    .filter(d => d.id !== paciente.doctor_id)
                    .map(doc => (
                      <option key={doc.id} value={doc.id}>
                        {doc.nombre} ({doc.email})
                      </option>
                    ))}
                </select>
                <button
                  onClick={abrirModalTransferencia}
                  disabled={transfiriendo || !nuevoDoctorId}
                  className="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 whitespace-nowrap shadow-sm"
                >
                  <ArrowRight className="w-4 h-4" />
                  Transferir
                </button>
              </div>
            </div>
          </div>

          {/* Sección de Trazabilidad: Quién accedió a mi historial (NIST SP 800-92) */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-teal-500">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-teal-600" />
                <h2 className="text-xl font-semibold text-gray-900">Quién accedió a mi historial</h2>
              </div>
              <button
                onClick={fetchAccesos}
                className="text-sm text-teal-600 hover:text-teal-800 font-medium flex items-center gap-1"
                title="Actualizar registro de accesos"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingAccesos ? 'animate-spin' : ''}`} />
                Actualizar
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Registro inmutable de todas las consultas, modificaciones y transferencias realizadas sobre su expediente médico (NIST SP 800-92).
            </p>

            {loadingAccesos ? (
              <div className="py-6 text-center text-gray-500">Cargando registros de auditoría...</div>
            ) : accesos.length === 0 ? (
              <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-500 text-center">
                Aún no hay accesos registrados a este expediente.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2.5 text-left font-medium text-gray-500">Fecha y Hora</th>
                      <th className="px-4 py-2.5 text-left font-medium text-gray-500">Acción</th>
                      <th className="px-4 py-2.5 text-left font-medium text-gray-500">Usuario</th>
                      <th className="px-4 py-2.5 text-left font-medium text-gray-500">Rol</th>
                      <th className="px-4 py-2.5 text-left font-medium text-gray-500">Detalle</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {accesos.map((log) => (
                      <tr key={log.id} className="hover:bg-gray-50">
                        <td className="px-4 py-2 text-gray-700 whitespace-nowrap">
                          {new Date(log.timestamp).toLocaleString('es-PE')}
                        </td>
                        <td className="px-4 py-2 whitespace-nowrap">
                          <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${
                            log.accion === 'acceso_emergencia' ? 'bg-red-600 text-white font-bold' :
                            log.accion === 'transferencia' ? 'bg-purple-100 text-purple-800' :
                            log.accion === 'exportacion' ? 'bg-emerald-100 text-emerald-800' :
                            log.accion === 'lectura' ? 'bg-blue-100 text-blue-800' :
                            log.accion === 'edicion' ? 'bg-amber-100 text-amber-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {log.accion === 'acceso_emergencia' ? '🚨 Acceso de Emergencia' : log.accion}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-gray-900 font-medium whitespace-nowrap">
                          {log.profesional_nombre}
                        </td>
                        <td className="px-4 py-2 text-gray-600 uppercase text-xs font-semibold whitespace-nowrap">
                          {log.profesional_rol}
                        </td>
                        <td className="px-4 py-2 text-gray-500 text-xs font-mono truncate max-w-xs">
                          {log.detalle || 'Consulta autorizada'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Información personal */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-green-600" />
              Datos Personales
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Nombre Completo</p>
                <p className="font-medium text-gray-900">{paciente.nombre_descifrado}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Edad</p>
                <p className="font-medium text-gray-900">{paciente.edad} años</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Género</p>
                <p className="font-medium text-gray-900">{paciente.genero}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Tipo de Sangre</p>
                <p className="font-medium text-gray-900">{paciente.tipo_sangre}</p>
              </div>
            </div>
          </div>

          {/* Información médica (cifrada con AES-256-GCM en base de datos) */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-red-600" />
              Información Clínica (Protegida con AES-256-GCM)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Diagnóstico Principal</p>
                <p className="font-medium text-gray-900">{paciente.diagnostico_descifrado || 'No registrado'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Medicación Actual</p>
                <p className="font-medium text-gray-900">{paciente.medicacion_descifrado || 'No registrado'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Resultado de Pruebas Clínicas</p>
                <p className="font-medium text-gray-900">{paciente.resultado_test_descifrado || 'No registrado'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Fecha de Admisión</p>
                <p className="font-medium text-gray-900">{new Date(paciente.fecha_admision).toLocaleDateString('es-PE')}</p>
              </div>
            </div>
          </div>

          {/* Información administrativa */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-yellow-600" />
              Datos Administrativos y Facturación
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Hospital / Clínica</p>
                <p className="font-medium text-gray-900">{paciente.hospital}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Número de Habitación</p>
                <p className="font-medium text-gray-900">{paciente.numero_habitacion}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Tipo de Admisión</p>
                <p className="font-medium text-gray-900">{paciente.tipo_admision}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Proveedor de Seguro</p>
                <p className="font-medium text-gray-900">{paciente.proveedor_seguro}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Monto Facturado</p>
                <p className="font-medium text-gray-900">S/. {paciente.monto_facturado_descifrado}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Estado Clínico</p>
                <p className="font-medium">
                  {paciente.fecha_alta ? (
                    <span className="text-gray-700 bg-gray-100 px-2 py-0.5 rounded text-xs">Dado de Alta</span>
                  ) : (
                    <span className="text-green-700 bg-green-100 px-2 py-0.5 rounded text-xs font-semibold">Tratamiento Activo</span>
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Confirmación Explícita de Transferencia */}
      {mostrarModalConfirmacion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 border border-gray-200">
            <div className="flex items-center gap-3 text-purple-600 mb-4">
              <AlertCircle className="w-6 h-6 flex-shrink-0" />
              <h3 className="text-lg font-bold text-gray-900">
                Confirmar Transferencia de Historial Médico
              </h3>
            </div>
            <div className="text-sm text-gray-600 space-y-3 mb-6">
              <p>
                Está a punto de transferir la custodia y acceso a su expediente clínico:
              </p>
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200 space-y-2">
                <p>
                  <strong>Doctor actual:</strong> {doctorActual ? doctorActual.nombre : 'Sin doctor asignado'}
                </p>
                <p className="text-purple-900 font-semibold">
                  ➔ <strong>Nuevo doctor tratante:</strong> {doctorSeleccionado ? doctorSeleccionado.nombre : 'Doctor seleccionado'}
                </p>
              </div>
              <p className="text-xs text-gray-500">
                Esta acción revocará inmediatamente el acceso del doctor actual, otorgará permisos al nuevo profesional y generará un registro verificable en la cadena de auditoría SHA-256.
              </p>
            </div>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setMostrarModalConfirmacion(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm font-medium"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={confirmarTransferencia}
                disabled={transfiriendo}
                className="px-5 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium shadow-sm flex items-center gap-2"
              >
                {transfiriendo ? (
                  <>
                    <RefreshCw className="animate-spin w-4 h-4" />
                    Transfiriendo...
                  </>
                ) : (
                  'Confirmar Transferencia'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MiHistorial;
