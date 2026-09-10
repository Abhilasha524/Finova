import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Register() {
  const { register, isLoading, authError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setSuccessMessage("");
    try {
      await register(email, password);
      setSuccessMessage("Account created. Redirecting to login...");
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      // authError is already set inside AuthContext - nothing extra needed here
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: "4rem auto", fontFamily: "sans-serif" }}>
      <h1>Register</h1>
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
            minLength={6}
            style={{ width: "100%", padding: "0.5rem" }}
          />
        </div>
        {authError && <p style={{ color: "red" }}>{authError}</p>}
        {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}
        <button type="submit" disabled={isLoading} style={{ width: "100%", padding: "0.6rem" }}>
          {isLoading ? "Creating account..." : "Register"}
        </button>
      </form>
      <p style={{ marginTop: "1rem" }}>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}

export default Register;