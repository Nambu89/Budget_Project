import { Package, Plus, Trash2 } from 'lucide-react';
import type { PaqueteInfo, PaqueteRequest } from '../../types/api';
import { QUALITY_LABELS, type QualityLevel } from '../../types/domain';
import GlassCard from '../ui/GlassCard';
import SparkButton from '../ui/SparkButton';
import { formatCurrency } from '../../utils/formatters';
import styles from '../../styles/components/Selectors.module.css';

interface Props {
  paquetes: PaqueteInfo[];
  selected: PaqueteRequest[];
  calidad: string;
  onAdd: (paquete: PaqueteRequest) => void;
  onRemove: (id: string) => void;
}

export default function PackageSelector({ paquetes, selected, calidad, onAdd, onRemove }: Props) {
  const isSelected = (id: string) => selected.some(p => p.id === id);

  return (
    <div className={styles.list}>
      {paquetes.map(paq => {
        const precioInfo = paq.precios[calidad] || paq.precios['estandar'] || {};
        const precioBase = (precioInfo as Record<string, unknown>).precio_base as number || 0;
        const active = isSelected(paq.id);

        return (
          <GlassCard key={paq.id} className={active ? styles.cardActive : ''}>
            <div className={styles.cardHeader}>
              <div className={styles.cardIcon}><Package size={20} /></div>
              <div className={styles.cardInfo}>
                <h4 className={styles.cardTitle}>{paq.nombre}</h4>
                <p className={styles.cardDesc}>{paq.descripcion}</p>
              </div>
            </div>

            {paq.incluye.length > 0 && (
              <ul className={styles.includeList}>
                {paq.incluye.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            )}

            <div className={styles.cardFooter}>
              <div className={styles.priceBlock}>
                <span className={styles.priceLabel}>
                  {QUALITY_LABELS[calidad as QualityLevel] || calidad}
                </span>
                <span className={styles.price}>
                  {precioBase > 0 ? formatCurrency(precioBase) : 'Consultar'}
                </span>
              </div>

              {active ? (
                <SparkButton variant="ghost" onClick={() => onRemove(paq.id)}>
                  <Trash2 size={16} /> Quitar
                </SparkButton>
              ) : (
                <SparkButton onClick={() => onAdd({ id: paq.id, cantidad: 1 })}>
                  <Plus size={16} /> Anadir
                </SparkButton>
              )}
            </div>
          </GlassCard>
        );
      })}
    </div>
  );
}
