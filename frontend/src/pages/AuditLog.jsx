import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { API_CONFIG } from '../config';
import {
  Shield, Search, Filter, ChevronLeft, ChevronRight,
  Clock, User as UserIcon, AlertTriangle, CheckCircle,
  XCircle, FileText, LogIn, LogOut, UserX, RefreshCw,
  Download, Siren, ArrowRightLeft, Eye, Pencil, Trash2,
  ShieldAlert,
} from 'lucide-react';

// ── Configuración de tipos de acción ──────────────────────────────────────────
const ACCIONES = {
  login: {
    label: 'Login',
    icon: LogIn,
    bg: 'bg-green-100',
    text: 'text-green-800',
    darkBg: 'dark:bg-green-900/40',
    darkText: 'dark:text-green-300',
  },
  login_fallido: {
    label: 'Login Fallido',
    icon: AlertTriangle,
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    darkBg: 'dark:bg-yellow-900/40',
    darkText: 'dark:text-yellow-300',
  },
  bloqueo: {
    label: 'Bloqueo',
    icon: UserX,
    bg: 'bg-red-100',
    text: 'text-red-800',
    darkBg: 'dark:bg-red-900/40',
    darkText: 'dark:text-red-300',
  },
  lectura: {
    label: 'Lectura',
    icon: Eye,
    bg: 'bg-blue-100',
    text: 'text-blue-800',
    darkBg: 'dark:bg-blue-900/40',
    darkText: 'dark:text-blue-300',
  },
  edicion: {
    label: 'Edición',
    icon: Pencil,
    bg: 'bg-amber-100',
    text: 'text-amber-800',
    darkBg: 'dark:bg-amber-900/40',
    darkText: 'dark:text-amber-300',
  },
  borrado: {
    label: 'Borrado',
    icon: Trash2,
    bg: 'bg-red-100',
    text: 'text-red-800',
    darkBg: 'dark:bg-red-900/40',
    darkText: 'dark:text-red-300',
  },
  transferencia: {
    label: 'Transferencia',
    icon: ArrowRightLeft,
    bg: 'bg-purple-100',
    text: 'text-purple-800',
    darkBg: 'dark:bg-purple-900/40',
    darkText: 'dark:text-purple-300',
  },
  exportacion: {
    label: 'Exportación',
    icon: Download,
    bg: 'bg-teal-100',
    text: 'text-teal-800',
    darkBg: 'dark:bg-teal-900/40',
    darkText: 'dark:text-teal-300',
  },
  acceso_emergencia: {
    label: '🚨 Emergencia',
    icon: Siren,
    bg: 'bg-red-600',
    text: 'text-white',
    darkBg: 'dark:bg-red-700',
    darkText: '',
  },
};

const getAccion = (key) => ACCIONES[key] || {
  label: key,
  icon: Clock,
  bg: 'bg-gray-100',
  text: 'text-gray-700',
  darkBg: '',
  darkText: '',
};

// Estadísticas de la página actual para las tarjetas
const STAT_KEYS = [
  { key: 'login',           label: 'Logins',           color: 'text-green-600',  bg: 'bg-green-100'  },
  { key: 'login_fallido',   label: 'Fallidos',          color: 'text-yellow-600', bg: 'bg-yellow-100' },
  { key: 'lectura',         label: 'Lecturas',          color: 'text-blue-600',   bg: 'bg-blue-100'   },
  { key: 'transferencia',   label: 'Transferencias',    color: 'text-purple-600', bg: 'bg-purple-100' },
  { key: 'exportacion',     label: 'Exportaciones',     color: 'text-teal-600',   bg: 'bg-teal-100'   },
  { key: 'acceso_emergencia', label: 'Emergencias',     color: 'text-red-600',    bg: 'bg-red-100'    },
];

// Opciones de filtro por acción
const FILTRO_ACCIONES = [
  { value: '',                  label: 'Todas las acciones' },
  { value: 'login',             label: 'Login' },
  { value: 'login_fallido',     label: 'Login Fallido' },
  { value: 'bloqueo',           label: 'Bloqueo' },
  { value: 'lectura',           label: 'Lectura' },
  { value: 'edicion',           label: 'Edición' },
  { value: 'borrado',           label: 'Borrado' },
  { value: 'transferencia',     label: 'Transferencia' },
  { value: 'exportacion',       label: 'Exportación' },
  { value: 'acceso_emergencia', label: 'Emergencia (break-glass)' },
];

const AuditLog = () => {
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAccion, setFilterAccion] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  // Mapa uuid → nombre de usuario (cacheado)
  const [usuarioMap, setUsuarioMap] = useState({});

  const PAGE_SIZE = 20;

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams({ page, page_size: PAGE_SIZE });
      if (filterAccion) params.append('accion', filterAccion);
      const response = await axios.get(`${API_CONFIG.URL}/audit-logs?${params}`);
      setLogs(response.data.items);
      setTotal(response.data.total);
    } catch (err) {
      console.error('error al obtener logs:', err);
      setError('Error al cargar logs de auditoría');
    } finally {
      setLoading(false);
    }
  }, [page, filterAccion]);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  // Cargar nombres de usuarios para los IDs que aún no conocemos
  useEffect(() => {
    if (!logs.length) return;
    const unknownIds = logs
      .map(l => l.usuario_id)
      .filter(id => id && !usuarioMap[id]);
    if (!unknownIds.length) return;

    axios.get(`${API_CONFIG.URL}/usuarios`)
      .then(res => {
        const map = {};
        res.data.forEach(u => { map[u.id] = u.nombre; });
        setUsuarioMap(prev => ({ ...prev, ...map }));
      })
      .catch(() => {}); // si no es admin, silenciar el error
  }, [logs]);

  // Resumen de acciones en la página actual
  const stats = STAT_KEYS.map(s => ({
    ...s,
    count: logs.filter(l => l.accion === s.key).length,
  }));

  // Filtro de búsqueda local (sobre la página cargada)
  const filteredLogs = logs.filter(log =>
    !searchTerm ||
    log.accion?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.recurso?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (log.ip_origen || '').includes(searchTerm) ||
    (usuarioMap[log.usuario_id] || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-gray-600">
          <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <span>Cargando logs de auditoría...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-red-600 bg-red-50 px-6 py-4 rounded-lg">
          <AlertTriangle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Logs de Auditoría</h1>
          <p className="text-gray-500 mt-1 text-sm">
            Cadena SHA-256 inmutable · {total.toLocaleString()} eventos totales
          </p>
        </div>
        <button
          onClick={fetchLogs}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
        >
          <RefreshCw className="w-4 h-4" />
          Actualizar
        </button>
      </div>

      {/* Stats de la página actual */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
        {stats.map(s => {
          const Icon = getAccion(s.key).icon;
          return (
            <button
              key={s.key}
              onClick={() => { setFilterAccion(filterAccion === s.key ? '' : s.key); setPage(1); }}
              className={`rounded-xl border p-3 text-left transition-all ${
                filterAccion === s.key
                  ? 'border-primary-400 ring-2 ring-primary-300 bg-primary-50'
                  : 'bg-white border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-2 ${s.bg}`}>
                <Icon className={`w-4 h-4 ${s.color}`} />
              </div>
              <p className="text-lg font-bold text-gray-900">{s.count}</p>
              <p className="text-xs text-gray-500 leading-tight">{s.label}</p>
            </button>
          );
        })}
      </div>

      {/* Barra de búsqueda y filtros */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por usuario, recurso, IP o acción..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none text-sm"
          />
        </div>
        <select
          value={filterAccion}
          onChange={e => { setFilterAccion(e.target.value); setPage(1); }}
          className="px-3 py-2.5 border border-gray-300 rounded-lg bg-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
        >
          {FILTRO_ACCIONES.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* Tabla */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide w-36">Acción</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Usuario</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Recurso</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide w-40">Timestamp</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide w-32">IP Origen</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Detalle</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredLogs.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                    No hay eventos que coincidan con el filtro.
                  </td>
                </tr>
              )}
              {filteredLogs.map(log => {
                const accion = getAccion(log.accion);
                const Icon = accion.icon;
                const nombreUsuario = usuarioMap[log.usuario_id] || null;
                const esEmergencia = log.accion === 'acceso_emergencia';

                return (
                  <tr
                    key={log.id}
                    className={`transition-colors ${
                      esEmergencia
                        ? 'bg-red-50 hover:bg-red-100'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    {/* Acción */}
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${accion.bg} ${accion.text}`}>
                        <Icon className="w-3.5 h-3.5 flex-shrink-0" />
                        {accion.label}
                      </span>
                    </td>

                    {/* Usuario */}
                    <td className="px-4 py-3">
                      {log.usuario_id ? (
                        <div className="flex items-center gap-1.5">
                          <UserIcon className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                          <span className="font-medium text-gray-900 truncate max-w-[140px]" title={log.usuario_id}>
                            {nombreUsuario || (
                              <span className="font-mono text-gray-400 text-xs">{log.usuario_id.slice(0, 8)}…</span>
                            )}
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400 italic text-xs">Sin autenticar</span>
                      )}
                    </td>

                    {/* Recurso */}
                    <td className="px-4 py-3">
                      <span className="text-gray-700 font-mono text-xs truncate block max-w-[180px]" title={log.recurso}>
                        {log.recurso}
                      </span>
                    </td>

                    {/* Timestamp */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center gap-1 text-gray-600">
                        <Clock className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                        <span className="text-xs">
                          {new Date(log.timestamp).toLocaleString('es-PE')}
                        </span>
                      </div>
                    </td>

                    {/* IP */}
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs text-gray-500">{log.ip_origen || '—'}</span>
                    </td>

                    {/* Detalle */}
                    <td className="px-4 py-3">
                      <span className="text-xs text-gray-500 truncate block max-w-[200px]" title={log.detalle || ''}>
                        {log.detalle || '—'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Paginación */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed text-sm"
        >
          <ChevronLeft className="w-4 h-4" />
          Anterior
        </button>
        <span className="text-sm text-gray-500">
          Página <strong>{page}</strong> de <strong>{totalPages}</strong>
          &nbsp;·&nbsp;{total.toLocaleString()} eventos
        </span>
        <button
          onClick={() => setPage(p => Math.min(totalPages, p + 1))}
          disabled={page >= totalPages}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed text-sm"
        >
          Siguiente
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default AuditLog;
