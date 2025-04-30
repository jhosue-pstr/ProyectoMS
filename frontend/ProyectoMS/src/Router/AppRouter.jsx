import { Navigate, Route, Routes } from "react-router-dom";
import { Dashboard } from "../components/Pages/Dashboard";
import { Cliente } from "../components/Pages/Cliente";

export const AppRouter = () => {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/cliente" element={<Cliente />} />
      <Route path="/*" element={<Navigate to="/" />} />
    </Routes>
  );
};
