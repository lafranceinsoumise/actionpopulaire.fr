import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import { login } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useHistory, useLocation } from "react-router-dom";

const LoginMailEmpty = () => {
  const history = useHistory();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [error, setError] = useState({});

  let next = "";
  if (location.search !== undefined)
    next = new URLSearchParams(location.search).get("next");

  const handleInputChange = (e) => {
    setEmail(e.target.value);
  };

  const handleSubmit = async () => {
    setError({});
    const data = await login(email);

    if (data.error) {
      setError(data.error);
      return;
    }

    const route = routeConfig.codeLogin.getLink();
    history.push(route, { email: email, code: data.data.code, next: next });
  };

  return (
    <>
      <div
        style={{
          boxSizing: "border-box",
          margin: "0 auto",
          marginTop: "24px",
        }}
      >
        <TextField
          id="field"
          label="Adresse e-mail"
          error={error && (error.email || error.detail)}
          placeholder="Adresse e-mail"
          onChange={handleInputChange}
          value={email}
        />
      </div>
      <Button
        color="primary"
        onClick={handleSubmit}
        style={{
          marginTop: "0.5rem",
          maxWidth: "100%",
          width: "400px",
          justifyContent: "center",
        }}
      >
        Me connecter
      </Button>
    </>
  );
};

export default LoginMailEmpty;
