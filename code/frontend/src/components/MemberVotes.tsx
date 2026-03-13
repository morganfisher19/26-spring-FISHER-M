import { useState, useEffect } from "react";

interface Member {
  member_id: string;
  full_name: string;
}

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
  const [members, setMembers] = useState<Member[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [memberDetail, setMemberDetail] = useState<MemberDetail | null>(null);
  const [loadingMembers, setLoadingMembers] = useState<boolean>(true);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch member list on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/members`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        return res.json();
      })
      .then((data: Member[]) => {
        setMembers(data);
        setLoadingMembers(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoadingMembers(false);
      });
  }, []);

  // Fetch member detail when selection changes
  useEffect(() => {
    if (!selectedId) {
      setMemberDetail(null);
      return;
    }

    setLoadingDetail(true);
    setError(null);

    fetch(`${API_BASE}/api/member/${selectedId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
        return res.json();
      })
      .then((data: MemberDetail) => {
        // Sort vote records most recent first
        data.vote_records.sort(
          (a, b) => new Date(b.vote_date).getTime() - new Date(a.vote_date).getTime()
        );
        setMemberDetail(data);
        setLoadingDetail(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoadingDetail(false);
      });
  }, [selectedId]);

  const formatDate = (isoString: string) =>
    new Date(isoString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });

  return (
    <div>
      {/* Member Select */}
      {loadingMembers ? (
        <p>Loading members...</p>
      ) : (
        <select value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
          <option value="">-- Select a Member --</option>
          {members.map((m) => (
            <option key={m.member_id} value={m.member_id}>
              {m.full_name}
            </option>
          ))}
        </select>
      )}

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {/* Vote Records */}
      {loadingDetail && <p>Loading votes...</p>}

      {memberDetail && !loadingDetail && (
        <div>
          <h2>{memberDetail.full_name}</h2>
          <p>
            {memberDetail.party} · {memberDetail.chamber === "H" ? "House" : "Senate"} · {memberDetail.state_name}
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
      )}
    </div>
  );
}