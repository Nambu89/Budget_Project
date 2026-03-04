export const API_BASE = '/api/v1';

export const ENDPOINTS = {
  catalogos: {
    paquetes: `${API_BASE}/catalogos/paquetes`,
    categorias: `${API_BASE}/catalogos/categorias`,
  },
  presupuesto: {
    calcular: `${API_BASE}/presupuesto/calcular`,
    pdf: `${API_BASE}/presupuesto/pdf`,
    guardar: `${API_BASE}/presupuesto/guardar`,
    misPresupuestos: `${API_BASE}/presupuesto/mis-presupuestos`,
    eliminar: (id: string) => `${API_BASE}/presupuesto/${id}`,
  },
  auth: {
    register: `${API_BASE}/auth/register`,
    login: `${API_BASE}/auth/login`,
    me: `${API_BASE}/auth/me`,
    requestPasswordReset: `${API_BASE}/auth/request-password-reset`,
    verifyResetToken: (token: string) => `${API_BASE}/auth/verify-reset-token/${token}`,
    resetPassword: `${API_BASE}/auth/reset-password`,
  },
  email: {
    enviar: `${API_BASE}/email/enviar`,
  },
} as const;
