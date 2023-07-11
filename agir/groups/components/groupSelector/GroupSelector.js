import React from "react";

import Async from "react-select/async";
import PropTypes from "prop-types";

import search from "./search";
import { debounce } from "@agir/lib/utils/promises";

const GROUP_TYPE = PropTypes.shape({
  id: PropTypes.string,
  name: PropTypes.string,
});

const debouncedSearch = debounce(search, 200);

const GroupSelector = ({
  groupChoices,
  onChange,
  value,
  filter,
  defaultOptionsLabel,
  search,
}) => {
  const defaultOptions = {
    label: defaultOptionsLabel,
    options: groupChoices.filter(filter),
  };
  return (
    <Async
      value={value}
      loadOptions={(terms) =>
        search(terms).then((options) =>
          options.length
            ? [
                {
                  label: "Ma recherche",
                  options: options,
                },
                defaultOptions,
              ]
            : [],
        )
      }
      defaultOptions={[defaultOptions]}
      formatGroupLabel={(g) => {
        return g.label;
      }}
      getOptionValue={({ id }) => id}
      getOptionLabel={({ name, location_zip }) =>
        location_zip ? `${name} (${location_zip})` : name
      }
      onChange={onChange}
      loadingMessage={() => "Recherche..."}
      noOptionsMessage={({ inputValue }) =>
        inputValue.length < 3
          ? "Entrez au moins 3 lettres pour chercher un groupe"
          : "Pas de résultats"
      }
      placeholder="Choisissez un groupe..."
    >
      {groupChoices.map(({ name, id }) => (
        <option key={id} value={id}>
          {name}
        </option>
      ))}
    </Async>
  );
};
GroupSelector.propTypes = {
  onChange: PropTypes.func,
  groupChoices: PropTypes.arrayOf(GROUP_TYPE),
  value: GROUP_TYPE,
  filter: PropTypes.func,
  defaultOptionsLabel: PropTypes.string,
  search: PropTypes.func,
};
GroupSelector.defaultProps = {
  onChange: () => null,
  filter: () => true,
  groupChoices: [],
  value: null,
  defaultOptionsLabel: "Mes groupes",
  search: debouncedSearch,
};

export default GroupSelector;
