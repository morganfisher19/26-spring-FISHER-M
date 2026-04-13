import { useParams, useNavigate } from "react-router-dom";
import { VISUALIZATIONS } from "./VizGallery";
import VizBipartisanship from "./visualizations/VizBipartisanship.tsx";
import VizBillSurvival from "./visualizations/VizBillSurvival.tsx";
import VizActivityOverTime from "./visualizations/VizActivityOverTime.tsx";
import VizTopInfluencers from "./visualizations/VizTopInfluencers.tsx";
import "./VizDetail.css";

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
    <div className='viz-container'>
      <h1>{viz.title}</h1>
      <p>{viz.description}</p>
      <div className='viz-wrapper'>
        {VizComponent ? (
          <VizComponent />
        ) : (
          <div className='viz-placeholder'>
            Visualization placeholder
          </div>
        )}
      </div>
    </div>
  );
}