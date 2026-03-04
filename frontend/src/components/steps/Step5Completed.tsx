import { useState, useEffect, useRef, useCallback } from 'react';
import { CheckCircle, Download, Mail, RefreshCw, Loader2 } from 'lucide-react';
import { useWizard } from '../../hooks/useWizard';
import { useAuth } from '../../hooks/useAuth';
import { descargarPDF, guardarPresupuesto } from '../../api/presupuesto';
import { enviarPresupuesto } from '../../api/email';
import SplitText from '../reactbits/SplitText';
import AnimatedContent from '../reactbits/AnimatedContent';
import EconomicSummary from '../budget/EconomicSummary';
import GlassCard from '../ui/GlassCard';
import SparkButton from '../ui/SparkButton';
import Modal from '../ui/Modal';
import styles from '../../styles/components/Steps.module.css';
import completedStyles from '../../styles/components/Completed.module.css';
import type { GenerarPDFRequest } from '../../types/api';

export default function Step5Completed() {
  const { state, dispatch } = useWizard();
  const { user, isAuthenticated } = useAuth();

  const [isDownloading, setIsDownloading] = useState(false);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailTo, setEmailTo] = useState(state.cliente.email || '');
  const [emailMsg, setEmailMsg] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const savedRef = useRef(false);

  // Auto-guardar presupuesto si el usuario esta autenticado
  useEffect(() => {
    if (!isAuthenticated || !user || savedRef.current) return;
    if (!state.presupuesto) return;

    savedRef.current = true;
    guardarPresupuesto({
      user_id: user.id,
      cliente: state.cliente,
      proyecto: state.proyecto,
      trabajos: { paquetes: state.paquetes, partidas: state.partidas },
    }).catch(() => {
      // Silencioso — el guardado es secundario
    });
  }, [isAuthenticated, user, state.presupuesto, state.cliente, state.proyecto, state.paquetes, state.partidas]);

  const buildPdfRequest = useCallback((): GenerarPDFRequest => ({
    cliente: state.cliente,
    proyecto: state.proyecto,
    trabajos: { paquetes: state.paquetes, partidas: state.partidas },
  }), [state.cliente, state.proyecto, state.paquetes, state.partidas]);

  const handleDownloadPDF = async () => {
    setIsDownloading(true);
    setFeedback(null);
    try {
      const blob = await descargarPDF(buildPdfRequest());
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `presupuesto_${state.presupuesto?.numero || 'reforma'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setFeedback({ type: 'success', text: 'PDF descargado correctamente' });
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al generar PDF';
      setFeedback({ type: 'error', text: msg });
    } finally {
      setIsDownloading(false);
    }
  };

  const handleSendEmail = async () => {
    if (!emailTo) return;
    setIsSendingEmail(true);
    setFeedback(null);
    try {
      // Generar PDF primero
      const pdfBlob = await descargarPDF(buildPdfRequest());

      // Enviar email con PDF adjunto
      const datosPresupuesto = {
        numero: state.presupuesto?.numero,
        total: state.presupuesto?.total,
        fecha_emision: state.presupuesto?.fecha_emision,
        cliente_nombre: state.cliente.nombre,
      };
      await enviarPresupuesto(emailTo, pdfBlob, datosPresupuesto, emailMsg || undefined);
      setFeedback({ type: 'success', text: `Presupuesto enviado a ${emailTo}` });
      setShowEmailModal(false);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al enviar email';
      setFeedback({ type: 'error', text: msg });
    } finally {
      setIsSendingEmail(false);
    }
  };

  const handleNewBudget = () => {
    dispatch({ type: 'RESET' });
  };

  return (
    <section className={styles.step}>
      <AnimatedContent direction="up" duration={600}>
        <div className={completedStyles.hero}>
          <CheckCircle size={56} className={completedStyles.checkIcon} />
          <SplitText
            text="Presupuesto completado"
            className={styles.stepTitle}
            delay={40}
          />
          <p className={styles.stepDesc}>
            Tu presupuesto ha sido generado correctamente.
          </p>
        </div>
      </AnimatedContent>

      {state.presupuesto && (
        <EconomicSummary presupuesto={state.presupuesto} />
      )}

      {feedback && (
        <div className={`${completedStyles.feedback} ${completedStyles[feedback.type]}`}>
          {feedback.text}
        </div>
      )}

      <GlassCard className={completedStyles.actions}>
        <h4 className={completedStyles.actionsTitle}>Acciones disponibles</h4>

        <div className={completedStyles.btnGrid}>
          <SparkButton onClick={handleDownloadPDF} disabled={isDownloading}>
            {isDownloading ? <Loader2 size={18} className={completedStyles.spin} /> : <Download size={18} />}
            {isDownloading ? 'Generando...' : 'Descargar PDF'}
          </SparkButton>
          <SparkButton variant="secondary" onClick={() => setShowEmailModal(true)} disabled={isSendingEmail}>
            <Mail size={18} /> Enviar por email
          </SparkButton>
          <SparkButton variant="ghost" onClick={handleNewBudget}>
            <RefreshCw size={18} /> Nuevo presupuesto
          </SparkButton>
        </div>
      </GlassCard>

      <Modal
        isOpen={showEmailModal}
        onClose={() => setShowEmailModal(false)}
        title="Enviar presupuesto por email"
      >
        <div className={completedStyles.emailForm}>
          <label className={completedStyles.label}>
            Email destinatario
            <input
              type="email"
              value={emailTo}
              onChange={e => setEmailTo(e.target.value)}
              placeholder="cliente@email.com"
              className={completedStyles.input}
            />
          </label>
          <label className={completedStyles.label}>
            Mensaje personalizado (opcional)
            <textarea
              value={emailMsg}
              onChange={e => setEmailMsg(e.target.value)}
              placeholder="Adjunto el presupuesto solicitado..."
              className={completedStyles.textarea}
              rows={3}
            />
          </label>
          <div className={completedStyles.modalActions}>
            <SparkButton variant="ghost" onClick={() => setShowEmailModal(false)}>
              Cancelar
            </SparkButton>
            <SparkButton onClick={handleSendEmail} disabled={!emailTo || isSendingEmail}>
              {isSendingEmail ? <Loader2 size={18} className={completedStyles.spin} /> : <Mail size={18} />}
              {isSendingEmail ? 'Enviando...' : 'Enviar ahora'}
            </SparkButton>
          </div>
        </div>
      </Modal>
    </section>
  );
}
