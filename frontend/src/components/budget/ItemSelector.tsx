import { useState } from 'react';
import { Plus } from 'lucide-react';
import type { CategoriaInfo, PartidaRequest, PartidaCatalogoInfo } from '../../types/api';
import { CATEGORY_ICONS } from '../../types/domain';
import GlassCard from '../ui/GlassCard';
import SparkButton from '../ui/SparkButton';
import styles from '../../styles/components/Selectors.module.css';

/** Normaliza partidas: soporta tanto string[] (legacy) como PartidaCatalogoInfo[] */
function normalizePartidas(partidas: PartidaCatalogoInfo[] | string[]): PartidaCatalogoInfo[] {
  if (partidas.length === 0) return [];
  if (typeof partidas[0] === 'string') {
    return (partidas as string[]).map(p => ({ nombre: p, unidad: 'ud' }));
  }
  return partidas as PartidaCatalogoInfo[];
}

interface Props {
  categorias: CategoriaInfo[];
  onAdd: (partida: PartidaRequest) => void;
}

export default function ItemSelector({ categorias, onAdd }: Props) {
  const [selectedCat, setSelectedCat] = useState('');
  const [selectedPartida, setSelectedPartida] = useState('');
  const [cantidad, setCantidad] = useState<number | ''>('');
  const [notas, setNotas] = useState('');
  const [asistenciaAlba, setAsistenciaAlba] = useState(false);

  const currentCat = categorias.find(c => c.id === selectedCat);
  const partidasNormalizadas = currentCat ? normalizePartidas(currentCat.partidas) : [];
  const selectedPartidaInfo = partidasNormalizadas.find(p => p.nombre === selectedPartida);
  const unidadActual = selectedPartidaInfo?.unidad || '';

  const handleAdd = () => {
    const cantidadNum = typeof cantidad === 'number' ? cantidad : 0;
    if (!selectedCat || !selectedPartida || cantidadNum <= 0) return;
    const partida: PartidaRequest = {
      categoria: selectedCat,
      partida: selectedPartida,
      cantidad: cantidadNum,
    };
    if (notas.trim()) {
      partida.notas = notas.trim();
    }
    if (asistenciaAlba) {
      partida.notas = partida.notas
        ? `[Requiere asistencia de albañilería] ${partida.notas}`
        : '[Requiere asistencia de albañilería]';
    }
    onAdd(partida);
    setSelectedPartida('');
    setCantidad('');
    setNotas('');
    setAsistenciaAlba(false);
  };

  return (
    <GlassCard>
      <div className={styles.itemGrid}>
        {/* Categoría */}
        <div className={styles.field}>
          <label htmlFor="cat-select">Categoría</label>
          <select
            id="cat-select"
            value={selectedCat}
            onChange={e => { setSelectedCat(e.target.value); setSelectedPartida(''); }}
          >
            <option value="">Seleccionar categoría...</option>
            {categorias.filter(c => c.id !== 'paquete').map(cat => (
              <option key={cat.id} value={cat.id}>
                {CATEGORY_ICONS[cat.id] || ''} {cat.nombre}
              </option>
            ))}
          </select>
        </div>

        {/* Partida */}
        <div className={styles.field}>
          <label htmlFor="partida-select">Partida</label>
          <select
            id="partida-select"
            value={selectedPartida}
            onChange={e => setSelectedPartida(e.target.value)}
            disabled={!currentCat}
          >
            <option value="">Seleccionar partida...</option>
            {partidasNormalizadas.map(p => (
              <option key={p.nombre} value={p.nombre}>
                {p.descripcion || p.nombre.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        </div>

        {/* Cantidad con unidad */}
        <div className={styles.field}>
          <label htmlFor="cantidad">Cantidad</label>
          <div className={styles.inputWithUnit}>
            <input
              id="cantidad"
              type="number"
              min={1}
              placeholder={unidadActual ? 'Ej: 10' : 'Ej: 1'}
              value={cantidad}
              onChange={e => {
                const val = e.target.value;
                setCantidad(val === '' ? '' : Number(val));
              }}
              onFocus={e => e.target.select()}
            />
            {unidadActual && <span className={styles.unitLabel}>{unidadActual}</span>}
          </div>
        </div>

        {/* Descripción / Notas */}
        <div className={styles.field}>
          <label htmlFor="notas">Descripción / Notas (opcional)</label>
          <textarea
            id="notas"
            className={styles.notasTextarea}
            value={notas}
            onChange={e => setNotas(e.target.value)}
            placeholder="Detalles adicionales sobre esta partida..."
            rows={2}
          />
        </div>

        {/* Asistencia albañilería (Solo Electricidad) */}
        {selectedCat === 'electricidad' && (
          <div className={styles.field} style={{ gridColumn: '1 / -1', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <input
              type="checkbox"
              id="asistenciaAlba"
              checked={asistenciaAlba}
              onChange={e => setAsistenciaAlba(e.target.checked)}
            />
            <label htmlFor="asistenciaAlba" style={{ margin: 0, cursor: 'pointer', fontWeight: 'normal' }}>
              Necesito asistencia de albañilería para estas rozas / puntos
            </label>
          </div>
        )}

        {/* Botón */}
        <div className={styles.fieldBtn}>
          <SparkButton
            onClick={handleAdd}
            disabled={!selectedPartida || (typeof cantidad === 'number' ? cantidad <= 0 : true)}
          >
            <Plus size={16} /> Añadir partida
          </SparkButton>
        </div>
      </div>
    </GlassCard>
  );
}
