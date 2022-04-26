import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledProgress = styled.div`
  display: inline-grid;
  color: ${(props) =>
    props.$progress === 1 && !props.$hasAlert
      ? props.theme.white
      : props.theme.black1000};

  & > * {
    grid-row: 1/2;
    grid-column: 1/2;
    align-items: center;
    justify-content: center;
  }

  & > svg {
    transform: rotate(-90deg);

    circle {
      stroke: ${(props) => props.theme.black100};
      fill: transparent;
      stroke-dashoffset: 0;
    }

    circle + circle {
      stroke: ${(props) =>
        props.$hasAlert ? props.theme.secondary600 : props.theme.green500};
      fill: ${(props) =>
        props.$progress === 1 && !props.$hasAlert
          ? props.theme.green500
          : "transparent"};
    }
  }
`;

const StyledCard = styled(Card)`
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};
  color: ${(props) => props.theme.black700};

  & > div {
    display: flex;
    align-items: center;
    flex-flow: row nowrap;
    gap: 0.75rem;

    p {
      margin: 0;
      font-size: 0.875rem;

      strong {
        font-size: 1rem;
        font-weight: 500;
        color: ${(props) => props.theme.black1000};
      }
    }

    ${StyledProgress} {
      flex: 0 0 auto;
    }
  }
`;

const Progress = (props) => {
  const { progress, hasAlert } = props;

  const radius = 24;
  const size = 2 * radius;
  const stroke = 4;
  const normalizedRadius = radius - stroke;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - progress * circumference;

  return (
    <StyledProgress $progress={progress} $hasAlert={hasAlert}>
      <svg height={size} width={size}>
        <circle
          strokeWidth={stroke}
          strokeDasharray={circumference + " " + circumference}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          strokeWidth={stroke}
          strokeDasharray={circumference + " " + circumference}
          style={{ strokeDashoffset }}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
      </svg>
      <RawFeatherIcon
        style={{ width: size + "px", height: size + "px" }}
        width="18px"
        height="18px"
        name={hasAlert ? "alert-triangle" : "check-circle"}
      />
    </StyledProgress>
  );
};

Progress.propTypes = {
  hasAlert: PropTypes.bool,
  progress: PropTypes.number,
};

const CertificationStatus = (props) => {
  const { certificationPanelRoute, isCertified, criteria } = props;

  const certificationCriteria = Object.keys(criteria);
  const checkedCriteria = certificationCriteria.filter((key) => criteria[key]);
  const isCertifiable = checkedCriteria.length === certificationCriteria.length;

  return (
    <StyledCard>
      <div>
        <Progress
          hasAlert={isCertified && !isCertifiable}
          progress={checkedCriteria.length / certificationCriteria.length}
        />
        <p>
          <strong>Certification du groupe</strong>
          <br />
          <span>
            {checkedCriteria.length}/{certificationCriteria.length}{" "}
            {checkedCriteria.length <= 1
              ? "condition remplie"
              : "conditions remplies"}
          </span>
        </p>
      </div>
      <Spacer size="1rem" />
      <Button small link to={certificationPanelRoute}>
        En savoir plus
      </Button>
    </StyledCard>
  );
};
CertificationStatus.propTypes = {
  isCertified: PropTypes.bool,
  certificationPanelRoute: PropTypes.string,
  criteria: PropTypes.shape({
    genderBalance: PropTypes.bool,
    activity: PropTypes.bool,
    members: PropTypes.bool,
    seasoned: PropTypes.bool,
  }),
};
export default CertificationStatus;
