import { Link, useLocation } from "react-router-dom";
import { useRef } from "react";
import "./Navbar.css";

const VIZ_LINKS = [
  { label: "Bipartisanship In Congress", path: "/visualizations/bipartisanship" },
  { label: "Bill Survival", path: "/visualizations/bill-survival" },
  { label: "Congressional Activity", path: "/visualizations/activity-over-time" },
  { label: "Bill Activity", path: "/visualizations/top-influencers" },
];

export default function Navbar() {
  const { pathname } = useLocation();
  const flowerContainerRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLLIElement>(null);

  const handleFlowerRain = () => {
    if (!flowerContainerRef.current) return;
    const container = flowerContainerRef.current;

    container.style.visibility = "visible";

    const totalDrops = 50;

    const spawnDrop = () => {
      const isPetal = Math.random() < 0.5;
      const drop = document.createElement("img");
      drop.src = isPetal
        ? "../../images/petal-1.png"
        : "../../images/flower-1.png";
      drop.className = "falling-drop";

      // random horizontal start position
      drop.style.left = `${Math.random() * 100}vw`;

      // random size
      const size = 20 + Math.random() * 30;
      drop.style.width = `${size}px`;
      drop.style.height = "auto";

      // random animation duration
      const animDuration = 3 + Math.random() * 4; // 3s to 6s
      drop.style.animationDuration = `${animDuration}s`;

      // remove only after animation ends (reaches bottom)
      drop.addEventListener("animationend", () => {
        drop.remove();
      });

      container.appendChild(drop);
    };

    // spawn initial batch
    for (let i = 0; i < totalDrops; i++) spawnDrop();

    // repeat batch every second 4 times
    let repeatCount = 0;
    const interval = setInterval(() => {
      if (repeatCount >= 4) {
        clearInterval(interval);

        setTimeout(() => {
          container.style.visibility = "hidden";
        }, 6_000); // max animation duration ~10s
        return;
      }
      for (let i = 0; i < totalDrops; i++) spawnDrop();
      repeatCount++;
    }, 1000);
  };

  return (
    <>
      <nav className="navbar">
        <div className="navbar-brand">
          <Link to="/" className="brand-link">Member Monitor</Link>
          <img
            src="../../images/flower-3.png"
            alt="flower"
            className="flower-icon"
            onClick={handleFlowerRain}
          />
          </div>
        <ul className="navbar-links">
          <li>
            <Link to="/" className={pathname === "/" ? "active" : ""}>
              Home
            </Link>
          </li>
          <li ref={dropdownRef} className="dropdown-wrapper">
            <div className="dropdown">
              <button className="dropbtn">Data Visualizations</button>
              <div className="dropdown-content">
                {VIZ_LINKS.map((link, index) => (
                  <a key={index} href={link.path}>
                    {link.label}
                  </a>
                ))}
              </div>
            </div>
          </li>
        </ul>
      </nav>

      {/* container for floating flowers */}
      <div ref={flowerContainerRef} className="flower-container"></div>
    </>
  );
}