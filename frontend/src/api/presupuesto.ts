import { apiFetch, getToken } from './client';
import { ENDPOINTS } from '../config/api';
import type {
  CalcularPresupuestoRequest,
  PresupuestoResponse,
  GenerarPDFRequest,
  GuardarPresupuestoRequest,
  GuardarPresupuestoResponse,
  UserBudgetsListResponse,
} from '../types/api';

export async function calcularPresupuesto(
  data: CalcularPresupuestoRequest
): Promise<PresupuestoResponse> {
  return apiFetch<PresupuestoResponse>(ENDPOINTS.presupuesto.calcular, {
    method: 'POST',
    body: JSON.stringify(data),
  });
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
    throw new Error(errorBody.detail || errorBody.error || `Error ${response.status}`);
  }

  return response.blob();
}

export async function guardarPresupuesto(
  data: GuardarPresupuestoRequest
): Promise<GuardarPresupuestoResponse> {
  return apiFetch<GuardarPresupuestoResponse>(ENDPOINTS.presupuesto.guardar, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getMisPresupuestos(
  userId: string
): Promise<UserBudgetsListResponse> {
  return apiFetch<UserBudgetsListResponse>(
    `${ENDPOINTS.presupuesto.misPresupuestos}?user_id=${encodeURIComponent(userId)}`
  );
}

export async function eliminarPresupuesto(
  budgetId: string,
  userId: string
): Promise<{ message: string; id: string }> {
  return apiFetch<{ message: string; id: string }>(
    `${ENDPOINTS.presupuesto.eliminar(budgetId)}?user_id=${encodeURIComponent(userId)}`,
    { method: 'DELETE' }
  );
}
