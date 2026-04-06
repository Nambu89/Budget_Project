import { getToken } from './client';
import { ENDPOINTS } from '../config/api';
import type {
  CalcularPresupuestoRequest,
  PresupuestoResponse,
  GenerarPDFRequest,
} from '../types/api';

export async function calcularPresupuesto(
  data: CalcularPresupuestoRequest
): Promise<PresupuestoResponse> {
  const response = await fetch(ENDPOINTS.presupuesto.calcular, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const detail = errorBody.detail;
    const msg = typeof detail === 'string'
      ? detail
      : errorBody.error || `Error ${response.status}`;
    throw new Error(msg);
  }

  return response.json();
}

export async function descargarPDF(data: GenerarPDFRequest): Promise<Blob> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(ENDPOINTS.presupuesto.pdf, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const detail = errorBody.detail;
    const msg = typeof detail === 'string'
      ? detail
      : errorBody.error || `Error ${response.status}`;
    throw new Error(msg);
  }

  return response.blob();
}
