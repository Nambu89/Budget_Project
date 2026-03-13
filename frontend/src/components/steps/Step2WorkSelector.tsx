import { useState } from 'react';
import { useWizard } from '../../hooks/useWizard';
import { useCatalogos } from '../../hooks/useCatalogos';
import SplitText from '../reactbits/SplitText';
import PackageSelector from '../budget/PackageSelector';
import ItemSelector from '../budget/ItemSelector';
import WorkSummary from '../budget/WorkSummary';
import LoadingSpinner from '../ui/LoadingSpinner';
import styles from '../../styles/components/Steps.module.css';

export default function Step2WorkSelector() {
  const { state, dispatch } = useWizard();
  const { paquetes, categorias, isLoading, error } = useCatalogos();
  const [activeTab, setActiveTab] = useState<'paquetes' | 'partidas'>('paquetes');

  if (isLoading) return <LoadingSpinner text="Cargando catalogo..." />;

  if (error) {
    return (
      <section className={styles.step}>
        <div className={styles.errorBox}>Error cargando catalogo: {error}</div>
      </section>
    );
  }

  return (
    <section className={styles.step}>
      <SplitText
        text="Selecciona los trabajos"
        className={styles.stepTitle}
        delay={30}
      />
      <p className={styles.stepDesc}>
        Elige paquetes completos o partidas individuales para tu reforma. Los precios son sin IVA.
      </p>

      {/* Tabs */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'paquetes' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('paquetes')}
        >
          Paquetes Completos
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'partidas' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('partidas')}
        >
          Partidas Individuales
        </button>
      </div>

      {/* Contenido */}
      {activeTab === 'paquetes' ? (
        <PackageSelector
          paquetes={paquetes}
          selected={state.paquetes}
          calidad={state.proyecto.calidad_general}
          tipoInmueble={state.proyecto.tipo_inmueble}
          onAdd={p => dispatch({ type: 'ADD_PAQUETE', paquete: p })}
          onRemove={id => dispatch({ type: 'REMOVE_PAQUETE', id })}
        />
      ) : (
        <ItemSelector
          categorias={categorias}
          onAdd={p => dispatch({ type: 'ADD_PARTIDA', partida: p })}
        />
      )}

      {/* Resumen */}
      <WorkSummary
        paquetes={state.paquetes}
        partidas={state.partidas}
        onRemovePaquete={id => dispatch({ type: 'REMOVE_PAQUETE', id })}
        onRemovePartida={i => dispatch({ type: 'REMOVE_PARTIDA', index: i })}
      />
    </section>
  );
}
