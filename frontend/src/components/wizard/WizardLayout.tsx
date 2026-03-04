import type { ReactNode } from 'react';
import WizardStepper from './WizardStepper';
import WizardNavigation from './WizardNavigation';
import AnimatedContent from '../reactbits/AnimatedContent';

interface Props {
  currentStep: number;
  onPrev: () => void;
  onNext: () => void;
  canNext?: boolean;
  nextLabel?: string;
  isLoading?: boolean;
  children: ReactNode;
}

export default function WizardLayout({
  currentStep,
  onPrev,
  onNext,
  canNext,
  nextLabel,
  isLoading,
  children,
}: Props) {
  return (
    <>
      <WizardStepper currentStep={currentStep} />
      <AnimatedContent key={currentStep} direction="up" duration={400}>
        {children}
      </AnimatedContent>
      <WizardNavigation
        currentStep={currentStep}
        onPrev={onPrev}
        onNext={onNext}
        canNext={canNext}
        nextLabel={nextLabel}
        isLoading={isLoading}
      />
    </>
  );
}
