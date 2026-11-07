import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Lock, Mail, AlertCircle, CheckCircle, Heart, LogIn } from 'lucide-react';

// Usuarios de demo — contraseñas leídas de variables de entorno Vite
// (se inyectan al build desde el .env vía docker-compose build args)
const DEMO_USERS = [
  { label: 'Admin',         email: 'admin@criptomed.com',      password: import.meta.env.VITE_DEMO_PASSWORD_ADMIN          || '', color: 'text-blue-600',   bg: 'hover:bg-blue-50',   rol: 'admin' },
  { label: 'Dra. Torres',   email: 'doctor@criptomed.com',     password: import.meta.env.VITE_DEMO_PASSWORD_DOCTOR         || '', color: 'text-green-600',  bg: 'hover:bg-green-50',  rol: 'doctor' },
  { label: 'Dr. Ramírez',   email: 'dr.ramirez@criptomed.com', password: import.meta.env.VITE_DEMO_PASSWORD_DOCTOR         || '', color: 'text-green-600',  bg: 'hover:bg-green-50',  rol: 'doctor' },
  { label: 'Dra. Quispe',   email: 'dra.quispe@criptomed.com', password: import.meta.env.VITE_DEMO_PASSWORD_DOCTOR         || '', color: 'text-green-600',  bg: 'hover:bg-green-50',  rol: 'doctor' },
  { label: 'Administrativo',email: 'admin@clinica.com',        password: import.meta.env.VITE_DEMO_PASSWORD_ADMINISTRATIVO || '', color: 'text-yellow-600', bg: 'hover:bg-yellow-50', rol: 'administrativo' },
  { label: 'Auditor',       email: 'auditor@criptomed.com',    password: import.meta.env.VITE_DEMO_PASSWORD_AUDITOR        || '', color: 'text-red-600',    bg: 'hover:bg-red-50',    rol: 'auditor' },
  { label: 'Paciente Demo', email: 'paciente@criptomed.com',   password: import.meta.env.VITE_DEMO_PASSWORD_PACIENTE       || '', color: 'text-purple-600', bg: 'hover:bg-purple-50', rol: 'paciente' },
];

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeUser, setActiveUser] = useState(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password);
    console.log('login result:', result);
    if (result.success) {
      console.log('navigating to /redirect');
      navigate('/redirect');
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const fillUser = (user) => {
    setEmail(user.email);
    setPassword(user.password);
    setActiveUser(user.email);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-medical-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo y Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-medical-500 rounded-2xl mb-4 shadow-lg">
            <Heart className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">CriptoMed</h1>
          <p className="text-gray-600">Sistema seguro de gestión de historiales médicos</p>
        </div>

        {/* Card de Login */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
            Iniciar Sesión
          </h2>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 outline-none"
                  placeholder="tu@email.com"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contraseña
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 outline-none"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-gradient-to-r from-primary-500 to-medical-500 text-white font-semibold rounded-lg hover:from-primary-600 hover:to-medical-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Cargando...
                </span>
              ) : (
                'Iniciar Sesión'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center">
            <div className="flex-1 border-t border-gray-200"></div>
            <span className="px-4 text-sm text-gray-500">Usuarios de prueba</span>
            <div className="flex-1 border-t border-gray-200"></div>
          </div>

          {/* Demo Users — click para autorellenar */}
          <div className="space-y-1">
            <p className="text-xs text-gray-400 mb-2 text-center">Haz clic en un usuario para autorellenar el formulario</p>
            {DEMO_USERS.map((u) => (
              <button
                key={u.email}
                type="button"
                onClick={() => fillUser(u)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg border transition-all duration-150 text-left
                  ${activeUser === u.email
                    ? 'border-primary-400 bg-primary-50 ring-1 ring-primary-300'
                    : 'border-gray-200 bg-gray-50 ' + u.bg
                  }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <CheckCircle className={`w-4 h-4 flex-shrink-0 ${u.color}`} />
                  <div className="min-w-0">
                    <span className={`text-xs font-semibold ${u.color} block`}>{u.label}</span>
                    <span className="text-xs text-gray-500 truncate block">{u.email}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                  <code className="text-xs bg-white border border-gray-200 rounded px-1.5 py-0.5 text-gray-700 font-mono">
                    {u.password}
                  </code>
                  <LogIn className="w-3.5 h-3.5 text-gray-400" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-gray-500">
          <p>Proyecto académico - DS3031 Ética y Seguridad de Datos</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
