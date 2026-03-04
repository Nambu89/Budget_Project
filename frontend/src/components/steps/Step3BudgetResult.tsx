import { useEffect } from 'react';
import { useWizard } from '../../hooks/useWizard';
import { useAuth } from '../../hooks/useAuth';
import { calcularPresupuesto } from '../../api/presupuesto';
import SplitText from '../reactbits/SplitText';
import BudgetBreakdown from '../budget/BudgetBreakdown';
import EconomicSummary from '../budget/EconomicSummary';
import PriceRangeTeaser from '../budget/PriceRangeTeaser';
import RegistrationGate from '../auth/RegistrationGate';
import LoadingSpinner from '../ui/LoadingSpinner';
import styles from '../../styles/components/Steps.module.css';

export default function Step3BudgetResult() {
  const { state, dispatch } = useWizard();
  const { isAuthenticated } = useAuth();

  // Calcular presupuesto al montar
  useEffect(() => {
    if (state.presupuesto || state.isCalculating) return;

    const calculate = async () => {
      dispatch({ type: 'SET_CALCULATING', value: true });
      try {
        const res = await calcularPresupuesto({
          proyecto: state.proyecto,
          trabajos: {
            paquetes: state.paquetes,
            partidas: state.partidas,
          },
        });
        dispatch({ type: 'SET_PRESUPUESTO', presupuesto: res });
      } catch (err) {
        dispatch({
          type: 'SET_ERROR',
          error: err instanceof Error ? err.message : 'Error calculando presupuesto',
        });
      }
    };

    calculate();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (state.isCalculating) {
    return <LoadingSpinner text="Calculando tu presupuesto..." />;
  }

  if (state.error) {
    return (
      <section className={styles.step}>
        <div className={styles.errorBox}>{state.error}</div>
      </section>
    );
  }

  if (!state.presupuesto) return null;

  return (
    <section className={styles.step}>
      <SplitText
        text="Tu presupuesto"
        className={styles.stepTitle}
        delay={30}
      />

      {isAuthenticated ? (
        <>
          <p className={styles.stepDesc}>
            Aqui tienes el desglose completo de tu presupuesto de reforma.
          </p>
          <BudgetBreakdown partidas={state.presupuesto.partidas} />
          <EconomicSummary presupuesto={state.presupuesto} />
        </>
      ) : (
        <>
          <PriceRangeTeaser total={state.presupuesto.total} />
          <RegistrationGate onAuthenticated={() => {
            // Forzar re-render al autenticarse
            dispatch({ type: 'SET_STEP', step: 3 });
          }} />
        </>
      )}
    </section>
  );
}
