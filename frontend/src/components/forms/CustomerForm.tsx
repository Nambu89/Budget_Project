import type { ClienteRequest } from '../../types/api';
import GlassCard from '../ui/GlassCard';
import styles from '../../styles/components/PropertyForm.module.css';

interface Props {
  cliente: ClienteRequest;
  onChange: (changes: Partial<ClienteRequest>) => void;
}

export default function CustomerForm({ cliente, onChange }: Props) {
  return (
    <div className={styles.grid}>
      <GlassCard>
        <label htmlFor="nombre">Nombre completo *</label>
        <input
          id="nombre"
          value={cliente.nombre}
          onChange={e => onChange({ nombre: e.target.value })}
          placeholder="Ej: Juan Perez"
          style={{ width: '100%', marginTop: 4 }}
        />
      </GlassCard>

      <GlassCard>
        <label htmlFor="email">Email *</label>
        <input
          id="email"
          type="email"
          value={cliente.email}
          onChange={e => onChange({ email: e.target.value })}
          placeholder="juan@ejemplo.com"
          style={{ width: '100%', marginTop: 4 }}
        />
      </GlassCard>

      <GlassCard>
        <label htmlFor="telefono">Telefono *</label>
        <input
          id="telefono"
          value={cliente.telefono}
          onChange={e => onChange({ telefono: e.target.value })}
          placeholder="600 123 456"
          style={{ width: '100%', marginTop: 4 }}
        />
      </GlassCard>

      <GlassCard>
        <label htmlFor="direccion">Direccion de la obra (opcional)</label>
        <input
          id="direccion"
          value={cliente.direccion_obra || ''}
          onChange={e => onChange({ direccion_obra: e.target.value })}
          placeholder="Calle, numero, ciudad"
          style={{ width: '100%', marginTop: 4 }}
        />
      </GlassCard>
    </div>
  );
}
