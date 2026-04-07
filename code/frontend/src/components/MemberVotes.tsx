import { useState, useEffect, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./MemberVotes.css";


interface VoteRecord {
  vote_id: string;
  vote_date: string;
  bill_title: string;
  bill_type: string;
  bill_num: number;
  question: string;
  position: string;
  policy_area: string | null;
  became_law: boolean; 
}

interface Sponsorship {
  bill_id: string;
  sponsor_type: string;
  bill_title: string | null;
  bill_type: string | null;
  bill_num: number | null;
  policy_area: string | null;
  became_law: boolean; 
}


interface MemberDetail {
  member_id: string;
  full_name: string;
  party: string;
  chamber: string;
  state_name: string;
  vote_records: VoteRecord[];
}

type Tab = "votes" | "sponsored" | "cosponsored";

const API_BASE = "http://localhost:5000";

const BILL_TYPE_MAP: Record<string, string> = {
  HR:      "house-bill",
  S:       "senate-bill",
  HRES:    "house-resolution",
  SRES:    "senate-resolution",
  HJRES:   "house-joint-resolution",
  SJRES:   "senate-joint-resolution",
  HCONRES: "house-concurrent-resolution",
  SCONRES: "senate-concurrent-resolution",
};

function formatDisplayName(fullName: string): string {
  const [last, first] = fullName.split(",").map((s) => s.trim());
  return first && last ? `${first} ${last}` : fullName;
}

function buildCongressUrl(billType: string | null, billNum: number | null): string | null {
  if (!billType || !billNum) return null;
  const slug = BILL_TYPE_MAP[billType];
  if (!slug) return null;
  return `https://www.congress.gov/bill/119th-congress/${slug}/${billNum}`;
}

function BillLink({ title, billType, billNum }: { title: string | null; billType: string | null; billNum: number | null }) {
  const url = buildCongressUrl(billType, billNum);
  if (!title) return <span>—</span>;
  return url
    ? <a className="billLink" href={url} target="_blank" rel="noopener noreferrer">{title}</a>
    : <span>{title}</span>;
}

function LawBadge({ became_law }: { became_law: boolean }) {
  if (!became_law) return null;
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem", marginLeft: "0.5rem" }}>
      <span style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "green", display: "inline-block" }} />
      <span style={{ color: "green", fontSize: "0.85em" }}>Passed into law</span>
    </span>
  );
}

export default function MemberVotes() {
  const { memberId } = useParams<{ memberId: string }>();
  const [memberDetail, setMemberDetail] = useState<MemberDetail | null>(null);
  const [sponsorships, setSponsorships] = useState<Sponsorship[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedArea, setSelectedArea] = useState<string>("All Areas");
  const [activeTab, setActiveTab] = useState<Tab>("votes");
  const [lawFilter, setLawFilter] = useState<boolean>(false);
  


  // Fetch member detail when selection changes
  useEffect(() => {
    if (!memberId) return;

    setLoading(true);
    setError(null);
    setSelectedArea("All Areas");
    setActiveTab("votes");

    Promise.all([
      fetch(`${API_BASE}/api/member/${memberId}`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
      fetch(`${API_BASE}/api/member/${memberId}/sponsorships`).then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }),
    ])
      .then(([memberData, sponsorshipData]: [MemberDetail, Sponsorship[]]) => {
        memberData.vote_records.sort(
          (a, b) => new Date(b.vote_date).getTime() - new Date(a.vote_date).getTime()
        );
        setMemberDetail(memberData);
        setSponsorships(sponsorshipData);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [memberId]);
  
  const policyAreas = useMemo(() => {
    if (!memberDetail) return [];
    const areas = new Set(
      memberDetail.vote_records
        .map((vr) => vr.policy_area)
        .filter((a): a is string => a !== null && a !== undefined && a !== "")
    );
    return Array.from(areas).sort();
  }, [memberDetail]);

  const filteredVotes = useMemo(() => {
    if (!memberDetail) return [];
    return memberDetail.vote_records.filter(vr => {
      const areaMatch = selectedArea === "All Areas" || vr.policy_area === selectedArea;
      const lawMatch = !lawFilter || vr.became_law;
      return areaMatch && lawMatch;
    });
  }, [memberDetail, selectedArea, lawFilter]);

  const filteredSponsored = useMemo(() => {
    return sponsorships.filter(s => {
      const areaMatch = selectedArea === "All Areas" || s.policy_area === selectedArea;
      const lawMatch = !lawFilter || s.became_law;
      return s.sponsor_type === "S" && areaMatch && lawMatch;
    });
  }, [sponsorships, selectedArea, lawFilter]);

  const filteredCosponsored = useMemo(() => {
    return sponsorships.filter(s => {
      const areaMatch = selectedArea === "All Areas" || s.policy_area === selectedArea;
      const lawMatch = !lawFilter || s.became_law;
      return s.sponsor_type === "C" && areaMatch && lawMatch;
    });
  }, [sponsorships, selectedArea, lawFilter]);

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
      <section className="memberInfo">
        <img
          src={`/images/member_images/${memberDetail.member_id}.jpg`}
          alt={formatDisplayName(memberDetail.full_name)}
          onError={e => { (e.currentTarget as HTMLImageElement).style.display = "none"; }}
          className="memberAvatar"
        />
        <div>
          <h2>{formatDisplayName(memberDetail.full_name)}</h2>
          <p className="memberMeta">
            {memberDetail.party} · {memberDetail.chamber === "H" ? "House" : "Senate"} · {memberDetail.state_name}
          </p>
        </div>
      </section>

      <section className="filter">
        <label htmlFor="policy-area-filter">Policy Area:</label>
        <select
          id="policy-area-filter"
          value={selectedArea}
          onChange={e => setSelectedArea(e.target.value)}
        >
          <option value="All Areas">All Areas</option>
          {policyAreas.map(area => (
            <option key={area} value={area}>{area}</option>
          ))}
        </select>

        <label className="checkboxLabel">
          <input
            type="checkbox"
            checked={lawFilter}
            onChange={e => setLawFilter(e.target.checked)}
          />
          Passed into law
        </label>
      </section>

      <section className="tabs">
        <div className="tabButtons">
          {(["votes", "sponsored", "cosponsored"] as Tab[]).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={activeTab === tab ? "tabBtn active" : "tabBtn"}
            >
              {tab === "votes" ? `Voting Records (${filteredVotes.length})`
                : tab === "sponsored" ? `Sponsored Bills (${filteredSponsored.length})`
                : `Cosponsored Bills (${filteredCosponsored.length})`}
            </button>
          ))}
        </div>
      </section>

      <section className="tabContent">
        {/* Tab content */}
        {activeTab === "votes" && (
          filteredVotes.length === 0 ? <p>No vote records found.</p> : (
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Bill Title</th>
                  <th>Position</th>
                </tr>
              </thead>
              <tbody>
                {filteredVotes.map(vr => (
                  <tr key={vr.vote_id}>
                    <td>{formatDate(vr.vote_date)}</td>
                    <td>
                      <BillLink title={vr.bill_title} billType={vr.bill_type} billNum={vr.bill_num} />
                      <LawBadge became_law={vr.became_law} />
                    </td>
                    <td>{vr.position}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        )}

        {activeTab === "sponsored" && (
          filteredSponsored.length === 0 ? <p>No sponsored bills found.</p> : (
            <ul>
              {filteredSponsored.map(s => (
                <li key={s.bill_id}>
                  <BillLink title={s.bill_title} billType={s.bill_type} billNum={s.bill_num} />
                  <LawBadge became_law={s.became_law} />
                </li>
              ))}
            </ul>
          )
        )}

        {activeTab === "cosponsored" && (
          filteredCosponsored.length === 0 ? <p>No cosponsored bills found.</p> : (
            <ul>
              {filteredCosponsored.map(s => (
                <li key={s.bill_id}>
                  <BillLink title={s.bill_title} billType={s.bill_type} billNum={s.bill_num} />
                  <LawBadge became_law={s.became_law} />
                </li>
              ))}
            </ul>
          )
        )}
      </section>
    </div>
  );
}