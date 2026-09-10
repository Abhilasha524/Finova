function StatCard({ label, value, color }) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 8,
        padding: "1rem",
        flex: 1,
        minWidth: 180,
      }}
    >
      <p style={{ margin: 0, color: "#666", fontSize: "0.9rem" }}>{label}</p>
      <p style={{ margin: "0.4rem 0 0", fontSize: "1.5rem", fontWeight: 600, color: color || "#222" }}>
        {value}
      </p>
    </div>
  );
}

export default StatCard;