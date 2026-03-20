import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./MemberSelect.css";

interface Member {
  member_id: string;
  full_name: string;
}

export default function MemberSelect() {
  const [members, setMembers] = useState<Member[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:5000/api/members")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        return res.json();
      })
      .then((data: Member[]) => {
        setMembers(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const handleNavigate = () => {
    if (selectedId) navigate(`/member/${selectedId}`);
  };

  if (loading) return <p>Loading members...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="member-select-form">
      <select value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
        <option value="">-- Select a Member --</option>
        {members.map((m) => (
          <option key={m.member_id} value={m.member_id}>
            {m.full_name}
          </option>
        ))}
      </select>

      <button onClick={handleNavigate} disabled={!selectedId}>
        Get Member Info
      </button>
    </div>
  );
}