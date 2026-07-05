import { useEffect, useRef, useState } from 'react';

interface CountUpProps {
  to: number;
  from?: number;
  duration?: number;
  separator?: string;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
  onEnd?: () => void;
}

const CountUp: React.FC<CountUpProps> = ({
  to,
  from = 0,
  duration = 1500,
  separator = '.',
  decimals = 2,
  prefix = '',
  suffix = '',
  className = '',
  onEnd,
}) => {
  const [value, setValue] = useState(from);
  const ref = useRef<HTMLSpanElement>(null);

  // Anima al montar (sin esperar a entrar al viewport): en pantallas
  // pequeñas el resumen queda bajo el fold y el total se veía a 0,00 €
  useEffect(() => {
    let rafId = 0;
    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = from + (to - from) * eased;
      setValue(current);

      if (progress < 1) {
        rafId = requestAnimationFrame(animate);
      } else {
        setValue(to);
        onEnd?.();
      }
    };

    rafId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafId);
  }, [to, from, duration, onEnd]);

  const formatNumber = (num: number) => {
    const fixed = num.toFixed(decimals);
    const [intPart, decPart] = fixed.split('.');
    const withSeparator = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, separator);
    return decimals > 0 ? `${withSeparator},${decPart}` : withSeparator;
  };

  return (
    <span ref={ref} className={className}>
      {prefix}{formatNumber(value)}{suffix}
    </span>
  );
};

export default CountUp;
