import { useWizard } from './hooks/useWizard';
import Aurora from './components/reactbits/Aurora';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import PageContainer from './components/layout/PageContainer';
import WizardLayout from './components/wizard/WizardLayout';
import Step1PropertyInfo from './components/steps/Step1PropertyInfo';
import Step2WorkSelector from './components/steps/Step2WorkSelector';
import Step3CustomerData from './components/steps/Step3CustomerData';
import Step4BudgetFinal from './components/steps/Step4BudgetFinal';
import { isValidEmail, isRequired } from './utils/validators';

function WizardApp() {
  const { state, dispatch } = useWizard();

  const canGoNext = (): boolean => {
    switch (state.currentStep) {
      case 1:
        return state.proyecto.metros_cuadrados > 0;
      case 2:
        return state.paquetes.length > 0 || state.partidas.length > 0;
      case 3:
        return isRequired(state.cliente.nombre) &&
          isRequired(state.cliente.dni) &&
          isValidEmail(state.cliente.email) &&
          isRequired(state.cliente.telefono);
      default:
        return false;
    }
  };

  const getNextLabel = (): string => {
    switch (state.currentStep) {
      case 2: return 'Datos de contacto';
      case 3: return 'Calcular presupuesto';
      default: return 'Siguiente';
    }
  };

  const handleNext = () => {
    if (state.currentStep === 3) {
      dispatch({ type: 'SET_ERROR', error: null });
    }
    dispatch({ type: 'NEXT_STEP' });
  };

  const renderStep = () => {
    switch (state.currentStep) {
      case 1: return <Step1PropertyInfo />;
      case 2: return <Step2WorkSelector />;
      case 3: return <Step3CustomerData />;
      case 4: return <Step4BudgetFinal />;
      default: return null;
    }
  };

  return (
    <>
      <Aurora />
      <Header />
      <PageContainer>
        <WizardLayout
          currentStep={state.currentStep}
          onPrev={() => dispatch({ type: 'PREV_STEP' })}
          onNext={handleNext}
          canNext={canGoNext()}
          nextLabel={getNextLabel()}
          isLoading={state.isCalculating}
        >
          {renderStep()}
        </WizardLayout>
      </PageContainer>
      <Footer />
    </>
  );
}

export default function App() {
  return <WizardApp />;
}
