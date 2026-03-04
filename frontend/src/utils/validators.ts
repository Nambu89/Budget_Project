/** Valida formato de email */
export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/** Valida telefono espanol (9 digitos, empieza por 6, 7 o 9) */
export function isValidPhone(phone: string): boolean {
  const digits = phone.replace(/\D/g, '');
  return /^[679]\d{8}$/.test(digits);
}

/** Valida que la contrasena tenga minimo 6 caracteres */
export function isValidPassword(password: string): boolean {
  return password.length >= 6;
}

/** Valida que un campo no este vacio */
export function isRequired(value: string): boolean {
  return value.trim().length > 0;
}
