import { useNavigate } from "react-router-dom";
import "./VizGallery.css";

export const VISUALIZATIONS = [
  {
    id: "bill-survival",
    title: "How a Bill Survives Congress",
    description: "Placeholder description",
  },
  {
    id: "activity-over-time",
    title: "Congressional Activity Over Time",
    description: "Placeholder description",
  },
  {
    id: "bipartisanship",
    title: "Bipartisanship Within Congress",
    description: "Placeholder description",
  },
];

export default function VizGallery() {
  const navigate = useNavigate();

  return (
    <div className="viz-gallery-page">
      <h1>Data Visualizations</h1>
      <div className="viz-grid">
        {VISUALIZATIONS.map((viz) => (
          <div
            key={viz.id}
            className="viz-card"
            onClick={() => navigate(`/visualizations/${viz.id}`)}
          >
            <div className="viz-thumbnail">
              {/* Replace with <img src={viz.image} alt={viz.title} /> later */}
              <span className="viz-thumbnail-placeholder">Image</span>
            </div>
            <div className="viz-card-body">
              <h2>{viz.title}</h2>
              <p>{viz.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}