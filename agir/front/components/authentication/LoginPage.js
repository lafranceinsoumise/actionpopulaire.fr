import React from "react";
import { useLocation } from "react-router-dom";

const LoginPage = () => {
  const location = useLocation();
  return (
    <div>
      <h1>Connexion !</h1>
      {location.state.from && location.state.from.pathname && (
        <p>
          Next = <strong>{location.state.from.pathname}</strong>
        </p>
      )}
    </div>
  );
};

export default LoginPage;
