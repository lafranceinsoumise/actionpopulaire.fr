import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import styled from "styled-components";

import DepartementField from "@agir/front/formComponents/DepartementField";
import SelectField from "@agir/front/formComponents/SelectField";
import useSWRImmutable from "swr/immutable";

const StyledField = styled.div`
  display: flex;
  flex-flow: row nowrap;
  gap: 1.5rem;
  justify-content: space-between;

  & > * {
    flex: 1 1 100%;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: column;
  }
`;

const getZipCodeLabel = (zipCode, short = false) => {
  const { code, communes } = zipCode;

  const communeNames =
    communes && Object.values(communes).length > 0
      ? Object.values(communes)
      : null;

  if (!communeNames) {
    return code;
  }

  if (short) {
    return code;
  }

  return `${code} — ${communeNames.join(", ")}`;
};

const ZipCodeSelectField = (props) => {
  const { value, onChange, zipCodes, isLoading } = props;

  const { data: session } = useSWRImmutable("/api/session/");
  const initializeForUser = useRef(!value.d && !value.z);

  const activeZipCodes = useMemo(
    () =>
      Array.isArray(zipCodes)
        ? zipCodes.map((zipCode) => ({
            ...zipCode,
            value: zipCode.code,
            label: getZipCodeLabel(zipCode),
          }))
        : [],
    [zipCodes],
  );

  const zipCodesByDepartement = useMemo(
    () =>
      activeZipCodes.reduce((obj, zipCode) => {
        if (zipCode.departement) {
          obj[zipCode.departement] = obj[zipCode.departement] || [];
          obj[zipCode.departement].push(zipCode);
        }

        return obj;
      }, {}),
    [activeZipCodes],
  );

  const filteredZipCodes = useMemo(() => {
    let visible = [];
    const selectedDepartements = !value.d
      ? Object.keys(zipCodesByDepartement)
      : !Array.isArray(value.d)
        ? [value.d]
        : value.d;
    selectedDepartements.forEach((departement) => {
      if (zipCodesByDepartement[departement]) {
        visible = visible.concat(zipCodesByDepartement[departement]);
      }
    });
    return visible;
  }, [value.d, zipCodesByDepartement]);

  const selectedZips = useMemo(() => {
    if (!value.z) {
      return value.z;
    }
    const zips = Array.isArray(value.z) ? value.z : [value.z];

    return zips
      .map((zip) => {
        const active = activeZipCodes.find((z) => z.code === zip);
        return (
          active && {
            ...active,
            label: getZipCodeLabel(active, true),
          }
        );
      })
      .filter(Boolean);
  }, [value.z, activeZipCodes]);

  const handleChangeZip = useCallback(
    (selected) => {
      const value = Array.isArray(selected)
        ? selected.map((zip) => zip.value)
        : selected?.value;
      onChange("z", value);
    },
    [onChange],
  );

  useEffect(() => {
    if (!initializeForUser.current || isLoading || !session?.user) {
      return;
    }

    initializeForUser.current = false;

    if (
      session.user.zip &&
      activeZipCodes.find((zipCode) => zipCode.code === session.user.zip)
    ) {
      onChange("z", session.user.zip);

      return;
    }

    if (
      session.user.departement &&
      activeZipCodes.find(
        (zipCode) => zipCode.departement === session.user.departement,
      )
    ) {
      onChange("d", session.user.departement);

      return;
    }
  }, [isLoading, value, session?.user, activeZipCodes, onChange]);

  useEffect(() => {
    if (!selectedZips) {
      return;
    }

    const selectedDepartements = Array.isArray(value.d)
      ? value.d
      : [value.d].filter(Boolean);

    const missingDepartementZips = selectedZips.filter(
      (zip) => !selectedDepartements.includes(zip.departement),
    );

    if (missingDepartementZips.length === 0) {
      return;
    }

    const missingDepartements = Array.from(
      new Set(
        missingDepartementZips.map((z) => z.departement).filter(Boolean),
      ).values(),
    );

    onChange(
      "d",
      value.d
        ? [...selectedDepartements, ...missingDepartements]
        : missingDepartements,
    );
  }, [value.d, selectedZips, onChange]);

  useEffect(() => {
    if (!selectedZips) {
      return;
    }

    const selected = Array.isArray(value.z)
      ? value.z
      : [value.z].filter(Boolean);

    if (selectedZips.length < selected.length) {
      onChange(
        "z",
        selectedZips.map((zip) => zip.code),
      );
    }
  }, [value.z, selectedZips, onChange]);

  return (
    <StyledField>
      <DepartementField
        isMulti
        value={value.d}
        onChange={(departements) => onChange("d", departements)}
        label="Départements"
        placeholder="Chercher un département par nom ou code"
        disabled={isLoading}
      />
      <SelectField
        isMulti
        isSearchable
        value={selectedZips}
        options={filteredZipCodes}
        onChange={handleChangeZip}
        label="Codes postaux"
        placeholder="Chercher un code postal par code ou par commune"
        disabled={isLoading || !value.d}
      />
    </StyledField>
  );
};

ZipCodeSelectField.propTypes = {
  value: PropTypes.shape({
    z: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(PropTypes.string),
    ]),
    d: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(PropTypes.string),
    ]),
  }),
  onChange: PropTypes.func,
  zipCodes: PropTypes.array,
  isLoading: PropTypes.bool,
};

export default ZipCodeSelectField;
