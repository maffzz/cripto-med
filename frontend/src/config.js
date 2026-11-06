// usa /api en produccion (nginx). vite inyecta VITE_API_URL solo si existe.
const fromEnv = import.meta.env.VITE_API_URL; // valor de build, puede faltar
const API_URL = import.meta.env.PROD ? '/api' : (fromEnv || '/api'); // docker y vite-dev van por /api

export const API_CONFIG = {
  URL: API_URL, // base de axios
  isProd: import.meta.env.PROD === true, // true en npm run build
};
