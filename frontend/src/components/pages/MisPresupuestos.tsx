import { useState, useEffect, useCallback } from 'react';
import { FileText, Download, Trash2, ArrowLeft, Loader2 } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { getMisPresupuestos, eliminarPresupuesto } from '../../api/presupuesto';
import { descargarPDF } from '../../api/presupuesto';
import AnimatedContent from '../reactbits/AnimatedContent';
import GlassCard from '../ui/GlassCard';
import SparkButton from '../ui/SparkButton';
import LoadingSpinner from '../ui/LoadingSpinner';
import type { UserBudgetResponse } from '../../types/api';
import styles from '../../styles/components/MisPresupuestos.module.css';
import stepStyles from '../../styles/components/Steps.module.css';

interface Props {
  onBack: () => void;
}

export default function MisPresupuestos({ onBack }: Props) {
  const { user } = useAuth();
  const [budgets, setBudgets] = useState<UserBudgetResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadBudgets = useCallback(async () => {
    if (!user) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await getMisPresupuestos(user.id);
      setBudgets(res.presupuestos);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar presupuestos');
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadBudgets();
  }, [loadBudgets]);

  const handleDownload = async (budget: UserBudgetResponse) => {
    setDownloadingId(budget.id);
    try {
      const proyecto = budget.datos_proyecto;
      const blob = await descargarPDF({
        cliente: {
          nombre: budget.cliente_nombre || '',
          email: budget.cliente_email || '',
          telefono: '',
          direccion_obra: '',
        },
        proyecto: {
          tipo_inmueble: (proyecto.tipo_inmueble as string) || 'piso',
          metros_cuadrados: (proyecto.metros_cuadrados as number) || 80,
          estado_actual: (proyecto.estado_actual as string) || 'normal',
          es_vivienda_habitual: (proyecto.es_vivienda_habitual as boolean) || false,
          calidad_general: (proyecto.calidad as string) || 'estandar',
        },
        trabajos: { paquetes: [], partidas: [] },
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `presupuesto_${budget.numero_presupuesto}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      setError('Error al descargar PDF');
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDelete = async (budget: UserBudgetResponse) => {
    if (!user) return;
    if (!confirm(`¿Eliminar presupuesto ${budget.numero_presupuesto}?`)) return;

    setDeletingId(budget.id);
    try {
      await eliminarPresupuesto(budget.id, user.id);
      setBudgets(prev => prev.filter(b => b.id !== budget.id));
    } catch {
      setError('Error al eliminar presupuesto');
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return '-';
    try {
      return new Date(dateStr).toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  };

  if (isLoading) {
    return <LoadingSpinner text="Cargando presupuestos..." />;
  }

  return (
    <section className={stepStyles.step}>
      <AnimatedContent direction="up" duration={400}>
        <div className={styles.headerRow}>
          <SparkButton variant="ghost" onClick={onBack}>
            <ArrowLeft size={18} /> Volver
          </SparkButton>
          <h2 className={stepStyles.stepTitle}>Mis Presupuestos</h2>
        </div>

        {error && (
          <div className={styles.error}>{error}</div>
        )}

        {budgets.length === 0 ? (
          <GlassCard className={styles.empty}>
            <FileText size={48} className={styles.emptyIcon} />
            <p className={styles.emptyText}>No tienes presupuestos guardados</p>
            <SparkButton onClick={onBack}>Crear mi primer presupuesto</SparkButton>
          </GlassCard>
        ) : (
          <div className={styles.list}>
            {budgets.map(budget => (
              <GlassCard key={budget.id} className={styles.card}>
                <div className={styles.cardHeader}>
                  <span className={styles.numero}>{budget.numero_presupuesto}</span>
                  <span className={styles.total}>{formatCurrency(budget.total_con_iva)}</span>
                </div>
                <div className={styles.cardBody}>
                  <div className={styles.meta}>
                    <span>Fecha: {formatDate(budget.fecha_creacion)}</span>
                    <span>Tipo: {(budget.datos_proyecto.tipo_inmueble as string || '-').toUpperCase()}</span>
                    <span>Superficie: {budget.datos_proyecto.metros_cuadrados as number || 0} m2</span>
                    <span>Partidas: {budget.partidas.length}</span>
                  </div>
                  {budget.cliente_nombre && (
                    <div className={styles.cliente}>
                      Cliente: {budget.cliente_nombre}
                    </div>
                  )}
                </div>
                <div className={styles.cardActions}>
                  <SparkButton
                    variant="secondary"
                    onClick={() => handleDownload(budget)}
                    disabled={downloadingId === budget.id}
                  >
                    {downloadingId === budget.id
                      ? <Loader2 size={16} className={styles.spin} />
                      : <Download size={16} />}
                    PDF
                  </SparkButton>
                  <SparkButton
                    variant="ghost"
                    onClick={() => handleDelete(budget)}
                    disabled={deletingId === budget.id}
                  >
                    {deletingId === budget.id
                      ? <Loader2 size={16} className={styles.spin} />
                      : <Trash2 size={16} />}
                    Eliminar
                  </SparkButton>
                </div>
              </GlassCard>
            ))}
          </div>
        )}
      </AnimatedContent>
    </section>
  );
}
