import { type ReactNode } from 'react';

interface ShinyTextProps {
  children: ReactNode;
  className?: string;
  speed?: number;
  color?: string;
}

const ShinyText: React.FC<ShinyTextProps> = ({
  children,
  className = '',
  speed = 3,
  color = 'rgba(255,255,255,0.3)',
}) => {
  return (
    <span
      className={className}
      style={{
        position: 'relative',
        display: 'inline-block',
        overflow: 'hidden',
      }}
    >
      {children}
      <span
        style={{
          position: 'absolute',
          top: 0,
          left: '-100%',
          width: '60%',
          height: '100%',
          background: `linear-gradient(90deg, transparent, ${color}, transparent)`,
          animation: `shiny-slide ${speed}s ease-in-out infinite`,
        }}
      />
      <style>{`
        @keyframes shiny-slide {
          0% { left: -100%; }
          50%, 100% { left: 150%; }
        }
      `}</style>
    </span>
  );
};

export default ShinyText;
