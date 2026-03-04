import type { ReactNode } from 'react';
import styles from '../../styles/components/GlassCard.module.css';

interface Props {
  children: ReactNode;
  className?: string;
}

export default function GlassCard({ children, className = '' }: Props) {
  return (
    <div className={`${styles.card} ${className}`}>
      {children}
    </div>
  );
}
