// Configuración de URLs del API
// Usa ruta relativa /api para Docker (servido por Nginx edge)
const API_URL = import.meta.env.VITE_API_URL || '/api';

export const API_CONFIG = {
  URL: API_URL,
  isProd: import.meta.env.PROD === 'true'
};
