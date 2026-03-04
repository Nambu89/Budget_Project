import { ChevronLeft, ChevronRight } from 'lucide-react';
import SparkButton from '../ui/SparkButton';
import styles from '../../styles/components/WizardNavigation.module.css';

interface Props {
  currentStep: number;
  onPrev: () => void;
  onNext: () => void;
  canNext?: boolean;
  nextLabel?: string;
  isLoading?: boolean;
}

export default function WizardNavigation({
  currentStep,
  onPrev,
  onNext,
  canNext = true,
  nextLabel,
  isLoading = false,
}: Props) {
  const isFirst = currentStep === 1;
  const isLast = currentStep === 5;

  return (
    <div className={styles.nav}>
      {!isFirst && (
        <SparkButton variant="secondary" onClick={onPrev}>
          <ChevronLeft size={18} />
          Anterior
        </SparkButton>
      )}

      <div className={styles.spacer} />

      {!isLast && (
        <SparkButton onClick={onNext} disabled={!canNext || isLoading}>
          {isLoading ? 'Calculando...' : nextLabel || 'Siguiente'}
          {!isLoading && <ChevronRight size={18} />}
        </SparkButton>
      )}
    </div>
  );
}
