import { useState, useEffect } from "react";

interface Member {
  member_id: string;
  full_name: string;
}

interface MemberSelectProps {
  onSelect?: (memberId: string) => void;
}

export default function MemberSelect({ onSelect }: MemberSelectProps) {
  const [members, setMembers] = useState<Member[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelected(val);
    onSelect?.(val);
  };

  if (loading) return <p>Loading members...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <select value={selected} onChange={handleChange}>
      <option value="">-- Select a Member --</option>
      {members.map((m) => (
        <option key={m.member_id} value={m.member_id}>
          {m.full_name}
        </option>
      ))}
    </select>
  );
}