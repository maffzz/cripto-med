// Configuración de URLs del API
// Detecta si estamos en GitHub Pages (producción) o localhost (desarrollo)
const isProd = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';

const API_URL = import.meta.env.VITE_API_URL || 
                 (isProd ? 'https://cripto-med.onrender.com' : 'http://127.0.0.1:8000');

export const API_CONFIG = {
  URL: API_URL,
  isProd: isProd
};
