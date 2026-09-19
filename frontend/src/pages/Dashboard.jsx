import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Users, Activity, Clock, AlertCircle, Search, Filter, MoreVertical, Shield } from 'lucide-react';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [pacientes, setPacientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [filterBy, setFilterBy] = useState('all'); // all, active, discharged

  useEffect(() => {
    const fetchPacientes = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
        const response = await axios.get(`${apiUrl}/pacientes`);
        setPacientes(response.data);
      } catch (err) {
        console.error('error al obtener pacientes:', err);
        setError('error al cargar pacientes');
      } finally {
        setLoading(false);
      }
    };
    fetchPacientes();
  }, []);

  const filteredPacientes = pacientes.filter((paciente) => {
    const matchesSearch =
      paciente.nombre_descifrado?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      paciente.hospital?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter =
      filterBy === 'all' ||
      (filterBy === 'active' && !paciente.fecha_alta) ||
      (filterBy === 'discharged' && paciente.fecha_alta);
    
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-gray-600">
          <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <span>Cargando pacientes...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-red-600 bg-red-50 px-6 py-4 rounded-lg">
          <AlertCircle className="w-6 h-6" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Bienvenido, {user?.nombre}</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Clock className="w-4 h-4" />
          <span>Última actualización: {new Date().toLocaleString()}</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total de Pacientes</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{pacientes.length}</p>
            </div>
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pacientes Activos</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {pacientes.filter(p => !p.fecha_alta).length}
              </p>
            </div>
            <div className="w-12 h-12 bg-medical-100 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-medical-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tu Rol</p>
              <p className="text-3xl font-bold text-gray-900 mt-2 capitalize">{user?.rol}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por nombre o hospital..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={filterBy}
            onChange={(e) => setFilterBy(e.target.value)}
            className="px-4 py-3 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            <option value="all">Todos</option>
            <option value="active">Activos</option>
            <option value="discharged">Dados de Alta</option>
          </select>
          <button
            onClick={() => setShowAll(!showAll)}
            className="flex items-center gap-2 px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            <Filter className="w-5 h-5" />
            <span>{showAll ? 'Mostrar Menos' : 'Mostrar Todos'}</span>
          </button>
        </div>
      </div>

      {/* Patients Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPacientes.slice(0, showAll ? filteredPacientes.length : 50).map((paciente) => (
          <div
            key={paciente.id}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 text-lg">
                  {paciente.nombre_descifrado}
                </h3>
                <p className="text-sm text-gray-600 mt-1">{paciente.hospital}</p>
              </div>
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <MoreVertical className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-500">Edad:</span>
                <span className="font-medium text-gray-900">{paciente.edad}</span>
                <span className="text-gray-500">|</span>
                <span className="text-gray-500">Género:</span>
                <span className="font-medium text-gray-900">{paciente.genero}</span>
              </div>

              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-500">Tipo Sangre:</span>
                <span className="font-medium text-gray-900">{paciente.tipo_sangre}</span>
              </div>

              <div className="pt-3 border-t border-gray-100">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-gray-500">Diagnóstico:</span>
                  <span className="font-medium text-primary-600">
                    {paciente.diagnostico_descifrado}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Admisión: {new Date(paciente.fecha_admision).toLocaleDateString()}</span>
                <span className={`px-2 py-1 rounded-full ${
                  paciente.fecha_alta ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {paciente.fecha_alta ? 'Alta' : 'Activo'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Show More */}
      {filteredPacientes.length > 50 && (
        <div className="text-center">
          <button className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors font-medium">
            Mostrar más pacientes ({filteredPacientes.length - 50} restantes)
          </button>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
