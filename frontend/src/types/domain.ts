/* Enums del dominio — mirror de src/domain/enums/ */

export const PropertyType = {
  PISO: 'piso',
  VIVIENDA: 'vivienda',
  OFICINA: 'oficina',
  LOCAL: 'local',
} as const;
export type PropertyType = (typeof PropertyType)[keyof typeof PropertyType];

export const PROPERTY_TYPE_LABELS: Record<PropertyType, string> = {
  piso: 'Piso',
  vivienda: 'Vivienda independiente',
  oficina: 'Oficina',
  local: 'Local comercial',
};

export const QualityLevel = {
  BASICO: 'basico',
  ESTANDAR: 'estandar',
  PREMIUM: 'premium',
} as const;
export type QualityLevel = (typeof QualityLevel)[keyof typeof QualityLevel];

export const QUALITY_LABELS: Record<QualityLevel, string> = {
  basico: 'B\u00e1sico',
  estandar: 'Est\u00e1ndar',
  premium: 'Premium',
};

export const QUALITY_DESCRIPTIONS: Record<QualityLevel, string> = {
  basico: 'Materiales econ\u00f3micos de buena relaci\u00f3n calidad-precio. Ideal para inversiones o alquiler.',
  estandar: 'Materiales de calidad media-alta. Equilibrio perfecto entre precio y durabilidad.',
  premium: 'Materiales de alta gama y acabados de lujo. M\u00e1xima calidad y dise\u00f1o.',
};

export const PropertyState = {
  NUEVO: 'nuevo',
  NORMAL: 'normal',
  ANTIGUO: 'antiguo',
  RUINA: 'ruina',
} as const;
export type PropertyState = (typeof PropertyState)[keyof typeof PropertyState];

export const PROPERTY_STATE_LABELS: Record<PropertyState, string> = {
  nuevo: 'Nuevo / Buen estado',
  normal: 'Normal / Uso habitual',
  antiguo: 'Antiguo / Necesita mejoras',
  ruina: 'Ruinoso / Reforma integral',
};

export const WorkCategory = {
  ALBANILERIA: 'albanileria',
  FONTANERIA: 'fontaneria',
  ELECTRICIDAD: 'electricidad',
  CARPINTERIA: 'carpinteria',
  PAQUETE: 'paquete',
} as const;
export type WorkCategory = (typeof WorkCategory)[keyof typeof WorkCategory];

export const CATEGORY_LABELS: Record<string, string> = {
  albanileria: 'Alba\u00f1iler\u00eda',
  fontaneria: 'Ba\u00f1o',
  electricidad: 'Electricidad',
  carpinteria: 'Carpinter\u00eda',
  paquete: 'Paquete Completo',
};

export const CATEGORY_ICONS: Record<string, string> = {
  albanileria: '',
  fontaneria: '',
  electricidad: '',
  carpinteria: '',
  paquete: '',
};
