import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./components/Home";
// import MemberSelect from "./components/MemberSelect";
import MemberVotes from "./components/MemberVotes";
import VizDetail from "./components/VizDetail";
import Navbar from "./components/Navbar";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        {/* <Route path="/" element={<MemberSelect />} />
        <Route path="/" element={<About />} />
        <Route path="/" element={<VizGallery />} /> */}
        <Route path="/member/:memberId" element={<MemberVotes />} />
        <Route path="/visualizations/:vizId" element={<VizDetail />} />
      </Routes>
    </BrowserRouter>
  );
}