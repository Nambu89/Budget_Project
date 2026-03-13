import { useWizard } from '../../hooks/useWizard';
import SplitText from '../reactbits/SplitText';
import PropertyForm from '../forms/PropertyForm';
import styles from '../../styles/components/Steps.module.css';

export default function Step1PropertyInfo() {
  const { state, dispatch } = useWizard();

  return (
    <section className={styles.step}>
      <SplitText
        text="Datos del inmueble"
        className={styles.stepTitle}
        delay={30}
      />
      <p className={styles.stepDesc}>
        Indica las caracter\u00edsticas b\u00e1sicas de tu inmueble para personalizar el presupuesto.
      </p>
      <PropertyForm
        proyecto={state.proyecto}
        onChange={changes => dispatch({ type: 'SET_PROYECTO', proyecto: changes })}
      />
    </section>
  );
}
