import { useParams, useNavigate } from "react-router-dom";
import { VISUALIZATIONS } from "./VizGallery";

export default function VizDetail() {
  const { vizId } = useParams();
  const navigate = useNavigate();

  const viz = VISUALIZATIONS.find((v) => v.id === vizId);

  if (!viz) {
    return (
      <div style={{ padding: "2rem" }}>
        <p>Visualization not found.</p>
        <button onClick={() => navigate("/visualizations")}>← Back</button>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem" }}>
      <button onClick={() => navigate("/visualizations")} style={{ marginBottom: "1rem" }}>
        ← Back to Gallery
      </button>
      <h1>{viz.title}</h1>
      <p>{viz.description}</p>
      {/* Drop your interactive visualization component here */}
      <div
        style={{
          marginTop: "1.5rem",
          width: "100%",
          height: "500px",
          background: "#f0f0f0",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: "8px",
          color: "#999",
        }}
      >
        Visualization placeholder
      </div>
    </div>
  );
}