import { createContext, useContext, useState } from "react";
import { getToken, setToken as saveToken, clearToken } from "../api/token";
import { loginUser, registerUser } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(() => getToken());
  const [isLoading, setIsLoading] = useState(false);
  const [authError, setAuthError] = useState(null);

  const isAuthenticated = Boolean(token);

  async function login(email, password) {
    setIsLoading(true);
    setAuthError(null);
    try {
      const result = await loginUser(email, password);
      saveToken(result.access_token);
      setTokenState(result.access_token);
      return result;
    } catch (err) {
      setAuthError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }

  async function register(email, password) {
    setIsLoading(true);
    setAuthError(null);
    try {
      return await registerUser(email, password);
    } catch (err) {
      setAuthError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }

  function logout() {
    clearToken();
    setTokenState(null);
  }

  const value = { token, isAuthenticated, isLoading, authError, login, register, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return context;
}