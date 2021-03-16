import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import { login } from "@agir/front/authentication/api";
import { routeConfig } from "@agir/front/app/routes.config";
import { useHistory } from "react-router-dom";

const LoginMailEmpty = () => {
  const history = useHistory();
  const [email, setEmail] = useState("");
  const [error, setError] = useState({});

  const handleInputChange = (e) => {
    setEmail(e.target.value);
  };

  const handleSubmit = async () => {
    setError({});
    const data = await login(email);
    console.log("data : ", data);
    if (data.error) {
      setError(data.error);
      return;
    }
    const route = routeConfig.codeLogin.getLink();
    history.push(route);
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
          error={error && error.email}
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
