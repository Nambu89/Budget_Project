import GradientText from '../reactbits/GradientText';
import styles from '../../styles/components/Header.module.css';

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <img src="/logo-isi.jpeg" alt="ISI Obras y Servicios" className={styles.logo} />
        <div className={styles.titleBlock}>
          <h1 className={styles.title}>
            <GradientText>Calculadora de Presupuestos</GradientText>
          </h1>
          <p className={styles.subtitle}>
            Calcula tu presupuesto de reforma en menos de 3 minutos
          </p>
        </div>
      </div>
    </header>
  );
}
