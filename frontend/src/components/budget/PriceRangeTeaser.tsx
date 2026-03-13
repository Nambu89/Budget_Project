import GlassCard from '../ui/GlassCard';
import AnimatedNumber from '../ui/AnimatedNumber';
import ShinyText from '../reactbits/ShinyText';
import styles from '../../styles/components/Budget.module.css';

interface Props {
  total: number;
}

export default function PriceRangeTeaser({ total }: Props) {
  const low = total * 0.97;
  const high = total * 1.03;

  return (
    <GlassCard className={styles.teaser}>
      <div className={styles.teaserBadge}>
        <ShinyText speed={2} color="rgba(255,255,255,0.4)">
          GRATIS
        </ShinyText>
      </div>

      <h3 className={styles.teaserTitle}>Tu presupuesto estimado</h3>
      <p className={styles.teaserSubtitle}>Rango aproximado (±3%)</p>

      <div className={styles.rangeDisplay}>
        <AnimatedNumber value={low} className={styles.rangeValue} />
        <span className={styles.rangeSep}>—</span>
        <AnimatedNumber value={high} className={styles.rangeValue} />
      </div>

      <p className={styles.teaserCta}>
        Reg\u00edstrate gratis para ver el precio exacto, descargar el PDF y guardar tu presupuesto.
      </p>
    </GlassCard>
  );
}
