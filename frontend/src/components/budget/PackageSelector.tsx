import { useState } from 'react';
import { Package, Plus, Trash2 } from 'lucide-react';
import type { PaqueteInfo, PaqueteRequest } from '../../types/api';
import { QUALITY_LABELS, type QualityLevel, PropertyType } from '../../types/domain';
import GlassCard from '../ui/GlassCard';
import SparkButton from '../ui/SparkButton';
import { formatCurrency } from '../../utils/formatters';
import styles from '../../styles/components/Selectors.module.css';

interface Props {
  paquetes: PaqueteInfo[];
  selected: PaqueteRequest[];
  calidad: string;
  tipoInmueble: string;
  factor: number;
  onAdd: (paquete: PaqueteRequest) => void;
  onRemove: (id: string) => void;
}

export default function PackageSelector({ paquetes, selected, calidad, tipoInmueble, factor, onAdd, onRemove }: Props) {
  const [metrosInput, setMetrosInput] = useState<Record<string, number>>({});

  const isSelected = (id: string) => selected.some(p => p.id === id);

  const filteredPaquetes = paquetes.filter(paq => {
    const isVivienda = tipoInmueble === PropertyType.PISO || tipoInmueble === PropertyType.VIVIENDA;
    const isLocal = tipoInmueble === PropertyType.LOCAL || tipoInmueble === PropertyType.OFICINA;

    if (paq.id === 'reforma_integral_local') return isLocal;
    if (paq.id === 'reforma_integral_vivienda') return isVivienda;
    if (paq.id === 'salon_completo' || paq.id === 'habitacion_completa') return false; // Eliminados por el feedback

    // El resto (baños, cocinas, aseos) se muestran siempre
    return true;
  });

  const handleAdd = (id: string) => {
    onAdd({
      id,
      cantidad: 1,
      metros: metrosInput[id] || undefined
    });
  };

  return (
    <div className={styles.list}>
      {filteredPaquetes.map(paq => {
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
                  {precioBase > 0 ? formatCurrency(precioBase * factor) : 'Consultar'}
                </span>
                {!active && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginLeft: '10px' }}>
                    <input
                      type="number"
                      min="1"
                      placeholder="m2 (opc)"
                      value={metrosInput[paq.id] || ''}
                      onChange={e => setMetrosInput({ ...metrosInput, [paq.id]: Number(e.target.value) || 0 })}
                      className={styles.metrosInput}
                      style={{ width: '80px', padding: '4px', borderRadius: '4px', border: '1px solid #ccc' }}
                    />
                    <span className={styles.unitLabel}>m²</span>
                  </div>
                )}
              </div>

              {active ? (
                <SparkButton variant="ghost" onClick={() => onRemove(paq.id)}>
                  <Trash2 size={16} /> Quitar
                </SparkButton>
              ) : (
                <SparkButton onClick={() => handleAdd(paq.id)}>
                  <Plus size={16} /> Añadir
                </SparkButton>
              )}
            </div>
          </GlassCard>
        );
      })}
    </div>
  );
}
