import type { ReactNode, ButtonHTMLAttributes } from 'react';
import ClickSpark from '../reactbits/ClickSpark';
import styles from '../../styles/components/SparkButton.module.css';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
}

export default function SparkButton({ children, variant = 'primary', className = '', ...rest }: Props) {
  return (
    <ClickSpark sparkColor={variant === 'primary' ? '#FFB84D' : '#F39200'}>
      <button
        className={`${styles.btn} ${styles[variant]} ${className}`}
        {...rest}
      >
        {children}
      </button>
    </ClickSpark>
  );
}
