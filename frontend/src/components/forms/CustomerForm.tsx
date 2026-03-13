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
          placeholder="Ej: Juan P\u00e9rez"
          style={{ width: '100%', marginTop: 4 }}
        />
      </GlassCard>

      <GlassCard>
        <label htmlFor="dni">DNI / NIF *</label>
        <input
          id="dni"
          value={cliente.dni}
          onChange={e => onChange({ dni: e.target.value })}
          placeholder="12345678A"
          style={{ width: '100%', marginTop: 4 }}
        />
      </GlassCard>

      <GlassCard>
        <label htmlFor="telefono">Tel\u00e9fono *</label>
        <input
          id="telefono"
          value={cliente.telefono}
          onChange={e => onChange({ telefono: e.target.value })}
          placeholder="600 123 456"
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
    </div>
  );
}
