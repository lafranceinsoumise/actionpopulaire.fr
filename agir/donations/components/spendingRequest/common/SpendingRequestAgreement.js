import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Link from "@agir/front/app/Link";

const AgreementField = ({ initialValue, onChange, disabled, reset }) => {
  const [agreements, setAgreements] = useState({
    political: !!initialValue,
    legal: !!initialValue,
  });

  const handleChangeAgreement = (e) => {
    setAgreements((state) => ({
      ...state,
      [e.target.name]: e.target.checked,
    }));
  };

  const hasAgreement = Object.values(agreements).every(Boolean);

  useEffect(() => {
    reset &&
      setAgreements((data) =>
        Object.keys(data).reduce((obj, key) => {
          obj[key] = false;
          return obj;
        }, {}),
      );
  }, [reset]);

  useEffect(() => {
    onChange(hasAgreement);
  }, [onChange, hasAgreement]);

  return (
    <>
      <CheckboxField
        disabled={disabled}
        id="political"
        name="political"
        value={agreements.political}
        onChange={handleChangeAgreement}
        label={
          <>
            Je certifie que cette dépense est conforme à{" "}
            <Link
              route="charteEquipes"
              target="_blank"
              rel="noopener noreferrer"
            >
              la charte des groupes d’action
            </Link>{" "}
            et aux principes, aux orientations politiques, stratégiques,
            programmatiques et électorales de{" "}
            <Link route="principes" target="_blank" rel="noopener noreferrer">
              la France Insoumise
            </Link>
            .
          </>
        }
      />
      <CheckboxField
        disabled={disabled}
        id="legal"
        name="legal"
        value={agreements.legal}
        onChange={handleChangeAgreement}
        label="Je certifie sur l'honneur être une personne physique et la dépense ne porte pas atteinte à la législation encadrant l’activité des partis et groupements politiques."
      />
    </>
  );
};

AgreementField.propTypes = {
  initialValue: PropTypes.bool,
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
  reset: PropTypes.bool,
};

export default AgreementField;
