import { useState, useEffect } from 'react';
import { KeyRound, CheckCircle, AlertCircle } from 'lucide-react';
import { verifyResetToken, resetPassword } from '../../api/auth';
import AnimatedContent from '../reactbits/AnimatedContent';
import GlassCard from '../ui/GlassCard';
import SparkButton from '../ui/SparkButton';
import LoadingSpinner from '../ui/LoadingSpinner';
import styles from '../../styles/components/ResetPassword.module.css';
import stepStyles from '../../styles/components/Steps.module.css';

interface Props {
  token: string;
  onBack: () => void;
}

type Status = 'verifying' | 'invalid' | 'form' | 'success';

export default function ResetPassword({ token, onBack }: Props) {
  const [status, setStatus] = useState<Status>('verifying');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!token) {
      setStatus('invalid');
      return;
    }

    verifyResetToken(token)
      .then(res => {
        if (res.valid) {
          setEmail(res.email || '');
          setStatus('form');
        } else {
          setStatus('invalid');
        }
      })
      .catch(() => {
        setStatus('invalid');
      });
  }, [token]);

  const handleSubmit = async () => {
    setError(null);

    if (password.length < 6) {
      setError('La contrasena debe tener al menos 6 caracteres');
      return;
    }
    if (password !== confirmPassword) {
      setError('Las contrasenas no coinciden');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await resetPassword(token, password);
      if (res.success) {
        setStatus('success');
      } else {
        setError(res.message || 'Error al cambiar contrasena');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cambiar contrasena');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (status === 'verifying') {
    return <LoadingSpinner text="Verificando enlace..." />;
  }

  return (
    <section className={stepStyles.step}>
      <AnimatedContent direction="up" duration={400}>
        {status === 'invalid' && (
          <GlassCard className={styles.card}>
            <AlertCircle size={48} className={styles.errorIcon} />
            <h2 className={stepStyles.stepTitle}>Enlace no valido</h2>
            <p className={styles.desc}>
              Este enlace de recuperacion ha expirado o ya fue utilizado.
            </p>
            <SparkButton onClick={onBack}>Volver al inicio</SparkButton>
          </GlassCard>
        )}

        {status === 'form' && (
          <GlassCard className={styles.card}>
            <KeyRound size={48} className={styles.keyIcon} />
            <h2 className={stepStyles.stepTitle}>Nueva contrasena</h2>
            {email && (
              <p className={styles.desc}>Cambiando contrasena para {email}</p>
            )}

            {error && <div className={styles.error}>{error}</div>}

            <div className={styles.form}>
              <label className={styles.label}>
                Nueva contrasena
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Minimo 6 caracteres"
                  className={styles.input}
                  minLength={6}
                />
              </label>
              <label className={styles.label}>
                Confirmar contrasena
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={e => setConfirmPassword(e.target.value)}
                  placeholder="Repite la contrasena"
                  className={styles.input}
                />
              </label>
              <SparkButton
                onClick={handleSubmit}
                disabled={isSubmitting || !password || !confirmPassword}
              >
                {isSubmitting ? 'Cambiando...' : 'Cambiar contrasena'}
              </SparkButton>
            </div>
          </GlassCard>
        )}

        {status === 'success' && (
          <GlassCard className={styles.card}>
            <CheckCircle size={48} className={styles.successIcon} />
            <h2 className={stepStyles.stepTitle}>Contrasena cambiada</h2>
            <p className={styles.desc}>
              Tu contrasena ha sido actualizada correctamente. Ya puedes iniciar sesion.
            </p>
            <SparkButton onClick={onBack}>Ir al inicio</SparkButton>
          </GlassCard>
        )}
      </AnimatedContent>
    </section>
  );
}
