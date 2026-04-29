import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./MemberSelect.css";

interface Member {
  member_id: string;
  full_name: string;
  first_name: string;
  last_name: string;
  party: string;
  chamber: string;
  state_name: string;
  district: string;
}


function formatMember(m: Member): string {
  // Convert "Last, First" → "First Last"
  const [last, first] = m.full_name.split(",").map((s) => s.trim());
  const name = first && last ? `${first} ${last}` : m.full_name;

  const base = `${name} (${m.party}-${m.state_name}`;
  return m.chamber === "H"
    ? `${base}-${m.district})`
    : `${base})`;
}

export default function MemberSelect() {
  const [members, setMembers] = useState<Member[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/api/members")
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

  const handleSelect = (m: Member) => {
    setSelectedId(m.member_id);
    setSearchTerm(formatMember(m));
    setIsOpen(false);
  };

  const filteredMembers = members.filter((m) =>
    formatMember(m).toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleNavigate = () => {
    if (selectedId) navigate(`/member/${selectedId}`);
  };

  if (loading) return <p>Loading members...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="member-select-form">
      <div className="dropdown">
        <input
          type="text"
          placeholder="-- Select a Member --"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
        />

        {isOpen && (
          <ul className="dropdown-list">
            {filteredMembers.length > 0 ? (
              filteredMembers.map((m) => (
                <li
                  key={m.member_id}
                  onClick={() => handleSelect(m)}
                >
                  {formatMember(m)}
                </li>
              ))
            ) : (
              <li className="no-results">No results</li>
            )}
          </ul>
        )}
      </div>

      <button onClick={handleNavigate} disabled={!selectedId}>
        Get Member Info
      </button>

      <a
        href="https://www.house.gov/representatives/find-your-representative"
        target="_blank"
        rel="noopener noreferrer"
        className="externalLink"
      >
        Find your representative by zip code
      </a>
    </div>
  );
}