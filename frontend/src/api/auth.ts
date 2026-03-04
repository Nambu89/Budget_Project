import { apiFetch } from './client';
import { ENDPOINTS } from '../config/api';
import type {
  RegisterRequest,
  LoginRequest,
  AuthResponse,
  UserResponse,
} from '../types/api';

export async function register(data: RegisterRequest): Promise<AuthResponse> {
  return apiFetch<AuthResponse>(ENDPOINTS.auth.register, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  return apiFetch<AuthResponse>(ENDPOINTS.auth.login, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getMe(email: string): Promise<UserResponse> {
  return apiFetch<UserResponse>(`${ENDPOINTS.auth.me}?email=${encodeURIComponent(email)}`);
}

export async function requestPasswordReset(
  email: string
): Promise<{ message: string; success: boolean }> {
  return apiFetch<{ message: string; success: boolean }>(
    ENDPOINTS.auth.requestPasswordReset,
    {
      method: 'POST',
      body: JSON.stringify({ email }),
    }
  );
}

export async function verifyResetToken(
  token: string
): Promise<{ valid: boolean; email?: string; nombre?: string }> {
  return apiFetch<{ valid: boolean; email?: string; nombre?: string }>(
    ENDPOINTS.auth.verifyResetToken(token)
  );
}

export async function resetPassword(
  token: string,
  newPassword: string
): Promise<{ message: string; success: boolean }> {
  return apiFetch<{ message: string; success: boolean }>(
    ENDPOINTS.auth.resetPassword,
    {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    }
  );
}
