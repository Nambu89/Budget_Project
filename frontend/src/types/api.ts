/* Request / Response types — mirror de FastAPI schemas */

// ---- Requests ----

export interface ProyectoRequest {
  tipo_inmueble: string;
  metros_cuadrados: number;
  estado_actual: string;
  es_vivienda_habitual: boolean;
  calidad_general: string;
  estado_mobiliario?: string;
}

export interface PaqueteRequest {
  id: string;
  cantidad: number;
  metros?: number;
}

export interface PartidaRequest {
  categoria: string;
  partida: string;
  cantidad: number;
  calidad?: string;
  notas?: string;
}

export interface TrabajosRequest {
  paquetes: PaqueteRequest[];
  partidas: PartidaRequest[];
}

export interface CalcularPresupuestoRequest {
  proyecto: ProyectoRequest;
  trabajos: TrabajosRequest;
  modo?: string;
  pais?: string;
}

export interface ClienteRequest {
  nombre: string;
  email: string;
  telefono: string;
  direccion_obra?: string;
}

export interface GenerarPDFRequest {
  cliente: ClienteRequest;
  proyecto: ProyectoRequest;
  trabajos: TrabajosRequest;
  modo?: string;
  pais?: string;
}

export interface GuardarPresupuestoRequest {
  user_id: string;
  cliente: ClienteRequest;
  proyecto: ProyectoRequest;
  trabajos: TrabajosRequest;
  modo?: string;
  pais?: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  nombre: string;
  telefono?: string;
  empresa?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface EnviarEmailRequest {
  email_destinatario: string;
  pdf_bytes: string;
  datos_presupuesto: Record<string, unknown>;
  mensaje_personalizado?: string;
}

// ---- Responses ----

export interface PartidaResponse {
  descripcion: string;
  categoria: string;
  cantidad: number;
  unidad: string;
  precio_unitario: number;
  subtotal: number;
  es_paquete: boolean;
  calidad: string;
}

export interface PresupuestoResponse {
  numero: string;
  fecha_emision: string;
  fecha_validez: string;
  subtotal: number;
  iva_porcentaje: number;
  iva_importe: number;
  total: number;
  partidas: PartidaResponse[];
  desglose_por_categoria: Record<string, number>;
  num_partidas: number;
  dias_validez: number;
}

export interface PaqueteInfo {
  id: string;
  nombre: string;
  descripcion: string;
  incluye: string[];
  precios: Record<string, Record<string, unknown>>;
}

export interface PartidaCatalogoInfo {
  nombre: string;
  unidad: string;
  descripcion?: string;
}

export interface CategoriaInfo {
  id: string;
  nombre: string;
  icono: string;
  partidas: PartidaCatalogoInfo[] | string[];
}

export interface PaquetesResponse {
  paquetes: PaqueteInfo[];
  total: number;
}

export interface CategoriasResponse {
  categorias: CategoriaInfo[];
  total: number;
}

export interface UserResponse {
  id: string;
  email: string;
  nombre: string;
  telefono: string | null;
  empresa: string | null;
  fecha_registro: string;
  num_presupuestos: number;
}

export interface AuthResponse {
  message: string;
  user: UserResponse;
  token: string;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  code?: string;
}

export interface GuardarPresupuestoResponse {
  id: string;
  numero_presupuesto: string;
  total: number;
  guardado: boolean;
}

export interface UserBudgetResponse {
  id: string;
  numero_presupuesto: string;
  datos_proyecto: Record<string, unknown>;
  partidas: Record<string, unknown>[];
  cliente_nombre: string | null;
  cliente_email: string | null;
  total_sin_iva: number;
  total_con_iva: number;
  iva_aplicado: number;
  fecha_creacion: string | null;
  fecha_validez: string | null;
}

export interface UserBudgetsListResponse {
  presupuestos: UserBudgetResponse[];
  total: number;
}

export interface EnviarEmailResponse {
  success: boolean;
  message: string;
}
