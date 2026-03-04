import { type ReactNode } from 'react';

interface GradientTextProps {
  children: ReactNode;
  className?: string;
  from?: string;
  via?: string;
  to?: string;
  animate?: boolean;
}

const GradientText: React.FC<GradientTextProps> = ({
  children,
  className = '',
  from = '#F39200',
  via = '#FFB84D',
  to = '#FF6B00',
  animate = true,
}) => {
  return (
    <span
      className={className}
      style={{
        background: `linear-gradient(135deg, ${from}, ${via}, ${to}, ${from})`,
        backgroundSize: animate ? '300% 300%' : '100% 100%',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
        animation: animate ? 'gradient-shift 4s ease infinite' : 'none',
      }}
    >
      <style>{`
        @keyframes gradient-shift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
      `}</style>
      {children}
    </span>
  );
};

export default GradientText;
