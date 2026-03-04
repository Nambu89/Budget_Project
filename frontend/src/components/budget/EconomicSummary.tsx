import type { PresupuestoResponse } from '../../types/api';
import GlassCard from '../ui/GlassCard';
import AnimatedNumber from '../ui/AnimatedNumber';
import styles from '../../styles/components/Budget.module.css';

interface Props {
  presupuesto: PresupuestoResponse;
}

export default function EconomicSummary({ presupuesto }: Props) {
  return (
    <GlassCard className={styles.summary}>
      <h4 className={styles.summaryTitle}>Resumen economico</h4>

      <div className={styles.summaryRow}>
        <span>Subtotal (sin IVA)</span>
        <AnimatedNumber value={presupuesto.subtotal} className={styles.summaryValue} />
      </div>

      <div className={styles.summaryRow}>
        <span>IVA ({presupuesto.iva_porcentaje}%)</span>
        <AnimatedNumber value={presupuesto.iva_importe} className={styles.summaryValue} />
      </div>

      <div className={`${styles.summaryRow} ${styles.totalRow}`}>
        <span>TOTAL</span>
        <AnimatedNumber value={presupuesto.total} className={styles.totalValue} />
      </div>

      <div className={styles.meta}>
        <span>Presupuesto: {presupuesto.numero}</span>
        <span>Validez: {presupuesto.dias_validez} dias</span>
        <span>{presupuesto.num_partidas} partidas</span>
      </div>
    </GlassCard>
  );
}
