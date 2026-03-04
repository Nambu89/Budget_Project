import { apiFetch } from './client';
import { ENDPOINTS } from '../config/api';
import type { EnviarEmailResponse } from '../types/api';

export async function enviarPresupuesto(
  emailDestinatario: string,
  pdfBlob: Blob,
  datosPresupuesto: Record<string, unknown>,
  mensajePersonalizado?: string
): Promise<EnviarEmailResponse> {
  // Convertir blob a base64 para enviar como string
  const arrayBuffer = await pdfBlob.arrayBuffer();
  const bytes = new Uint8Array(arrayBuffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  const pdfBase64 = btoa(binary);

  return apiFetch<EnviarEmailResponse>(ENDPOINTS.email.enviar, {
    method: 'POST',
    body: JSON.stringify({
      email_destinatario: emailDestinatario,
      pdf_bytes: pdfBase64,
      datos_presupuesto: datosPresupuesto,
      mensaje_personalizado: mensajePersonalizado,
    }),
  });
}
