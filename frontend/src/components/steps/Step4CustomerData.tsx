import { useWizard } from '../../hooks/useWizard';
import { useAuth } from '../../hooks/useAuth';
import { useEffect } from 'react';
import SplitText from '../reactbits/SplitText';
import CustomerForm from '../forms/CustomerForm';
import styles from '../../styles/components/Steps.module.css';

export default function Step4CustomerData() {
  const { state, dispatch } = useWizard();
  const { user } = useAuth();

  // Pre-fill from auth user
  useEffect(() => {
    if (user && !state.cliente.email) {
      dispatch({
        type: 'SET_CLIENTE',
        cliente: {
          nombre: user.nombre || '',
          email: user.email || '',
          telefono: user.telefono || '',
        },
      });
    }
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <section className={styles.step}>
      <SplitText
        text="Datos de contacto"
        className={styles.stepTitle}
        delay={30}
      />
      <p className={styles.stepDesc}>
        Introduce tus datos para generar el presupuesto personalizado en PDF.
      </p>
      <CustomerForm
        cliente={state.cliente}
        onChange={changes => dispatch({ type: 'SET_CLIENTE', cliente: changes })}
      />
    </section>
  );
}
