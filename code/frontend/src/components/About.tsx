import "./About.css";

export default function About() {
  return (
    <section>
      <div className="row">
        <div className="flower">
          <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <g transform="translate(50,50)">
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(0)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(45)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(90)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(135)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(180)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(225)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(270)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(315)"/>
              <circle cx="0" cy="0" r="18" fill="white"/>
            </g>
            <text x="50" y="54" text-anchor="middle" font-size="10">Your text</text>
          </svg>
        </div>

        <div className="middle">
          <img src="../../public/images/tree-1.png" alt="tree" />
        </div>

        <div className="flower">
          <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <g transform="translate(50,50)">
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(0)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(45)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(90)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(135)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(180)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(225)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(270)"/>
              <ellipse cx="0" cy="-20" rx="12" ry="20" fill="pink" transform="rotate(315)"/>
              <circle cx="0" cy="0" r="18" fill="white"/>
            </g>
            <text x="50" y="54" text-anchor="middle" font-size="10">Your text</text>
          </svg>
        </div>
      </div>
    </section>
  );
}