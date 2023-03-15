const formatEvent = (types, subtypes) => (event) => {
  const subtype = subtypes.find((type) => type.id === event.subtype);
  const type = types.find((type) => type.id === subtype.type);
  const color = subtype.color ? subtype.color : type.color;
  const label = subtype.hideLabel ? type.label : subtype.description;

  return `
    <a target="_top" href="${event.link}" style="color:${color};">
      ${event.name}
    </a>
    <br/>
    <strong>${label}</strong>
    <br/>
    ${event.date}
  `;
};

const formatGroup = (types, subtypes) => (group) => {
  const type = types.find((type) => type.id === group.type);
  const displayableSubtypes = subtypes
    .filter(
      (subtype) => !subtype.hideLabel && group.subtypes.includes(subtype.id)
    )
    .map((subtype) => subtype.description);

  return `
    <a target="_top" href="${group.link}">${group.name}</a>
    <br/>
    <strong>${type.label}</strong>
    ${
      displayableSubtypes.length > 0
        ? `<br/><small>${displayableSubtypes.map(
            (subtype) => `· ${subtype}`
          )}</small>`
        : ""
    }
  `;
};

const getFormatPopups = (types, subtypes) => ({
  groups: formatGroup(types, subtypes),
  events: formatEvent(types, subtypes),
});

export default getFormatPopups;
