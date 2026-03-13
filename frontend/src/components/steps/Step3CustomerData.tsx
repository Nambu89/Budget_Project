import { useWizard } from '../../hooks/useWizard';
import SplitText from '../reactbits/SplitText';
import CustomerForm from '../forms/CustomerForm';
import styles from '../../styles/components/Steps.module.css';

export default function Step3CustomerData() {
  const { state, dispatch } = useWizard();

  return (
    <section className={styles.step}>
      <SplitText
        text="Datos de contacto"
        className={styles.stepTitle}
        delay={30}
      />
      <p className={styles.stepDesc}>
        Introduce tus datos para generar el presupuesto personalizado.
        No es necesario registrarse.
      </p>
      <CustomerForm
        cliente={state.cliente}
        onChange={changes => dispatch({ type: 'SET_CLIENTE', cliente: changes })}
      />
    </section>
  );
}
