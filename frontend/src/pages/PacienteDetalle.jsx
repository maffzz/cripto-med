import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { API_CONFIG } from '../config';
import { ArrowLeft, User, Activity, FileText, Calendar, CreditCard, Building2, Stethoscope, Syringe, TestTube, Edit, Trash2, Plus, AlertTriangle } from 'lucide-react';

const PacienteDetalle = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [paciente, setPaciente] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editedData, setEditedData] = useState({
    diagnostico: '',
    medicacion: ''
  });

  useEffect(() => {
    const fetchPaciente = async () => {
      try {
        const response = await axios.get(`${API_CONFIG.URL}/pacientes/${id}`);
        setPaciente(response.data);
        setEditedData({
          diagnostico: response.data.diagnostico_descifrado || '',
          medicacion: response.data.medicacion_descifrado || ''
        });
      } catch (err) {
        console.error('error al obtener paciente:', err);
        setError('error al cargar paciente');
      } finally {
        setLoading(false);
      }
    };
    fetchPaciente();
  }, [id]);

  const handleEdit = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_CONFIG.URL}/pacientes/${id}`,
        {
          diagnostico_descifrado: editedData.diagnostico,
          medicacion_descifrado: editedData.medicacion
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      alert('Paciente actualizado correctamente');
      setEditMode(false);
      // Recargar datos
      const response = await axios.get(`${API_CONFIG.URL}/pacientes/${id}`);
      setPaciente(response.data);
    } catch (err) {
      console.error('error al editar paciente:', err);
      alert('Error al editar paciente');
    }
  };

  const handleDelete = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_CONFIG.URL}/pacientes/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Paciente borrado correctamente');
      setShowDeleteModal(false);
      navigate('/dashboard');
    } catch (err) {
      console.error('error al borrar paciente:', err);
      alert('Error al borrar paciente');
    }
  };

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

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        {user?.rol === 'admin' && (
          <>
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Plus className="w-5 h-5" />
              <span>Crear Paciente</span>
            </button>
            <button
              onClick={() => setEditMode(true)}
              className="flex items-center gap-2 px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
            >
              <Edit className="w-5 h-5" />
              <span>Editar Historial</span>
            </button>
            <button
              onClick={() => setShowDeleteModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              <Trash2 className="w-5 h-5" />
              <span>Borrar Paciente</span>
            </button>
          </>
        )}
        {(user?.rol === 'doctor' || user?.rol === 'administrativo') && (
          <button
            onClick={() => setEditMode(true)}
            className="flex items-center gap-2 px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
          >
            <Edit className="w-5 h-5" />
            <span>Editar Historial</span>
          </button>
        )}
        {user?.rol === 'administrativo' && (
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span>Crear Paciente</span>
          </button>
        )}
      </div>

      {/* Edit Mode */}
      {editMode && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Editar Paciente</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Diagnóstico</label>
              <input
                type="text"
                value={editedData.diagnostico}
                onChange={(e) => setEditedData({...editedData, diagnostico: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Medicación</label>
              <input
                type="text"
                value={editedData.medicacion}
                onChange={(e) => setEditedData({...editedData, medicacion: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleEdit}
                className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                <span>Guardar Cambios</span>
              </button>
              <button
                onClick={() => setEditMode(false)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                <span>Cancelar</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-red-600" />
              <h3 className="text-xl font-semibold text-gray-900">Confirmar Borrado</h3>
            </div>
            <p className="text-gray-600 mb-6">
              ¿Estás seguro de que quieres borrar a {paciente.nombre_descifrado}? Esta acción no se puede deshacer.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                Borrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PacienteDetalle;
