import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function NavBar() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  if (!isAuthenticated) return null;

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const linkStyle = {
    marginRight: "1rem",
    textDecoration: "none",
    color: "#ffffff",
    fontWeight: "500",
  };

  return (
    <nav
      style={{
        padding: "1rem",
        backgroundColor: "#324635",
        borderBottom: "1px solid #4b5f4f",
        fontFamily: "sans-serif",
      }}
    >
      <Link to="/" style={linkStyle}>
        Dashboard
      </Link>

      <Link to="/transactions" style={linkStyle}>
        Transactions
      </Link>

      <Link to="/anomalies" style={linkStyle}>
        Anomalies
      </Link>

      <Link to="/forecast" style={linkStyle}>
        Forecast
      </Link>

      <Link to="/goals" style={linkStyle}>
        Goals
      </Link>

      <Link to="/persona" style={linkStyle}>
        Persona
      </Link>

      <Link to="/chat" style={linkStyle}>
        Chat
      </Link>

      <Link to="/recommendations" style={linkStyle}>
        Recommendations
      </Link>

      <button
        onClick={handleLogout}
        style={{
          float: "right",
          padding: "0.4rem 0.8rem",
          borderRadius: "6px",
          border: "1px solid #ffffff",
          backgroundColor: "transparent",
          color: "#ffffff",
          cursor: "pointer",
        }}
      >
        Logout
      </button>
    </nav>
  );
}

export default NavBar;