import { useState, useEffect, useRef } from 'react';
import type { PaqueteInfo, CategoriaInfo } from '../types/api';
import { getPaquetes, getCategorias } from '../api/catalogos';

interface CatalogosState {
  paquetes: PaqueteInfo[];
  categorias: CategoriaInfo[];
  isLoading: boolean;
  error: string | null;
}

export function useCatalogos() {
  const [state, setState] = useState<CatalogosState>({
    paquetes: [],
    categorias: [],
    isLoading: true,
    error: null,
  });
  const fetched = useRef(false);

  useEffect(() => {
    if (fetched.current) return;
    fetched.current = true;

    async function load() {
      try {
        const [paqRes, catRes] = await Promise.all([getPaquetes(), getCategorias()]);
        setState({
          paquetes: paqRes.paquetes,
          categorias: catRes.categorias,
          isLoading: false,
          error: null,
        });
      } catch (err) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: err instanceof Error ? err.message : 'Error cargando catalogos',
        }));
      }
    }

    load();
  }, []);

  return state;
}
