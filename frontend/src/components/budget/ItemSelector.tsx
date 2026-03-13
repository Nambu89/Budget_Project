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
  const [cantidad, setCantidad] = useState(1);
  const [notas, setNotas] = useState('');
  const [asistenciaAlba, setAsistenciaAlba] = useState(false);

  const currentCat = categorias.find(c => c.id === selectedCat);
  const partidasNormalizadas = currentCat ? normalizePartidas(currentCat.partidas) : [];
  const selectedPartidaInfo = partidasNormalizadas.find(p => p.nombre === selectedPartida);
  const unidadActual = selectedPartidaInfo?.unidad || '';

  const handleAdd = () => {
    if (!selectedCat || !selectedPartida || cantidad <= 0) return;
    const partida: PartidaRequest = {
      categoria: selectedCat,
      partida: selectedPartida,
      cantidad,
    };
    if (notas.trim()) {
      partida.notas = notas.trim();
    }
    if (asistenciaAlba) {
      partida.notas = partida.notas ? `[Requiere asistencia de alba\u00f1iler\u00eda] ${partida.notas}` : '[Requiere asistencia de alba\u00f1iler\u00eda]';
    }
    onAdd(partida);
    setSelectedPartida('');
    setCantidad(1);
    setNotas('');
    setAsistenciaAlba(false);
  };

  return (
    <GlassCard>
      <div className={styles.itemGrid}>
        {/* Categor\u00eda */}
        <div className={styles.field}>
          <label htmlFor="cat-select">Categor\u00eda</label>
          <select
            id="cat-select"
            value={selectedCat}
            onChange={e => { setSelectedCat(e.target.value); setSelectedPartida(''); }}
          >
            <option value="">Seleccionar categor\u00eda...</option>
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
          <label htmlFor="cantidad">
            Cantidad{unidadActual ? ` (${unidadActual})` : ''}
          </label>
          <div className={styles.inputWithUnit}>
            <input
              id="cantidad"
              type="number"
              min={1}
              value={cantidad}
              onChange={e => setCantidad(Number(e.target.value) || 1)}
            />
            {unidadActual && <span className={styles.unitLabel}>{unidadActual}</span>}
          </div>
        </div>

        {/* Descripci\u00f3n / Notas */}
        <div className={styles.field}>
          <label htmlFor="notas">Descripci\u00f3n / Notas (opcional)</label>
          <textarea
            id="notas"
            className={styles.notasTextarea}
            value={notas}
            onChange={e => setNotas(e.target.value)}
            placeholder="Detalles adicionales sobre esta partida..."
            rows={2}
          />
        </div>

        {/* Asistencia alba\u00f1iler\u00eda (Solo Electricidad) */}
        {selectedCat === 'electricidad' && (
          <div className={styles.field} style={{ gridColumn: '1 / -1', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <input
              type="checkbox"
              id="asistenciaAlba"
              checked={asistenciaAlba}
              onChange={e => setAsistenciaAlba(e.target.checked)}
            />
            <label htmlFor="asistenciaAlba" style={{ margin: 0, cursor: 'pointer', fontWeight: 'normal' }}>
              Necesito asistencia de alba\u00f1iler\u00eda para estas rozas / puntos
            </label>
          </div>
        )}

        {/* Bot\u00f3n */}
        <div className={styles.fieldBtn}>
          <SparkButton
            onClick={handleAdd}
            disabled={!selectedPartida || cantidad <= 0}
          >
            <Plus size={16} /> A\u00f1adir partida
          </SparkButton>
        </div>
      </div>
    </GlassCard>
  );
}
