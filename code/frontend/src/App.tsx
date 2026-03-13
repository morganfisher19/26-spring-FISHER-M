import { BrowserRouter, Routes, Route } from "react-router-dom";
import MemberSelect from "./components/MemberSelect";
import MemberVotes from "./components/MemberVotes";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MemberSelect />} />
        <Route path="/member/:memberId" element={<MemberVotes />} />
      </Routes>
    </BrowserRouter>
  );
}