import { useEffect, useRef, useState } from 'react';

interface SplitTextProps {
  text: string;
  className?: string;
  delay?: number;
  animationFrom?: React.CSSProperties;
  animationTo?: React.CSSProperties;
  threshold?: number;
  rootMargin?: string;
  onLetterAnimationComplete?: () => void;
}

const SplitText: React.FC<SplitTextProps> = ({
  text,
  className = '',
  delay = 50,
  animationFrom = { opacity: 0, transform: 'translateY(20px)' },
  animationTo = { opacity: 1, transform: 'translateY(0)' },
  threshold = 0.1,
  rootMargin = '-50px',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold, rootMargin }
    );

    if (containerRef.current) observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  const words = text.split(' ');

  return (
    <div ref={containerRef} className={className} style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3em' }}>
      {words.map((word, wIdx) => (
        <span key={wIdx} style={{ display: 'inline-flex' }}>
          {word.split('').map((char, cIdx) => {
            const globalIdx = words.slice(0, wIdx).join(' ').length + cIdx + (wIdx > 0 ? 1 : 0);
            return (
              <span
                key={cIdx}
                style={{
                  display: 'inline-block',
                  transition: `all 0.4s ease ${globalIdx * delay}ms`,
                  ...(isVisible ? animationTo : animationFrom),
                }}
              >
                {char}
              </span>
            );
          })}
        </span>
      ))}
    </div>
  );
};

export default SplitText;
