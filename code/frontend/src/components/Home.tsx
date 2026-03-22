import MemberSelect from "./MemberSelect";
import "./Home.css";

export default function Home() {
  return (
   <>
   <main>
      <section className="hero">
        {/* Left: stacked/layered images */}
        <div className="imageStack">
          <img className="branch" src="../../public/images/branch-2.png" alt="" />
          <img className="capitol" src="../../public/images/capitol-4.png" alt="" />
        </div>

        {/* Right: text + member select */}
        <div className="content">
          <h1>Congress Search</h1>
          <h2>119th Congress</h2>
          <p>Select a member to explore their voting record.</p>
          <MemberSelect />
        </div>
      </section>

      {/* Repeating banner image */}
      <div>
        <div className="repeatBanner" />
      </div>
      
    </main>
    </>
  );
}