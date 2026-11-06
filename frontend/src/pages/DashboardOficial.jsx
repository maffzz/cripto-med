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
  Users,
  Activity,
  Lock,
  RefreshCw,
  LogIn,
  UserX,
  Siren,
  Download,
  FileSearch,
  HeartPulse,
} from 'lucide-react';
import Skeleton from '../components/Skeleton';

// Traducciones de rol
const ROL_ES = {
  admin: 'Admin',
  doctor: 'Doctor',
  administrativo: 'Administrativo',
  auditor: 'Auditor',
  paciente: 'Paciente',
};

// Tarjeta de métrica reutilizable
const MetricCard = ({ label, value, icon: Icon, color, sublabel, theme }) => {
  const colorMap = {
    blue:   { bg: theme === 'dark' ? 'bg-blue-900/30'   : 'bg-blue-50',   icon: theme === 'dark' ? 'text-blue-400'   : 'text-blue-600',   border: 'border-blue-200'   },
    green:  { bg: theme === 'dark' ? 'bg-green-900/30'  : 'bg-green-50',  icon: theme === 'dark' ? 'text-green-400'  : 'text-green-600',  border: 'border-green-200'  },
    yellow: { bg: theme === 'dark' ? 'bg-yellow-900/30' : 'bg-yellow-50', icon: theme === 'dark' ? 'text-yellow-400' : 'text-yellow-600', border: 'border-yellow-200' },
    red:    { bg: theme === 'dark' ? 'bg-red-900/30'    : 'bg-red-50',    icon: theme === 'dark' ? 'text-red-400'    : 'text-red-600',    border: 'border-red-200'    },
    purple: { bg: theme === 'dark' ? 'bg-purple-900/30' : 'bg-purple-50', icon: theme === 'dark' ? 'text-purple-400' : 'text-purple-600', border: 'border-purple-200' },
    teal:   { bg: theme === 'dark' ? 'bg-teal-900/30'   : 'bg-teal-50',   icon: theme === 'dark' ? 'text-teal-400'   : 'text-teal-600',   border: 'border-teal-200'   },
  };
  const c = colorMap[color] || colorMap.blue;

  return (
    <div className={`rounded-xl shadow-sm border p-5 flex items-center gap-4 ${c.border} ${c.bg}`}>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} shadow-sm`}>
        <Icon className={`w-6 h-6 ${c.icon}`} />
      </div>
      <div className="min-w-0">
        <p className={`text-xs font-medium uppercase tracking-wide truncate ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
          {label}
        </p>
        <p className={`text-2xl font-bold mt-0.5 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
          {value ?? '—'}
        </p>
        {sublabel && (
          <p className={`text-xs mt-0.5 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>
            {sublabel}
          </p>
        )}
      </div>
    </div>
  );
};

const DashboardOficial = () => {
  const { user } = useAuth();
  const { theme } = useTheme();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_CONFIG.URL}/audit-logs/metricas`);
      setMetrics(response.data);
    } catch (err) {
      console.error('Error al obtener métricas:', err);
      setError('No se pudieron cargar las métricas. Verifica la conexión.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-72" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className={`flex items-center gap-3 px-6 py-4 rounded-lg ${theme === 'dark' ? 'bg-red-900/30 text-red-400' : 'bg-red-50 text-red-700'}`}>
          <AlertTriangle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  const m = metrics;
  const generadoEn = m?.generado_en ? new Date(m.generado_en).toLocaleString('es-PE') : '—';
  const ultimoLogTs = m?.ultimo_log_ts ? new Date(m.ultimo_log_ts).toLocaleString('es-PE') : 'Sin registros';

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className={`text-3xl font-bold flex items-center gap-3 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            <ShieldCheck className="w-8 h-8 text-primary-600" />
            Dashboard Oficial de Datos Personales
          </h1>
          <p className={`mt-1 text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
            Bienvenido, <strong>{user?.nombre}</strong> · Datos en tiempo real · Actualizado: {generadoEn}
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

      {/* Sección 1: Pacientes y Usuarios */}
      <div>
        <h2 className={`text-xs font-semibold uppercase tracking-widest mb-3 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>
          Pacientes y Usuarios
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard label="Total Pacientes"   value={m.total_pacientes}    icon={HeartPulse} color="blue"   theme={theme} />
          <MetricCard label="Pacientes Activos" value={m.pacientes_activos}  icon={Activity}   color="green"  theme={theme} sublabel="En tratamiento" />
          <MetricCard label="Dados de Alta"     value={m.pacientes_dados_alta} icon={CheckCircle} color="teal" theme={theme} />
          <MetricCard label="Usuarios Activos"  value={`${m.usuarios_activos} / ${m.total_usuarios}`} icon={Users} color="purple" theme={theme} sublabel="activos / total" />
        </div>
      </div>

      {/* Sección 2: Actividad de Seguridad */}
      <div>
        <h2 className={`text-xs font-semibold uppercase tracking-widest mb-3 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>
          Actividad de Seguridad
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard label="Accesos (24 h)"         value={m.accesos_24h}           icon={FileSearch}  color="blue"   theme={theme} sublabel="lecturas de historiales" />
          <MetricCard label="Accesos (7 días)"        value={m.accesos_7d}            icon={Activity}    color="teal"   theme={theme} sublabel="lecturas de historiales" />
          <MetricCard label="Logins Fallidos (24 h)"  value={m.logins_fallidos_24h}   icon={LogIn}       color={m.logins_fallidos_24h > 0 ? 'yellow' : 'green'} theme={theme} />
          <MetricCard label="Bloqueos (24 h)"         value={m.bloqueos_24h}          icon={UserX}       color={m.bloqueos_24h > 0 ? 'red' : 'green'} theme={theme} />
        </div>
      </div>

      {/* Sección 3: Derechos y Emergencias */}
      <div>
        <h2 className={`text-xs font-semibold uppercase tracking-widest mb-3 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>
          Derechos del Titular y Emergencias
        </h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard label="Exportaciones (7 días)"     value={m.exportaciones_7d}      icon={Download}    color="blue"   theme={theme} sublabel="Portabilidad Ley 29733" />
          <MetricCard label="Accesos de Emergencia (7d)" value={m.accesos_emergencia_7d} icon={Siren}       color={m.accesos_emergencia_7d > 0 ? 'red' : 'green'} theme={theme} sublabel="break-glass" />
          <MetricCard label="Total Eventos en Logs"      value={m.total_logs}            icon={Database}    color="purple" theme={theme} sublabel="cadena SHA-256" />
          <MetricCard label="Último Evento Registrado"   value={null}                    icon={Clock}       color="teal"   theme={theme} sublabel={ultimoLogTs} />
        </div>
      </div>

      {/* Sección 4: Distribución por rol + Cumplimiento */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Distribución de usuarios por rol */}
        <div className={`rounded-xl shadow-sm border p-6 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <h2 className={`text-base font-semibold mb-4 flex items-center gap-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            <Users className="w-5 h-5 text-primary-600" />
            Usuarios por Rol
          </h2>
          <div className="space-y-3">
            {Object.entries(m.usuarios_por_rol).map(([rol, count]) => {
              const pct = m.total_usuarios > 0 ? Math.round((count / m.total_usuarios) * 100) : 0;
              return (
                <div key={rol}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}>
                      {ROL_ES[rol] || rol}
                    </span>
                    <span className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                      {count}
                    </span>
                  </div>
                  <div className={`w-full rounded-full h-2 ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'}`}>
                    <div
                      className="h-2 rounded-full bg-primary-500 transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Cumplimiento y trazabilidad */}
        <div className={`rounded-xl shadow-sm border p-6 ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <h2 className={`text-base font-semibold mb-4 flex items-center gap-2 ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
            <Lock className="w-5 h-5 text-primary-600" />
            Cumplimiento y Trazabilidad
          </h2>
          <div className="space-y-4">
            {[
              { label: 'Cifrado en reposo',      value: 'AES-256-GCM',        ok: true  },
              { label: 'Cifrado en tránsito',    value: 'TLS 1.3',            ok: true  },
              { label: 'Logs con cadena SHA-256', value: `${m.total_logs} eventos`, ok: true },
              { label: 'Hashing de contraseñas', value: 'bcrypt factor 12',   ok: true  },
              { label: 'Bloqueo por intentos',   value: '5 intentos → 15 min', ok: true },
              { label: 'Marco legal',            value: 'Ley 29733 / D.S. 016-2024-JUS', ok: true },
            ].map(({ label, value, ok }) => (
              <div key={label} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  {ok
                    ? <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                    : <AlertTriangle className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                  }
                  <span className={theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}>{label}</span>
                </div>
                <span className={`text-xs font-mono px-2 py-0.5 rounded ${theme === 'dark' ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'}`}>
                  {value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer legal */}
      <p className={`text-xs ${theme === 'dark' ? 'text-gray-600' : 'text-gray-400'}`}>
        Métricas calculadas en tiempo real desde la base de datos. Conforme a Ley N° 29733 y Reglamento D.S. N° 016-2024-JUS.
      </p>
    </div>
  );
};

export default DashboardOficial;
