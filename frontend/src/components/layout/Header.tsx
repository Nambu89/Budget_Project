import { FileText, LogOut } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import GradientText from '../reactbits/GradientText';
import styles from '../../styles/components/Header.module.css';

interface Props {
  onNavigate?: (page: 'wizard' | 'mis-presupuestos') => void;
  currentPage?: string;
}

export default function Header({ onNavigate, currentPage }: Props) {
  const { user, isAuthenticated, logout } = useAuth();

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
        {isAuthenticated && user && (
          <nav className={styles.nav}>
            <span className={styles.userName}>{user.nombre}</span>
            {currentPage !== 'mis-presupuestos' && onNavigate && (
              <button className={styles.navBtn} onClick={() => onNavigate('mis-presupuestos')}>
                <FileText size={16} /> Mis presupuestos
              </button>
            )}
            {currentPage === 'mis-presupuestos' && onNavigate && (
              <button className={styles.navBtn} onClick={() => onNavigate('wizard')}>
                Calculadora
              </button>
            )}
            <button className={styles.navBtn} onClick={logout}>
              <LogOut size={16} /> Salir
            </button>
          </nav>
        )}
      </div>
    </header>
  );
}
