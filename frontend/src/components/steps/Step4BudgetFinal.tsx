import { useState, useEffect, useCallback } from 'react';
import { Download, Mail, MessageCircle, RefreshCw, Loader2 } from 'lucide-react';
import { useWizard } from '../../hooks/useWizard';
import { calcularPresupuesto, descargarPDF } from '../../api/presupuesto';
import { enviarPresupuesto } from '../../api/email';
import SplitText from '../reactbits/SplitText';
import BudgetBreakdown from '../budget/BudgetBreakdown';
import EconomicSummary from '../budget/EconomicSummary';
import GlassCard from '../ui/GlassCard';
import SparkButton from '../ui/SparkButton';
import Modal from '../ui/Modal';
import LoadingSpinner from '../ui/LoadingSpinner';
import styles from '../../styles/components/Steps.module.css';
import completedStyles from '../../styles/components/Completed.module.css';
import type { GenerarPDFRequest } from '../../types/api';

const WHATSAPP_PHONE = '34636155847';

export default function Step4BudgetFinal() {
  const { state, dispatch } = useWizard();

  const [isDownloading, setIsDownloading] = useState(false);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailTo, setEmailTo] = useState(state.cliente.email || '');
  const [emailMsg, setEmailMsg] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Calcular presupuesto al montar
  useEffect(() => {
    if (state.presupuesto || state.isCalculating) return;

    const calculate = async () => {
      dispatch({ type: 'SET_CALCULATING', value: true });
      try {
        const res = await calcularPresupuesto({
          proyecto: state.proyecto,
          trabajos: {
            paquetes: state.paquetes,
            partidas: state.partidas,
          },
        });
        dispatch({ type: 'SET_PRESUPUESTO', presupuesto: res });
      } catch (err) {
        dispatch({
          type: 'SET_ERROR',
          error: err instanceof Error ? err.message : 'Error calculando presupuesto',
        });
      }
    };

    calculate();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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
      const pdfBlob = await descargarPDF(buildPdfRequest());
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

  const handleSendWhatsApp = () => {
    const total = state.presupuesto?.total?.toFixed(2) || '0';
    const numero = state.presupuesto?.numero || '';
    const nombre = state.cliente.nombre || 'Cliente';
    const texto = encodeURIComponent(
      `Hola, soy ${nombre}. He generado el presupuesto ${numero} con un total de ${total}\u20ac (IVA incluido). Me gustar\u00eda recibir m\u00e1s informaci\u00f3n.`
    );
    window.open(`https://wa.me/${WHATSAPP_PHONE}?text=${texto}`, '_blank');
  };

  const handleNewBudget = () => {
    dispatch({ type: 'RESET' });
  };

  if (state.isCalculating) {
    return <LoadingSpinner text="Calculando tu presupuesto..." />;
  }

  if (state.error) {
    return (
      <section className={styles.step}>
        <div className={styles.errorBox}>{state.error}</div>
      </section>
    );
  }

  if (!state.presupuesto) return null;

  return (
    <section className={styles.step}>
      <SplitText
        text="Tu presupuesto"
        className={styles.stepTitle}
        delay={30}
      />
      <p className={styles.stepDesc}>
        Aqu\u00ed tienes el desglose completo de tu presupuesto de reforma.
      </p>

      <BudgetBreakdown partidas={state.presupuesto.partidas} />
      <EconomicSummary presupuesto={state.presupuesto} />

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
          <SparkButton variant="secondary" onClick={handleSendWhatsApp}>
            <MessageCircle size={18} /> Enviar por WhatsApp
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
