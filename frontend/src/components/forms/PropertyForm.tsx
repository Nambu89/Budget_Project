import type { ProyectoRequest } from '../../types/api';
import { PropertyType, PROPERTY_TYPE_LABELS, PropertyState, PROPERTY_STATE_LABELS, QualityLevel, QUALITY_LABELS, QUALITY_DESCRIPTIONS } from '../../types/domain';
import GlassCard from '../ui/GlassCard';
import styles from '../../styles/components/PropertyForm.module.css';

const FURNITURE_OPTIONS = [
  { value: 'vacio', label: 'Vacío', hint: 'Sin incremento adicional' },
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

  const handleNumberChange = (field: keyof ProyectoRequest, value: string, fallback: number = 0) => {
    onChange({ [field]: value === '' ? fallback : Number(value) } as Partial<ProyectoRequest>);
  };

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
        <label htmlFor="metros">Superficie</label>
        <div className={styles.inputWithUnit}>
          <input
            id="metros"
            type="number"
            min={1}
            max={10000}
            placeholder="Ej: 80"
            value={proyecto.metros_cuadrados || ''}
            onChange={e => handleNumberChange('metros_cuadrados', e.target.value)}
            onFocus={e => e.target.select()}
          />
          <span className={styles.unitLabel}>m²</span>
        </div>
      </GlassCard>

      {/* Habitaciones y Baños */}
      {(proyecto.tipo_inmueble === PropertyType.PISO || proyecto.tipo_inmueble === PropertyType.VIVIENDA) && (
        <>
          <GlassCard>
            <label htmlFor="habitaciones">Habitaciones</label>
            <div className={styles.inputWithUnit}>
              <input
                id="habitaciones"
                type="number"
                min={0}
                max={20}
                placeholder="Ej: 3"
                value={proyecto.habitaciones || ''}
                onChange={e => handleNumberChange('habitaciones', e.target.value)}
                onFocus={e => e.target.select()}
              />
              <span className={styles.unitLabel}>ud</span>
            </div>
          </GlassCard>
          <GlassCard>
            <label htmlFor="banos">Fontanerías</label>
            <div className={styles.inputWithUnit}>
              <input
                id="banos"
                type="number"
                min={0}
                max={10}
                placeholder="Ej: 2"
                value={proyecto.banos || ''}
                onChange={e => handleNumberChange('banos', e.target.value)}
                onFocus={e => e.target.select()}
              />
              <span className={styles.unitLabel}>ud</span>
            </div>
          </GlassCard>
        </>
      )}

      {/* Vivienda independiente: Plantas */}
      {proyecto.tipo_inmueble === PropertyType.VIVIENDA && (
        <GlassCard>
          <label htmlFor="plantas">Plantas</label>
          <div className={styles.inputWithUnit}>
            <input
              id="plantas"
              type="number"
              min={1}
              max={10}
              placeholder="Ej: 2"
              value={proyecto.plantas || ''}
              onChange={e => handleNumberChange('plantas', e.target.value, 1)}
              onFocus={e => e.target.select()}
            />
            <span className={styles.unitLabel}>ud</span>
          </div>
        </GlassCard>
      )}

      {/* Local / Oficina: Salas y Aseos */}
      {(proyecto.tipo_inmueble === PropertyType.LOCAL || proyecto.tipo_inmueble === PropertyType.OFICINA) && (
        <>
          <GlassCard>
            <label htmlFor="salas">Salas</label>
            <div className={styles.inputWithUnit}>
              <input
                id="salas"
                type="number"
                min={0}
                max={50}
                placeholder="Ej: 3"
                value={proyecto.salas || ''}
                onChange={e => handleNumberChange('salas', e.target.value)}
                onFocus={e => e.target.select()}
              />
              <span className={styles.unitLabel}>ud</span>
            </div>
          </GlassCard>
          <GlassCard>
            <label htmlFor="aseos">Aseos</label>
            <div className={styles.inputWithUnit}>
              <input
                id="aseos"
                type="number"
                min={0}
                max={20}
                placeholder="Ej: 1"
                value={proyecto.aseos || ''}
                onChange={e => handleNumberChange('aseos', e.target.value)}
                onFocus={e => e.target.select()}
              />
              <span className={styles.unitLabel}>ud</span>
            </div>
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
