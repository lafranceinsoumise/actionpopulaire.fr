import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";

const LoginMailEmpty = () => {
  const [email, setEmail] = useState("");
  const handleInputChange = (e) => {
    setEmail(e.target.value);
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
          error=""
          id="field"
          label="Adresse e-mail"
          placeholder="Adresse e-mail"
          onChange={handleInputChange}
          value={email}
        />
      </div>
      <Button
        color="primary"
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
