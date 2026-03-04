import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import GlassCard from '../ui/GlassCard';
import SparkButton from '../ui/SparkButton';
import { isValidEmail, isValidPassword, isRequired } from '../../utils/validators';
import styles from '../../styles/components/RegistrationGate.module.css';

interface Props {
  onAuthenticated: () => void;
}

export default function RegistrationGate({ onAuthenticated }: Props) {
  const { login, register, error, clearError, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<'register' | 'login'>('register');

  // Register form
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regPhone, setRegPhone] = useState('');

  // Login form
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  const handleRegister = async () => {
    if (!isRequired(regName) || !isValidEmail(regEmail) || !isValidPassword(regPassword)) return;
    try {
      await register({ email: regEmail, password: regPassword, nombre: regName, telefono: regPhone || undefined });
      onAuthenticated();
    } catch { /* error handled by context */ }
  };

  const handleLogin = async () => {
    if (!isValidEmail(loginEmail) || !isValidPassword(loginPassword)) return;
    try {
      await login(loginEmail, loginPassword);
      onAuthenticated();
    } catch { /* error handled by context */ }
  };

  return (
    <GlassCard className={styles.gate}>
      <h3 className={styles.title}>Accede para ver tu presupuesto exacto</h3>
      <p className={styles.subtitle}>Registrate gratis y obtendras:</p>
      <ul className={styles.benefits}>
        <li>Precio exacto detallado</li>
        <li>Descarga en PDF profesional</li>
        <li>Guardar y comparar presupuestos</li>
        <li>Ofertas exclusivas</li>
      </ul>

      {/* Tabs */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'register' ? styles.tabActive : ''}`}
          onClick={() => { setActiveTab('register'); clearError(); }}
        >
          Registrarse
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'login' ? styles.tabActive : ''}`}
          onClick={() => { setActiveTab('login'); clearError(); }}
        >
          Iniciar sesion
        </button>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {activeTab === 'register' ? (
        <div className={styles.form}>
          <input placeholder="Nombre completo *" value={regName} onChange={e => setRegName(e.target.value)} />
          <input placeholder="Email *" type="email" value={regEmail} onChange={e => setRegEmail(e.target.value)} />
          <input placeholder="Contrasena (min. 6 caracteres) *" type="password" value={regPassword} onChange={e => setRegPassword(e.target.value)} />
          <input placeholder="Telefono (opcional)" value={regPhone} onChange={e => setRegPhone(e.target.value)} />
          <SparkButton onClick={handleRegister} disabled={isLoading}>
            {isLoading ? 'Registrando...' : 'Registrarme gratis'}
          </SparkButton>
        </div>
      ) : (
        <div className={styles.form}>
          <input placeholder="Email *" type="email" value={loginEmail} onChange={e => setLoginEmail(e.target.value)} />
          <input placeholder="Contrasena *" type="password" value={loginPassword} onChange={e => setLoginPassword(e.target.value)} />
          <SparkButton onClick={handleLogin} disabled={isLoading}>
            {isLoading ? 'Iniciando sesion...' : 'Iniciar sesion'}
          </SparkButton>
        </div>
      )}
    </GlassCard>
  );
}
