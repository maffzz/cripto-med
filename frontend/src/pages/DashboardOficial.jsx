import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import axios from 'axios';
import { API_CONFIG } from '../config';
import {
  ShieldCheck,
  Database,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Users,
  Activity,
  TrendingUp,
  Lock,
  RefreshCw
} from 'lucide-react';
import Skeleton from '../components/Skeleton';

const DashboardOficial = () => {
  const { user } = useAuth();
  const { theme } = useTheme();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      // Simular métricas (en producción, esto vendría de la API)
      const simulatedMetrics = {
        totalBancosDatos: 3,
        solicitudesARCO: {
          pendientes: 5,
          completadas: 23,
          rechazadas: 2
        },
        incidentesUltimos30Dias: 0,
        ultimaVerificacionCadena: new Date().toISOString(),
        retencionCumplimiento: 98.5,
        pacientesAnonimizados: 0,
        pacientesActivos: 45,
        accesosUltimos7Dias: 127
      };
      setMetrics(simulatedMetrics);
    } catch (err) {
      console.error('Error al obtener métricas:', err);
      setError('Error al cargar métricas');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className={`rounded-lg p-4 ${theme === 'dark' ? 'bg-red-900/30 text-red-400' : 'bg-red-50 text-red-800'}`}>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className={`text-3xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'} flex items-center gap-3`}>
            <ShieldCheck className="w-8 h-8 text-primary-600" />
            Dashboard Oficial de Datos Personales
          </h1>
          <p className={`mt-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
            Bienvenido, {user?.nombre} | Rol: {user?.rol}
          </p>
        </div>
        <button
          onClick={fetchMetrics}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
            theme === 'dark'
              ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <RefreshCw className="w-4 h-4" />
          Actualizar
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Bancos de Datos */}
        <div className={`rounded-xl shadow-sm border p-6 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                Bancos de Datos Registrados
              </p>
              <p className={`text-3xl font-bold mt-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.totalBancosDatos}
              </p>
            </div>
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
              theme === 'dark' ? 'bg-primary-900/30' : 'bg-primary-100'
            }`}>
              <Database className={`w-6 h-6 ${theme === 'dark' ? 'text-primary-400' : 'text-primary-600'}`} />
            </div>
          </div>
        </div>

        {/* Solicitudes ARCO Pendientes */}
        <div className={`rounded-xl shadow-sm border p-6 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                Solicitudes ARCO Pendientes
              </p>
              <p className={`text-3xl font-bold mt-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.solicitudesARCO.pendientes}
              </p>
            </div>
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
              theme === 'dark' ? 'bg-yellow-900/30' : 'bg-yellow-100'
            }`}>
              <Clock className={`w-6 h-6 ${theme === 'dark' ? 'text-yellow-400' : 'text-yellow-600'}`} />
            </div>
          </div>
        </div>

        {/* Incidentes de Seguridad */}
        <div className={`rounded-xl shadow-sm border p-6 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                Incidentes (Últimos 30 días)
              </p>
              <p className={`text-3xl font-bold mt-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.incidentesUltimos30Dias}
              </p>
            </div>
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
              theme === 'dark' ? 'bg-green-900/30' : 'bg-green-100'
            }`}>
              <CheckCircle className={`w-6 h-6 ${theme === 'dark' ? 'text-green-400' : 'text-green-600'}`} />
            </div>
          </div>
        </div>

        {/* Cumplimiento de Retención */}
        <div className={`rounded-xl shadow-sm border p-6 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
                Cumplimiento de Retención
              </p>
              <p className={`text-3xl font-bold mt-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.retencionCumplimiento}%
              </p>
            </div>
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
              theme === 'dark' ? 'bg-purple-900/30' : 'bg-purple-100'
            }`}>
              <ShieldCheck className={`w-6 h-6 ${theme === 'dark' ? 'text-purple-400' : 'text-purple-600'}`} />
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Solicitudes ARCO */}
        <div className={`rounded-xl shadow-sm border p-6 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <h2 className={`text-xl font-semibold mb-4 flex items-center gap-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            <FileText className="w-5 h-5 text-primary-600" />
            Solicitudes ARCO (Derechos del Titular)
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>Pendientes</span>
              <span className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.solicitudesARCO.pendientes}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>Completadas</span>
              <span className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.solicitudesARCO.completadas}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>Rechazadas</span>
              <span className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.solicitudesARCO.rechazadas}
              </span>
            </div>
          </div>
        </div>

        {/* Métricas de Operación */}
        <div className={`rounded-xl shadow-sm border p-6 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <h2 className={`text-xl font-semibold mb-4 flex items-center gap-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            <Activity className="w-5 h-5 text-primary-600" />
            Métricas de Operación
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>Pacientes Activos</span>
              <span className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.pacientesActivos}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>Accesos (Últimos 7 días)</span>
              <span className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.accesosUltimos7Dias}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>Pacientes Anonimizados</span>
              <span className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {metrics.pacientesAnonimizados}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Legal Compliance Section */}
      <div className={`rounded-xl shadow-sm border p-6 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
        <h2 className={`text-xl font-semibold mb-4 flex items-center gap-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
          <Lock className="w-5 h-5 text-primary-600" />
          Cumplimiento Legal
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'} mb-2`}>
              Última Verificación de Cadena de Logs
            </p>
            <p className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
              {new Date(metrics.ultimaVerificacionCadena).toLocaleString('es-PE')}
            </p>
          </div>
          <div>
            <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'} mb-2`}>
              Estado de Cadena
            </p>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                Válida
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Reference */}
      <div className={`text-sm ${theme === 'dark' ? 'text-gray-500' : 'text-gray-500'}`}>
        <p>Conforme a Ley 29733, Reglamento D.S. 016-2024-JUS, Norma Técnica MINSA R.M. Nº 214-2018/MINSA</p>
      </div>
    </div>
  );
};

export default DashboardOficial;
