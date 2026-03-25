import "./About.css";

export default function About() {
  return (
    <section className="aboutSection">
      <h1>About Member Monitor</h1>
      <div className="row">

        {/* Left Flower - GitHub */}
        <div className="flower-wrapper">
          <div className="flower-inner">

            {/* Front */}
            <div className="flower-front">
              <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <g transform="translate(50,50)">
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(0)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(45)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(90)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(135)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(180)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(225)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(270)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(315)"/>
                </g>
                <foreignObject x="20" y="35" width="60" height="30">
                  <div className="flowerText">
                    Member Monitor was designed and developed using publicly accessible data to provide a free, user-friendly way to explore member's legislative activity.
                  </div>
                </foreignObject>
              </svg>
            </div>

            {/* Back */}
            <div className="flower-back">
              <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <g transform="translate(50,50)">
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(0)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(45)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(90)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(135)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(180)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(225)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(270)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(315)"/>
                </g>
                <foreignObject x="25" y="28" width="50" height="44">
                  <div className="flowerBackContent">
                    <a href="https://github.com/morganfisher19/26-spring-FISHER-M" target="_blank" rel="noopener noreferrer">
                      <img src="../../public/images/github-logo.png" alt="GitHub" className="backIcon" />
                      <span className="backLabel">Open Source Code Found Here</span>
                    </a>
                  </div>
                </foreignObject>
              </svg>
            </div>

          </div>
        </div>

        <div className="middle">
          <img src="../../public/images/tree-3.png" alt="tree" />
        </div>

        {/* Right Flower - LinkedIn */}
        <div className="flower-wrapper">
          <div className="flower-inner">

            {/* Front */}
            <div className="flower-front">
              <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <g transform="translate(50,50)">
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(0)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(45)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(90)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(135)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(180)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(225)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(270)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(315)"/>
                </g>
                <foreignObject x="20" y="35" width="60" height="30">
                  <div className="flowerText">
                    Morgan Fisher built Member Monitor for her senior capstone project at the George Washington University. The website combines her interests in politics, data, & coding.
                  </div>
                </foreignObject>
              </svg>
            </div>

            {/* Back */}
            <div className="flower-back">
              <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <g transform="translate(50,50)">
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(0)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(45)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(90)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(135)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(180)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(225)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(270)"/>
                  <ellipse cx="0" cy="-20" rx="12" ry="20" fill="#FFB3C1" transform="rotate(315)"/>
                </g>
                <foreignObject x="20" y="20" width="60" height="60">
                  <div className="flowerBackContent">
                    <a href="https://www.linkedin.com/in/morganfisher19" target="_blank" rel="noopener noreferrer">
                      <img src="../../public/images/headshot.jpg" alt="LinkedIn" className="headshotIcon" />
                    </a>
                  </div>
                </foreignObject>
              </svg>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
}