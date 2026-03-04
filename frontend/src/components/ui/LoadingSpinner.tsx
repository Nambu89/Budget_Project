import styles from '../../styles/components/LoadingSpinner.module.css';

interface Props {
  text?: string;
}

export default function LoadingSpinner({ text = 'Cargando...' }: Props) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.spinner} />
      <p className={styles.text}>{text}</p>
    </div>
  );
}
