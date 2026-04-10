import { useParams, useNavigate } from "react-router-dom";
import { VISUALIZATIONS } from "./VizGallery";
import VizBipartisanship from "./visualizations/VizBipartisanship.tsx";
import VizBillSurvival from "./visualizations/VizBillSurvival.tsx";
import VizActivityOverTime from "./visualizations/VizActivityOverTime.tsx";
import VizTopInfluencers from "./visualizations/VizTopInfluencers.tsx";

const VIZ_COMPONENTS: Record<string, React.ComponentType> = {
  "bipartisanship":     VizBipartisanship,
  "bill-survival":      VizBillSurvival,
  "activity-over-time": VizActivityOverTime,
  "top-influencers":    VizTopInfluencers,
};


export default function VizDetail() {
  const { vizId } = useParams();

  const viz = VISUALIZATIONS.find((v) => v.id === vizId);

  if (!viz) {
    return (
      <div style={{ padding: "2rem" }}>
        <p>Visualization not found.</p>
      </div>
    );
  }

  const VizComponent = vizId ? VIZ_COMPONENTS[vizId] : null;

  return (
    <div style={{ padding: "2rem" }}>
      <h1>{viz.title}</h1>
      <p>{viz.description}</p>
      <div style={{ marginTop: "1.5rem" }}>
        {VizComponent ? (
          <VizComponent />
        ) : (
          <div
            style={{
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
        )}
      </div>
    </div>
  );
}