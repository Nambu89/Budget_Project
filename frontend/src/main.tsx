import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { WizardProvider } from './context/WizardContext';
import App from './App';
import './styles/global.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <WizardProvider>
      <App />
    </WizardProvider>
  </StrictMode>,
);
