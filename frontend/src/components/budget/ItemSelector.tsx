import { useState } from 'react';
import { Plus } from 'lucide-react';
import type { CategoriaInfo, PartidaRequest } from '../../types/api';
import { CATEGORY_ICONS } from '../../types/domain';
import GlassCard from '../ui/GlassCard';
import SparkButton from '../ui/SparkButton';
import styles from '../../styles/components/Selectors.module.css';

interface Props {
  categorias: CategoriaInfo[];
  onAdd: (partida: PartidaRequest) => void;
}

export default function ItemSelector({ categorias, onAdd }: Props) {
  const [selectedCat, setSelectedCat] = useState('');
  const [selectedPartida, setSelectedPartida] = useState('');
  const [cantidad, setCantidad] = useState(1);

  const currentCat = categorias.find(c => c.id === selectedCat);

  const handleAdd = () => {
    if (!selectedCat || !selectedPartida || cantidad <= 0) return;
    onAdd({
      categoria: selectedCat,
      partida: selectedPartida,
      cantidad,
    });
    setSelectedPartida('');
    setCantidad(1);
  };

  return (
    <GlassCard>
      <div className={styles.itemGrid}>
        {/* Categoria */}
        <div className={styles.field}>
          <label htmlFor="cat-select">Categoria</label>
          <select
            id="cat-select"
            value={selectedCat}
            onChange={e => { setSelectedCat(e.target.value); setSelectedPartida(''); }}
          >
            <option value="">Seleccionar categoria...</option>
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
            {currentCat?.partidas.map(p => (
              <option key={p} value={p}>
                {p.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        </div>

        {/* Cantidad */}
        <div className={styles.field}>
          <label htmlFor="cantidad">Cantidad</label>
          <input
            id="cantidad"
            type="number"
            min={1}
            value={cantidad}
            onChange={e => setCantidad(Number(e.target.value) || 1)}
          />
        </div>

        {/* Boton */}
        <div className={styles.fieldBtn}>
          <SparkButton
            onClick={handleAdd}
            disabled={!selectedPartida || cantidad <= 0}
          >
            <Plus size={16} /> Anadir partida
          </SparkButton>
        </div>
      </div>
    </GlassCard>
  );
}
