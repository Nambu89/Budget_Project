import type { ReactNode } from 'react';
import styles from '../../styles/components/PageContainer.module.css';

interface Props {
  children: ReactNode;
}

export default function PageContainer({ children }: Props) {
  return (
    <main className={styles.container}>
      {children}
    </main>
  );
}
