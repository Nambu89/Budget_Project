import type { PartidaResponse } from '../../types/api';
import { CATEGORY_ICONS } from '../../types/domain';
import GlassCard from '../ui/GlassCard';
import { formatCurrency } from '../../utils/formatters';
import styles from '../../styles/components/Budget.module.css';

interface Props {
  partidas: PartidaResponse[];
}

export default function BudgetBreakdown({ partidas }: Props) {
  // Agrupar por categoria
  const byCategory: Record<string, PartidaResponse[]> = {};
  for (const p of partidas) {
    if (!byCategory[p.categoria]) byCategory[p.categoria] = [];
    byCategory[p.categoria].push(p);
  }

  return (
    <div className={styles.breakdown}>
      {Object.entries(byCategory).map(([cat, items]) => (
        <GlassCard key={cat}>
          <h4 className={styles.catTitle}>
            {CATEGORY_ICONS[cat] || '🔧'} {cat.replace(/_/g, ' ')}
          </h4>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Descripcion</th>
                <th>Cant.</th>
                <th>Ud.</th>
                <th>P. Unit.</th>
                <th>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, i) => (
                <tr key={i}>
                  <td>{item.descripcion}</td>
                  <td>{item.cantidad}</td>
                  <td>{item.unidad}</td>
                  <td>{formatCurrency(item.precio_unitario)}</td>
                  <td className={styles.priceCell}>{formatCurrency(item.subtotal)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </GlassCard>
      ))}
    </div>
  );
}
