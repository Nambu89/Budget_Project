import { apiFetch } from './client';
import { ENDPOINTS } from '../config/api';
import type { PaquetesResponse, CategoriasResponse } from '../types/api';

export async function getPaquetes(pais = 'ES'): Promise<PaquetesResponse> {
  return apiFetch<PaquetesResponse>(`${ENDPOINTS.catalogos.paquetes}?pais=${pais}`);
}

export async function getCategorias(pais = 'ES'): Promise<CategoriasResponse> {
  return apiFetch<CategoriasResponse>(`${ENDPOINTS.catalogos.categorias}?pais=${pais}`);
}
