import Recommendations from "./pages/recommendations";
import Chat from "./pages/chat";
import Goals from "./pages/goals";
import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Transactions from "./pages/Transactions";
import Anomalies from "./pages/Anomalies";
import Forecast from "./pages/Forecast";
import ProtectedRoute from "./components/ProtectedRoute";
import NavBar from "./components/NavBar";
import Persona from "./pages/persona";

function App() {
  return (
    <>
      <NavBar />

      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/transactions"
          element={
            <ProtectedRoute>
              <Transactions />
            </ProtectedRoute>
          }
        />

        <Route
          path="/anomalies"
          element={
            <ProtectedRoute>
              <Anomalies />
            </ProtectedRoute>
          }
        />

        <Route
          path="/forecast"
          element={
            <ProtectedRoute>
              <Forecast />
            </ProtectedRoute>
          }
        />
        <Route
          path="/goals"
          element={
            <ProtectedRoute>
              <Goals />
            </ProtectedRoute>
          }
        />
        <Route
          path="/persona"
          element={
            <ProtectedRoute>
              <Persona />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recommendations"
          element={
            <ProtectedRoute>
              <Recommendations />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;