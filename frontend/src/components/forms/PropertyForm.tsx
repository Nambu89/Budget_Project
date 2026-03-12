import type { ProyectoRequest } from '../../types/api';
import { PropertyType, PROPERTY_TYPE_LABELS, PropertyState, PROPERTY_STATE_LABELS, QualityLevel, QUALITY_LABELS, QUALITY_DESCRIPTIONS } from '../../types/domain';
import GlassCard from '../ui/GlassCard';
import styles from '../../styles/components/PropertyForm.module.css';

const FURNITURE_OPTIONS = [
  { value: 'vacio', label: 'Vacío', hint: 'Sin incremento adicional' },
  { value: 'parcial', label: 'Parcialmente amueblado', hint: '+10% por retirada parcial de mobiliario' },
  { value: 'amueblado', label: 'Totalmente amueblado', hint: '+20% por retirada completa de mobiliario' },
] as const;

interface Props {
  proyecto: ProyectoRequest;
  onChange: (changes: Partial<ProyectoRequest>) => void;
}

export default function PropertyForm({ proyecto, onChange }: Props) {
  const currentFurniture = FURNITURE_OPTIONS.find(
    opt => opt.value === (proyecto.estado_mobiliario || 'vacio')
  );

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
        <label htmlFor="metros">Superficie (m2)</label>
        <input
          id="metros"
          type="number"
          min={1}
          max={10000}
          value={proyecto.metros_cuadrados}
          onChange={e => onChange({ metros_cuadrados: Number(e.target.value) || 0 })}
        />
      </GlassCard>

      {/* Habitaciones y Baños (Solo aplica a viviendas generalmente, pero dejémoslo común o con lógica) */}
      {(proyecto.tipo_inmueble === PropertyType.PISO || proyecto.tipo_inmueble === PropertyType.VIVIENDA) && (
        <>
          <GlassCard>
            <label htmlFor="habitaciones">Número de habitaciones</label>
            <input
              id="habitaciones"
              type="number"
              min={0}
              max={20}
              value={proyecto.habitaciones || 0}
              onChange={e => onChange({ habitaciones: Number(e.target.value) || 0 })}
            />
          </GlassCard>
          <GlassCard>
            <label htmlFor="banos">Número de baños</label>
            <input
              id="banos"
              type="number"
              min={0}
              max={10}
              value={proyecto.banos || 0}
              onChange={e => onChange({ banos: Number(e.target.value) || 0 })}
            />
          </GlassCard>
        </>
      )}

      {/* Vivienda independiente: Plantas */}
      {proyecto.tipo_inmueble === PropertyType.VIVIENDA && (
        <GlassCard>
          <label htmlFor="plantas">Número de plantas</label>
          <input
            id="plantas"
            type="number"
            min={1}
            max={10}
            value={proyecto.plantas || 1}
            onChange={e => onChange({ plantas: Number(e.target.value) || 1 })}
          />
        </GlassCard>
      )}

      {/* Local / Oficina: Salas y Aseos */}
      {(proyecto.tipo_inmueble === PropertyType.LOCAL || proyecto.tipo_inmueble === PropertyType.OFICINA) && (
        <>
          <GlassCard>
            <label htmlFor="salas">Número de salas</label>
            <input
              id="salas"
              type="number"
              min={0}
              max={50}
              value={proyecto.salas || 0}
              onChange={e => onChange({ salas: Number(e.target.value) || 0 })}
            />
          </GlassCard>
          <GlassCard>
            <label htmlFor="aseos">Número de aseos</label>
            <input
              id="aseos"
              type="number"
              min={0}
              max={20}
              value={proyecto.aseos || 0}
              onChange={e => onChange({ aseos: Number(e.target.value) || 0 })}
            />
          </GlassCard>
        </>
      )}

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

      {/* Contenido del inmueble */}
      <GlassCard>
        <label htmlFor="mobiliario">Contenido del inmueble</label>
        <select
          id="mobiliario"
          value={proyecto.estado_mobiliario || 'vacio'}
          onChange={e => onChange({ estado_mobiliario: e.target.value })}
        >
          {FURNITURE_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <p className={styles.hint}>
          {currentFurniture?.hint || ''}
        </p>
      </GlassCard>

    </div>
  );
}
