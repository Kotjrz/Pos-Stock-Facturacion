import { ChangeEvent, FormEvent, useEffect, useState } from "react";

import "./App.css";
import { ApiError, LoginResponse, checkHealth, login } from "./api";

type HealthState = "checking" | "ok" | "error";

type FormState = {
  username: string;
  password: string;
};

function App() {
  const [form, setForm] = useState<FormState>({ username: "", password: "" });
  const [healthState, setHealthState] = useState<HealthState>("checking");
  const [healthMessage, setHealthMessage] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<LoginResponse["user"] | null>(null);

  useEffect(() => {
    let isMounted = true;

    checkHealth()
      .then((result) => {
        if (!isMounted) return;
        if (result.status === "ok" && result.database === "ok") {
          setHealthState("ok");
          setHealthMessage("Base de datos conectada");
        } else {
          setHealthState("error");
          setHealthMessage("API respondió pero la base de datos no está disponible");
        }
      })
      .catch((err) => {
        if (!isMounted) return;
        setHealthState("error");
        setHealthMessage(err.message || "No se pudo verificar la API");
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (healthState !== "ok") {
      setError("La API no está disponible");
      return;
    }

    setLoading(true);
    setError(null);

    const username = form.username.trim();
    const password = form.password;

    if (!username || !password) {
      setError("Usuario y contraseña son obligatorios");
      setLoading(false);
      return;
    }

    try {
      const response = await login(username, password);
      setUser(response.user);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Ocurrió un error inesperado. Intenta nuevamente.");
      }
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <main className="login-card">
        <h1>Vivero - Acceso</h1>
        <p className="tagline">Inicia sesión para ingresar al panel de gestión.</p>

        <div
          className={`status-banner ${
            healthState === "ok" ? "status-ok" : healthState === "checking" ? "status-checking" : "status-error"
          }`}
        >
          {healthState === "checking" && "Verificando conexión..."}
          {healthState === "ok" && healthMessage}
          {healthState === "error" && healthMessage}
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <label htmlFor="username">Usuario</label>
          <input
            id="username"
            name="username"
            type="text"
            autoComplete="username"
            value={form.username}
            onChange={handleChange}
            placeholder="Ingresa tu usuario"
            disabled={loading}
            required
          />

          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={form.password}
            onChange={handleChange}
            placeholder="••••••••"
            disabled={loading}
            required
          />

          {error && <p className="feedback error">{error}</p>}
          {user && !error && (
            <div className="feedback success">
              <strong>¡Bienvenido, {user.username}!</strong>
              <span>Rol: {user.rol ?? "Sin rol"}</span>
              {user.email && <span>Email: {user.email}</span>}
            </div>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;
