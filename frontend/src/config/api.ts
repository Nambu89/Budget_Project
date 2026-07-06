export const API_BASE = '/api/v1';

// Endpoints consumidos por el wizard. El backend expone además rutas de
// auth (JWT) y presupuestos guardados (/presupuesto/guardar, /mis-presupuestos)
// que la UI actual no usa — ver src/infrastructure/api/routes/ en el backend.
export const ENDPOINTS = {
  catalogos: {
    paquetes: `${API_BASE}/catalogos/paquetes`,
    categorias: `${API_BASE}/catalogos/categorias`,
  },
  presupuesto: {
    calcular: `${API_BASE}/presupuesto/calcular`,
    pdf: `${API_BASE}/presupuesto/pdf`,
  },
  email: {
    enviar: `${API_BASE}/email/enviar`,
  },
} as const;
