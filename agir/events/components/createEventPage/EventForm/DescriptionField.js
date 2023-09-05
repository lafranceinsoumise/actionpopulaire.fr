import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useShallowCompareEffect } from "react-use";

import Button from "@agir/front/genericComponents/Button";
import RichTextField from "@agir/front/formComponents/RichText/RichTextField";
import Spacer from "@agir/front/genericComponents/Spacer";

const DescriptionField = (props) => {
  const { onChange, name, error, required, disabled } = props;

  const [isExpanded, setIsExpanded] = useState(false);
  const [description, setDescription] = useState(props.value);

  const expand = () => {
    setIsExpanded(true);
  };

  useShallowCompareEffect(() => {
    onChange(name, description);
  }, [description, onChange, name]);

  return (
    <div>
      <strong
        css={`
          font-weight: 600;
          padding: 4px 0;
          font-size: 1rem;
          line-height: 1.5;
          margin-bottom: 5px;
        `}
      >
        Description de l'événement
      </strong>
      <br />
      <span
        css={`
          line-height: 1.5;
        `}
      >
        {!required && <em>Facultative. </em>}
        La description apparaîtra sur la page publique de l'événement.
      </span>
      {isExpanded ? (
        <RichTextField
          id="description"
          label=""
          placeholder=""
          onChange={setDescription}
          value={description}
          error={error}
          disabled={disabled}
        />
      ) : (
        <p
          css={`
            margin: 5px 0 0;
          `}
        >
          <Button small disabled={disabled} onClick={expand}>
            Ajouter une description à l'évenement
          </Button>
        </p>
      )}
    </div>
  );
};

DescriptionField.propTypes = {
  onChange: PropTypes.func,
  name: PropTypes.string.isRequired,
  value: PropTypes.string,
  error: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default DescriptionField;
