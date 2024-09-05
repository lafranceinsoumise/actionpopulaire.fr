import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledProgress = styled.div`
  display: inline-grid;
  color: ${(props) =>
    props.$progress === 1 && !props.$hasAlert
      ? props.theme.background0
      : props.theme.text1000};

  & > * {
    grid-row: 1/2;
    grid-column: 1/2;
    align-items: center;
    justify-content: center;
  }

  & > svg {
    transform: rotate(-90deg);

    circle {
      stroke: ${(props) => props.theme.text100};
      fill: transparent;
      stroke-dashoffset: 0;
    }

    circle + circle {
      stroke: ${(props) =>
        props.$hasAlert ? props.theme.secondary600 : props.theme.success500};
      fill: ${(props) =>
        props.$progress === 1 && !props.$hasAlert
          ? props.theme.success500
          : "transparent"};
    }
  }
`;

const StyledCard = styled(Card)`
  padding: 1rem;
  background-color: transparent;
  border-radius: ${(props) => props.theme.borderRadius};
  color: ${(props) => props.theme.text700};

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
        color: ${(props) => props.theme.text1000};
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
  const { isCertifiable, isCertified, certificationCriteria, routes } = props;

  const certificationPanelRoute = routes
    .find((route) => route.id === "certification")
    ?.getLink();

  const criteria = useMemo(
    () =>
      Object.entries(certificationCriteria).map(([id, val]) => ({
        id,
        ...val,
      })),
    [certificationCriteria],
  );

  const [checkedCriteria, hasUncheckedCriteria] = useMemo(() => {
    const checked = criteria.filter((criterion) => !!criterion.value);
    return [checked, checked.length !== criteria.length];
  }, [criteria]);

  if (!isCertifiable) {
    return null;
  }

  return (
    <StyledCard>
      <div>
        <Progress
          hasAlert={isCertified && hasUncheckedCriteria}
          progress={checkedCriteria.length / criteria.length}
        />
        <p>
          <strong>Certification du groupe</strong>
          <br />
          <span>
            {checkedCriteria.length}/{criteria.length}{" "}
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
  isCertifiable: PropTypes.bool,
  isCertified: PropTypes.bool,
  routes: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      getLink: PropTypes.func.isRequired,
    }).isRequired,
  ).isRequired,
  certificationCriteria: PropTypes.shape({
    gender: PropTypes.shape({ value: PropTypes.bool }),
    activity: PropTypes.shape({ value: PropTypes.bool }),
    members: PropTypes.shape({ value: PropTypes.bool }),
    creation: PropTypes.shape({ value: PropTypes.bool }),
  }),
};
export default CertificationStatus;
