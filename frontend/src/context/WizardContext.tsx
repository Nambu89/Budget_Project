import { createContext, useReducer, type ReactNode } from 'react';
import type { ProyectoRequest, PaqueteRequest, PartidaRequest, PresupuestoResponse, ClienteRequest } from '../types/api';

// ---- State ----

export interface WizardState {
  currentStep: number;
  proyecto: ProyectoRequest;
  paquetes: PaqueteRequest[];
  partidas: PartidaRequest[];
  presupuesto: PresupuestoResponse | null;
  cliente: ClienteRequest;
  isCalculating: boolean;
  error: string | null;
}

const initialProyecto: ProyectoRequest = {
  tipo_inmueble: 'piso',
  metros_cuadrados: 80,
  estado_actual: 'normal',
  es_vivienda_habitual: false,
  calidad_general: 'estandar',
};

const initialCliente: ClienteRequest = {
  nombre: '',
  email: '',
  telefono: '',
  direccion_obra: '',
};

export const initialState: WizardState = {
  currentStep: 1,
  proyecto: initialProyecto,
  paquetes: [],
  partidas: [],
  presupuesto: null,
  cliente: initialCliente,
  isCalculating: false,
  error: null,
};

// ---- Actions ----

export type WizardAction =
  | { type: 'SET_STEP'; step: number }
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'SET_PROYECTO'; proyecto: Partial<ProyectoRequest> }
  | { type: 'ADD_PAQUETE'; paquete: PaqueteRequest }
  | { type: 'REMOVE_PAQUETE'; id: string }
  | { type: 'ADD_PARTIDA'; partida: PartidaRequest }
  | { type: 'REMOVE_PARTIDA'; index: number }
  | { type: 'SET_PRESUPUESTO'; presupuesto: PresupuestoResponse }
  | { type: 'SET_CLIENTE'; cliente: Partial<ClienteRequest> }
  | { type: 'SET_CALCULATING'; value: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'RESET' };

function wizardReducer(state: WizardState, action: WizardAction): WizardState {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, currentStep: action.step };
    case 'NEXT_STEP':
      return { ...state, currentStep: Math.min(state.currentStep + 1, 5) };
    case 'PREV_STEP':
      return { ...state, currentStep: Math.max(state.currentStep - 1, 1) };
    case 'SET_PROYECTO':
      return { ...state, proyecto: { ...state.proyecto, ...action.proyecto } };
    case 'ADD_PAQUETE': {
      const exists = state.paquetes.find(p => p.id === action.paquete.id);
      if (exists) return state;
      return { ...state, paquetes: [...state.paquetes, action.paquete] };
    }
    case 'REMOVE_PAQUETE':
      return { ...state, paquetes: state.paquetes.filter(p => p.id !== action.id) };
    case 'ADD_PARTIDA':
      return { ...state, partidas: [...state.partidas, action.partida] };
    case 'REMOVE_PARTIDA':
      return { ...state, partidas: state.partidas.filter((_, i) => i !== action.index) };
    case 'SET_PRESUPUESTO':
      return { ...state, presupuesto: action.presupuesto, isCalculating: false, error: null };
    case 'SET_CLIENTE':
      return { ...state, cliente: { ...state.cliente, ...action.cliente } };
    case 'SET_CALCULATING':
      return { ...state, isCalculating: action.value, error: null };
    case 'SET_ERROR':
      return { ...state, error: action.error, isCalculating: false };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

// ---- Context ----

export interface WizardContextValue {
  state: WizardState;
  dispatch: React.Dispatch<WizardAction>;
}

export const WizardContext = createContext<WizardContextValue | null>(null);

export function WizardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(wizardReducer, initialState);

  return (
    <WizardContext.Provider value={{ state, dispatch }}>
      {children}
    </WizardContext.Provider>
  );
}
