import PropTypes from "prop-types";
import React, { useCallback } from "react";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import ImageField from "@agir/front/formComponents/ImageField";
import Spacer from "@agir/front/genericComponents/Spacer";

const EventImageField = (props) => {
  const { onChange, value, name, error, required, disabled } = props;

  const handleChange = useCallback(
    (file) => {
      onChange(name, file && { file, hasLicense: false });
    },
    [name, onChange],
  );

  const handleChangeLicense = useCallback(
    (e) => {
      onChange(name, { ...value, hasLicense: e.target.checked });
    },
    [name, value, onChange],
  );

  return (
    <>
      <strong
        css={`
          font-weight: 600;
          padding: 4px 0;
          font-size: 1rem;
          line-height: 1.5;
          margin-bottom: 5px;
        `}
      >
        Image de couverture
      </strong>
      <br />
      <span
        css={`
          line-height: 1.5;
        `}
      >
        {!required && <em>Facultative. </em>}
        L'image apparaîtra sur la page et sur les réseaux sociaux. Taille
        conseillée&nbsp;: 1200x630&nbsp;px ou plus.
      </span>
      <ImageField
        name={name}
        value={value?.file || null}
        onChange={handleChange}
        accept=".jpg,.jpeg,.gif,.png"
        disabled={disabled}
        required={required}
        error={error}
      />
      {!!value?.file && (
        <>
          <Spacer size="0.5rem" />
          <CheckboxField
            value={value?.hasLicense || false}
            label={
              <span>
                En important une image, je certifie être propriétaire des droits
                et accepte de la partager sous licence libre{" "}
                <a
                  target="_blank"
                  rel="noopener noreferrer"
                  href="https://creativecommons.org/licenses/by-nc-sa/3.0/fr/"
                >
                  Creative Commons CC-BY-NC 3.0
                </a>
                .
              </span>
            }
            onChange={handleChangeLicense}
            disabled={!value || disabled}
            error={error}
            required
          />
        </>
      )}
    </>
  );
};
EventImageField.propTypes = {
  onChange: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  value: PropTypes.object,
  error: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default EventImageField;
