import React, { useState } from "react";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import style from "@agir/front/genericComponents/_variables.scss";
// import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

const defaultData = {
  email: "",
  postalCode: "",
  reasonChecked: 0,
};

const SignIn = () => {
  const [rgpdChecked, setRgpdChecked] = useState(false);
  const [formData, setFormData] = useState(defaultData);

  const handleRgpdCheck = () => {
    setRgpdChecked(!rgpdChecked);
  };

  const handleChecked = (value) => {
    setFormData({ ...formData, reasonChecked: value });
  };

  const handleChange = (e, name) => {
    const newFormData = { ...formData };
    newFormData[name] = e.target.value;
    setFormData(newFormData);
  };

  return (
    <div style={{ width: "500px", maxWidth: "100%" }}>
      <h1>Je m'inscris</h1>

      <div style={{ display: "inline-block", marginTop: "8px" }}>
        <span>Déjà inscrit·e ?</span>
        &nbsp;
        <span style={{ color: style.primary500, fontWeight: 700 }}>
          Je me connecte
        </span>
      </div>
      <span
        style={{ display: "inline-block", margin: "20px 0px", fontWeight: 500 }}
      >
        Pour quelle campagne rejoignez-vous Action Populaire ?
      </span>

      <ul style={{ padding: "0", listStyleType: "none" }}>
        <li onClick={() => handleChecked(0)}>
          <label style={{ cursor: "pointer", fontWeight: 400 }}>
            <input
              type="radio"
              value="0"
              onChange={() => {}}
              checked={0 === formData.reasonChecked}
            />
            <span>&nbsp; La présidentielle de 2022</span>
          </label>
        </li>
        <li onClick={() => handleChecked(1)}>
          <label style={{ cursor: "pointer", fontWeight: 400 }}>
            <input
              type="radio"
              value="1"
              onChange={() => {}}
              checked={1 === formData.reasonChecked}
            />
            <span>&nbsp; Une autre campagne de la France Insoumise</span>
          </label>
        </li>
      </ul>

      <div
        style={{
          boxSizing: "border-box",
          margin: "0 auto",
          marginTop: "24px",
          display: "flex",
          justifyContent: "space-between",
          flexWrap: "wrap",
        }}
      >
        <TextField
          error=""
          label="Adresse e-mail"
          placeholder="Adresse e-mail"
          onChange={(e) => handleChange(e, "email")}
          value={formData.email}
          style={{ width: "340px" }}
        />

        <TextField
          error=""
          label="Code postal"
          placeholder=""
          onChange={(e) => handleChange(e, "postalCode")}
          value={formData.postalCode}
          style={{ width: "140px" }}
        />
      </div>

      <div
        onClick={handleRgpdCheck}
        style={{ marginTop: "16px", marginBottom: "32px", cursor: "pointer" }}
      >
        <input type="checkbox" checked={rgpdChecked} /> &nbsp; J'accepte que mes
        informations soient traitées par Action Populaire, conformément à la
        politique de conservation des données
      </div>

      <Button
        color="primary"
        style={{
          marginTop: "0.5rem",
          maxWidth: "100%",
          width: "100%",
          justifyContent: "center",
        }}
      >
        Créer mon compte
      </Button>
    </div>
  );
};

// const SignIn = () => {

//   return (
//     <>
//       <ResponsiveLayout
//         MobileLayout={SignInDesktop}
//         DesktopLayout={SignInDesktop}
//       >
//       </ResponsiveLayout>
//     </>
//   );
// };

export default SignIn;
