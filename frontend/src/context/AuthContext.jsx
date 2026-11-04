import { createContext, useContext, useState, useEffect } from 'react'; // hooks de react
import axios from 'axios'; // cliente http
import { API_CONFIG } from '../config'; // configuracion de API

const AuthContext = createContext(null); // crea el contexto de autenticacion

export const AuthProvider = ({ children }) => { // proveedor del contexto
  const [user, setUser] = useState(null); // estado del usuario actual
  const [loading, setLoading] = useState(true); // estado de carga
  const [token, setToken] = useState(localStorage.getItem('token')); // token jwt del localstorage

  // configura axios con el token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`; // añade header de autorizacion
    } else {
      delete axios.defaults.headers.common['Authorization']; // elimina header si no hay token
    }
  }, [token]);

  // verifica si el usuario esta autenticado al cargar
  useEffect(() => { // funcion asincrona para verificar auth
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('token'); // obtiene token del localstorage
      if (storedToken) {
        try {
          const response = await axios.get(`${API_CONFIG.URL}/auth/me`); // llama al endpoint /auth/me
          setUser(response.data); // guarda el usuario en el estado
          setToken(storedToken); // guarda el token en el estado
        } catch (error) {
          console.error('error al verificar autenticacion:', error); // log error
          localStorage.removeItem('token'); // elimina token invalido
          setToken(null); // limpia estado del token
        }
      }
      setLoading(false); // marca que ya no esta cargando
    };
    checkAuth(); // ejecuta verificacion
  }, []);

  const login = async (email, password) => { // funcion para login
    try {
      const formData = new FormData(); // crea formulario
      formData.append('username', email); // añade email
      formData.append('password', password); // añade password
      
      console.log('login attempt:', email, API_CONFIG.URL);
      const response = await axios.post(`${API_CONFIG.URL}/auth/login`, formData); // llama al endpoint de login
      const { access_token } = response.data; // obtiene el token
      
      console.log('token received');
      localStorage.setItem('token', access_token); // guarda token en localstorage
      setToken(access_token); // guarda token en estado
      
      // configura header manualmente para la siguiente peticion
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`; // añade header
      
      const userResponse = await axios.get(`${API_CONFIG.URL}/auth/me`); // obtiene datos del usuario
      console.log('user received:', userResponse.data);
      setUser(userResponse.data); // guarda usuario en estado
      
      return { success: true }; // retorna exito
    } catch (error) {
      console.error('error al hacer login:', error); // log error
      return { success: false, error: error.response?.data?.detail || 'error al hacer login' }; // retorna error
    }
  };

  const logout = () => { // funcion para logout
    localStorage.removeItem('token'); // elimina token del localstorage
    setToken(null); // limpia estado del token
    setUser(null); // limpia estado del usuario
    delete axios.defaults.headers.common['Authorization']; // elimina header de autorizacion
  };

  // Temporizador de inactividad de 15 minutos (NIST SP 800-63B / OWASP Session Management)
  const INACTIVITY_TIMEOUT_MS = 15 * 60 * 1000;

  useEffect(() => {
    if (!token) return;

    let timer = null;

    const resetTimer = () => {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        console.warn('Sesión expirada por inactividad de 15 minutos.');
        logout();
        window.location.href = '/';
      }, INACTIVITY_TIMEOUT_MS);
    };

    const events = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart'];
    events.forEach(evt => window.addEventListener(evt, resetTimer, { passive: true }));

    resetTimer();

    return () => {
      if (timer) clearTimeout(timer);
      events.forEach(evt => window.removeEventListener(evt, resetTimer));
    };
  }, [token]);

  return ( // retorna el proveedor del contexto
    <AuthContext.Provider value={{ user, loading, login, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext); // hook para usar el contexto
