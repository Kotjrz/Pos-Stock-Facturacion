export const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL ?? "http://localhost:5000";

export interface LoginResponse {
  user: {
    id: number;
    username: string;
    rol: string | null;
    email: string | null;
  };
}

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type");
  const isJson = contentType?.includes("application/json");
  const body = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const message = isJson && body?.error ? body.error : response.statusText;
    throw new ApiError(response.status, message || "Unexpected error");
  }

  return body as T;
}

export async function login(
  username: string,
  password: string,
): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  return parseResponse<LoginResponse>(response);
}

export async function checkHealth(): Promise<{ status: string; database: string }> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  return parseResponse<{ status: string; database: string }>(response);
}

export { ApiError };
