import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./components/Home";
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
        <Route path="/member/:memberId" element={<MemberVotes />} />
        <Route path="/visualizations/:vizId" element={<VizDetail />} />
      </Routes>
    </BrowserRouter>
  );
}