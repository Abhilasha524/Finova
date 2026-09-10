import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Login() {
  const { login, isLoading, authError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      // authError is already set inside AuthContext - nothing extra needed here
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: "4rem auto", fontFamily: "sans-serif" }}>
      <h1>Log in</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "1rem" }}>
          <label>Email</label><br />
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <label>Password</label><br />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </div>
        {authError && <p style={{ color: "red" }}>{authError}</p>}
        <button type="submit" disabled={isLoading} style={{ width: "100%", padding: "0.6rem" }}>
          {isLoading ? "Logging in..." : "Log in"}
        </button>
      </form>
      <p style={{ marginTop: "1rem" }}>
        No account? <Link to="/register">Register</Link>
      </p>
    </div>
  );
}

export default Login;