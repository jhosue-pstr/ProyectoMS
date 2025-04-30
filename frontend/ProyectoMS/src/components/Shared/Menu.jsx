import React from "react";
import { Link } from "react-router-dom";

export const Menu = () => {
  return (
    <nav>
      <Link to="/">Dashboard </Link>
      <Link to="/cliente">Cliente </Link>
    </nav>
  );
};
