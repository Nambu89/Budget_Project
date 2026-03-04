import type { ProyectoRequest } from '../../types/api';
import { PropertyType, PROPERTY_TYPE_LABELS, PropertyState, PROPERTY_STATE_LABELS, QualityLevel, QUALITY_LABELS, QUALITY_DESCRIPTIONS } from '../../types/domain';
import GlassCard from '../ui/GlassCard';
import styles from '../../styles/components/PropertyForm.module.css';

interface Props {
  proyecto: ProyectoRequest;
  onChange: (changes: Partial<ProyectoRequest>) => void;
}

export default function PropertyForm({ proyecto, onChange }: Props) {
  return (
    <div className={styles.grid}>
      {/* Tipo de inmueble */}
      <GlassCard>
        <label htmlFor="tipo">Tipo de inmueble</label>
        <select
          id="tipo"
          value={proyecto.tipo_inmueble}
          onChange={e => onChange({ tipo_inmueble: e.target.value })}
        >
          {Object.values(PropertyType).map(val => (
            <option key={val} value={val}>{PROPERTY_TYPE_LABELS[val]}</option>
          ))}
        </select>
      </GlassCard>

      {/* Metros cuadrados */}
      <GlassCard>
        <label htmlFor="metros">Superficie (m²)</label>
        <input
          id="metros"
          type="number"
          min={1}
          max={10000}
          value={proyecto.metros_cuadrados}
          onChange={e => onChange({ metros_cuadrados: Number(e.target.value) || 0 })}
        />
      </GlassCard>

      {/* Estado actual */}
      <GlassCard>
        <label htmlFor="estado">Estado actual</label>
        <select
          id="estado"
          value={proyecto.estado_actual}
          onChange={e => onChange({ estado_actual: e.target.value })}
        >
          {Object.values(PropertyState).map(val => (
            <option key={val} value={val}>{PROPERTY_STATE_LABELS[val]}</option>
          ))}
        </select>
      </GlassCard>

      {/* Calidad */}
      <GlassCard>
        <label htmlFor="calidad">Nivel de calidad</label>
        <select
          id="calidad"
          value={proyecto.calidad_general}
          onChange={e => onChange({ calidad_general: e.target.value })}
        >
          {Object.values(QualityLevel).map(val => (
            <option key={val} value={val}>{QUALITY_LABELS[val]}</option>
          ))}
        </select>
        <p className={styles.hint}>
          {QUALITY_DESCRIPTIONS[proyecto.calidad_general as QualityLevel] || ''}
        </p>
      </GlassCard>


    </div>
  );
}
