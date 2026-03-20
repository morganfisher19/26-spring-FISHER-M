import MemberSelect from "./MemberSelect";
import "./Home.css";

export default function Home() {
  return (
    <main>
      <section>
        <h1>Congress Search</h1>
        <h2>119th Congress</h2>
        <p>Select a member to explore their voting record.</p>
      </section>
      <MemberSelect />
    </main>
  );
}