import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";


interface VoteRecord {
  vote_id: string;
  vote_date: string;
  bill_title: string;
  position: string;
}

interface MemberDetail {
  member_id: string;
  full_name: string;
  party: string;
  chamber: string;
  state_name: string;
  vote_records: VoteRecord[];
}

const API_BASE = "http://localhost:5000";

export default function MemberVotes() {
  const { memberId } = useParams<{ memberId: string }>();
  const navigate = useNavigate();
  const [memberDetail, setMemberDetail] = useState<MemberDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch member detail when selection changes
  useEffect(() => {
    if (!memberId) return;

    setLoading(true);
    setError(null);

    fetch(`${API_BASE}/api/member/${memberId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        return res.json();
      })
      .then((data: MemberDetail) => {
        data.vote_records.sort(
          (a, b) => new Date(b.vote_date).getTime() - new Date(a.vote_date).getTime()
        );
        setMemberDetail(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [memberId]);

  const formatDate = (isoString: string) =>
    new Date(isoString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });

  if (loading) return <p>Loading member profile...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!memberDetail) return <p>No member data found.</p>;

  return (
    <div>
      <button onClick={() => navigate(-1)}>← Back</button>

      <h2>{memberDetail.full_name}</h2>
      <p>
        {memberDetail.party} · {memberDetail.chamber === "H" ? "House" : "Senate"} ·{" "}
        {memberDetail.state_name}
      </p>

      {memberDetail.vote_records.length === 0 ? (
        <p>No vote records found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Bill Title</th>
              <th>Position</th>
            </tr>
          </thead>
          <tbody>
            {memberDetail.vote_records.map((vr) => (
              <tr key={vr.vote_id}>
                <td>{formatDate(vr.vote_date)}</td>
                <td>{vr.bill_title}</td>
                <td>{vr.position}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}