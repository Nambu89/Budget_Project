import { useState, useEffect } from 'react';
import { useWizard } from './hooks/useWizard';
import { useAuth } from './hooks/useAuth';
import Aurora from './components/reactbits/Aurora';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import PageContainer from './components/layout/PageContainer';
import WizardLayout from './components/wizard/WizardLayout';
import Step1PropertyInfo from './components/steps/Step1PropertyInfo';
import Step2WorkSelector from './components/steps/Step2WorkSelector';
import Step3BudgetResult from './components/steps/Step3BudgetResult';
import Step4CustomerData from './components/steps/Step4CustomerData';
import Step5Completed from './components/steps/Step5Completed';
import MisPresupuestos from './components/pages/MisPresupuestos';
import ResetPassword from './components/pages/ResetPassword';
import { isValidEmail, isRequired } from './utils/validators';

type Page = 'wizard' | 'mis-presupuestos' | 'reset-password';

function WizardApp() {
  const { state, dispatch } = useWizard();
  const { isAuthenticated } = useAuth();
  const [currentPage, setCurrentPage] = useState<Page>('wizard');
  const [resetToken, setResetToken] = useState<string | null>(null);

  // Detectar ?reset_token= en la URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('reset_token');
    if (token) {
      setResetToken(token);
      setCurrentPage('reset-password');
      // Limpiar query param de la URL sin recargar
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const canGoNext = (): boolean => {
    switch (state.currentStep) {
      case 1:
        return state.proyecto.metros_cuadrados > 0;
      case 2:
        return state.paquetes.length > 0 || state.partidas.length > 0;
      case 3:
        return isAuthenticated && !!state.presupuesto;
      case 4:
        return isRequired(state.cliente.nombre) &&
          isValidEmail(state.cliente.email) &&
          isRequired(state.cliente.telefono);
      default:
        return false;
    }
  };

  const getNextLabel = (): string => {
    switch (state.currentStep) {
      case 2: return 'Calcular presupuesto';
      case 3: return 'Datos de contacto';
      case 4: return 'Finalizar';
      default: return 'Siguiente';
    }
  };

  const handleNext = () => {
    if (state.currentStep === 2) {
      dispatch({ type: 'SET_ERROR', error: null });
    }
    dispatch({ type: 'NEXT_STEP' });
  };

  const handleNavigate = (page: Page) => {
    setCurrentPage(page);
  };

  const renderStep = () => {
    switch (state.currentStep) {
      case 1: return <Step1PropertyInfo />;
      case 2: return <Step2WorkSelector />;
      case 3: return <Step3BudgetResult />;
      case 4: return <Step4CustomerData />;
      case 5: return <Step5Completed />;
      default: return null;
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'mis-presupuestos':
        return <MisPresupuestos onBack={() => setCurrentPage('wizard')} />;
      case 'reset-password':
        return (
          <ResetPassword
            token={resetToken || ''}
            onBack={() => setCurrentPage('wizard')}
          />
        );
      case 'wizard':
      default:
        return (
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
        );
    }
  };

  return (
    <>
      <Aurora />
      <Header onNavigate={handleNavigate} currentPage={currentPage} />
      <PageContainer>
        {renderPage()}
      </PageContainer>
      <Footer />
    </>
  );
}

export default function App() {
  return <WizardApp />;
}
