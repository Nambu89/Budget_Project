import { Check } from 'lucide-react';
import ShinyText from '../reactbits/ShinyText';
import styles from '../../styles/components/WizardStepper.module.css';

const STEPS = [
  { label: 'Tipo' },
  { label: 'Trabajos' },
  { label: 'Datos' },
  { label: 'Presupuesto' },
];

interface Props {
  currentStep: number;
}

export default function WizardStepper({ currentStep }: Props) {
  return (
    <nav className={styles.stepper} aria-label="Progreso del presupuesto">
      {STEPS.map((step, idx) => {
        const stepNum = idx + 1;
        const isCompleted = stepNum < currentStep;
        const isActive = stepNum === currentStep;
        const isPending = stepNum > currentStep;

        return (
          <div key={idx} className={styles.stepWrapper}>
            {/* Linea conectora */}
            {idx > 0 && (
              <div className={styles.lineWrapper}>
                <div
                  className={`${styles.line} ${stepNum <= currentStep ? styles.lineFilled : ''}`}
                />
              </div>
            )}

            {/* Circulo */}
            <div
              className={`
                ${styles.circle}
                ${isCompleted ? styles.completed : ''}
                ${isActive ? styles.active : ''}
                ${isPending ? styles.pending : ''}
              `}
              aria-current={isActive ? 'step' : undefined}
            >
              {isCompleted ? (
                <Check size={20} strokeWidth={3} />
              ) : isActive ? (
                <ShinyText speed={2.5} color="rgba(255,255,255,0.5)">
                  <span className={styles.activeNumber}>{stepNum}</span>
                </ShinyText>
              ) : (
                <span className={styles.pendingNumber}>{stepNum}</span>
              )}
            </div>

            {/* Label */}
            <span
              className={`
                ${styles.label}
                ${isActive ? styles.labelActive : ''}
                ${isCompleted ? styles.labelCompleted : ''}
              `}
            >
              {step.label}
            </span>
          </div>
        );
      })}
    </nav>
  );
}
