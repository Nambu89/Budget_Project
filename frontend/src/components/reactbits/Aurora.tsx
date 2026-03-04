interface AuroraProps {
  className?: string;
  color1?: string;
  color2?: string;
  color3?: string;
  opacity?: number;
}

const Aurora: React.FC<AuroraProps> = ({
  className = '',
  color1 = 'rgba(243,146,0,0.15)',
  color2 = 'rgba(255,107,0,0.1)',
  color3 = 'rgba(204,122,0,0.08)',
  opacity = 1,
}) => {
  return (
    <div
      className={className}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 0,
        opacity,
      }}
    >
      <div
        style={{
          position: 'absolute',
          width: '60vw',
          height: '60vw',
          borderRadius: '50%',
          background: `radial-gradient(circle, ${color1} 0%, transparent 70%)`,
          top: '-20%',
          left: '-10%',
          animation: 'aurora-float-1 12s ease-in-out infinite',
          filter: 'blur(60px)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          width: '50vw',
          height: '50vw',
          borderRadius: '50%',
          background: `radial-gradient(circle, ${color2} 0%, transparent 70%)`,
          bottom: '-20%',
          right: '-10%',
          animation: 'aurora-float-2 15s ease-in-out infinite',
          filter: 'blur(80px)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          width: '40vw',
          height: '40vw',
          borderRadius: '50%',
          background: `radial-gradient(circle, ${color3} 0%, transparent 70%)`,
          top: '30%',
          right: '20%',
          animation: 'aurora-float-3 18s ease-in-out infinite',
          filter: 'blur(70px)',
        }}
      />
      <style>{`
        @keyframes aurora-float-1 {
          0%, 100% { transform: translate(0, 0); }
          33% { transform: translate(5%, 3%); }
          66% { transform: translate(-3%, 5%); }
        }
        @keyframes aurora-float-2 {
          0%, 100% { transform: translate(0, 0); }
          33% { transform: translate(-4%, -3%); }
          66% { transform: translate(3%, -5%); }
        }
        @keyframes aurora-float-3 {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(-5%, 4%); }
        }
      `}</style>
    </div>
  );
};

export default Aurora;
