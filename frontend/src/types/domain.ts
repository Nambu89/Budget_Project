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
  basico: 'Básico',
  estandar: 'Estándar',
  premium: 'Premium',
};

export const QUALITY_DESCRIPTIONS: Record<QualityLevel, string> = {
  basico: 'Materiales económicos de buena relación calidad-precio. Ideal para inversiones o alquiler.',
  estandar: 'Materiales de calidad media-alta. Equilibrio perfecto entre precio y durabilidad.',
  premium: 'Materiales de alta gama y acabados de lujo. Máxima calidad y diseño.',
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

/** Factores multiplicadores — mirror de src/domain/models/project.py */
export const ESTADO_FACTORS: Record<string, number> = {
  nuevo: 0.95,
  normal: 1.0,
  antiguo: 1.1,
  ruina: 1.25,
};

export const MOBILIARIO_FACTORS: Record<string, number> = {
  vacio: 1.0,
  parcial: 1.10,
  amueblado: 1.20,
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
  albanileria: 'Albañilería',
  fontaneria: 'Fontanería',
  electricidad: 'Electricidad',
  carpinteria: 'Carpintería',
  paquete: 'Paquete Completo',
};

export const CATEGORY_ICONS: Record<string, string> = {
  albanileria: '',
  fontaneria: '',
  electricidad: '',
  carpinteria: '',
  paquete: '',
};
