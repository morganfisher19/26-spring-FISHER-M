import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  const { pathname } = useLocation();

  const links = [
    { label: "Home", path: "/" },
    // { label: "About", path: "/about" },
    // { label: "Data Visualizations", path: "/visualizations" },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">Congress Search</div>
      <ul className="navbar-links">
        {links.map(({ label, path }) => (
          <li key={path}>
            <Link
              to={path}
              className={pathname === path ? "active" : ""}
            >
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}