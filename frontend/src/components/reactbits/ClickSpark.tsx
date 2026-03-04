import { useRef, type ReactNode, type MouseEvent } from 'react';

interface ClickSparkProps {
  children: ReactNode;
  sparkColor?: string;
  sparkCount?: number;
  sparkSize?: number;
}

const ClickSpark: React.FC<ClickSparkProps> = ({
  children,
  sparkColor = '#F39200',
  sparkCount = 8,
  sparkSize = 10,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const createSpark = (e: MouseEvent) => {
    const container = containerRef.current;
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    for (let i = 0; i < sparkCount; i++) {
      const spark = document.createElement('div');
      const angle = (360 / sparkCount) * i;
      const velocity = 30 + Math.random() * 30;

      Object.assign(spark.style, {
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        width: `${sparkSize}px`,
        height: `${sparkSize}px`,
        borderRadius: '50%',
        background: sparkColor,
        pointerEvents: 'none',
        zIndex: '9999',
        animation: `spark-fly 0.5s ease-out forwards`,
        '--angle': `${angle}deg`,
        '--velocity': `${velocity}px`,
      } as Record<string, string>);

      container.appendChild(spark);
      setTimeout(() => spark.remove(), 500);
    }
  };

  return (
    <div
      ref={containerRef}
      onClick={createSpark}
      style={{ position: 'relative', display: 'inline-block', overflow: 'visible' }}
    >
      <style>{`
        @keyframes spark-fly {
          0% { opacity: 1; transform: translate(0, 0) scale(1); }
          100% {
            opacity: 0;
            transform: translate(
              calc(cos(var(--angle)) * var(--velocity)),
              calc(sin(var(--angle)) * var(--velocity))
            ) scale(0);
          }
        }
      `}</style>
      {children}
    </div>
  );
};

export default ClickSpark;
