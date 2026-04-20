import { useNavigate } from "react-router-dom";
import "./VizGallery.css";

export const VISUALIZATIONS = [
    {
    id: "bipartisanship",
    title: "Bipartisanship In Congress",
    description: "How often do the parties agree with one another?",
    image: "../../images/bipartisan-cover.png",
  },
  {
    id: "bill-survival",
    title: "How a Bill Survives Congress",
    description: "How many bills actually become law?",
    image: "../../images/bill-funnel-cover.png",

  },
  {
    id: "activity-over-time",
    title: "Congressional Activity Over Time",
    description: "When are members voting the most?",
    image: "../../images/activity-cover.png",

  },
  { id: "top-influencers",
    title: "Top Influencers in Congress",
    description: "Which members have the most influence in Congress?",
    image: "../../images/top-influencers-cover.png",
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
              <img src={viz.image} alt={viz.title} />
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