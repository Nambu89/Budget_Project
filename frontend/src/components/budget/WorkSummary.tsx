import { Trash2, Package, Wrench } from 'lucide-react';
import type { PaqueteRequest, PartidaRequest } from '../../types/api';
import GlassCard from '../ui/GlassCard';
import styles from '../../styles/components/Selectors.module.css';

interface Props {
  paquetes: PaqueteRequest[];
  partidas: PartidaRequest[];
  onRemovePaquete: (id: string) => void;
  onRemovePartida: (index: number) => void;
}

export default function WorkSummary({ paquetes, partidas, onRemovePaquete, onRemovePartida }: Props) {
  const total = paquetes.length + partidas.length;

  if (total === 0) return null;

  return (
    <GlassCard>
      <h4 className={styles.summaryTitle}>
        Trabajos seleccionados ({total})
      </h4>

      {paquetes.map(p => (
        <div key={p.id} className={styles.summaryItem}>
          <Package size={16} className={styles.iconPkg} />
          <span className={styles.summaryName}>
            {p.id.replace(/_/g, ' ')} x{p.cantidad}
          </span>
          <button className={styles.removeBtn} onClick={() => onRemovePaquete(p.id)}>
            <Trash2 size={14} />
          </button>
        </div>
      ))}

      {partidas.map((p, i) => (
        <div key={i} className={styles.summaryItem}>
          <Wrench size={16} className={styles.iconItem} />
          <span className={styles.summaryName}>
            {p.partida.replace(/_/g, ' ')} — {p.cantidad} ud
          </span>
          <button className={styles.removeBtn} onClick={() => onRemovePartida(i)}>
            <Trash2 size={14} />
          </button>
        </div>
      ))}
    </GlassCard>
  );
}
