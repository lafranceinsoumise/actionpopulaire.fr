const formatEvent = (types, subtypes) => (event) => {
  const subtype = subtypes[event.subtype];
  const type = types[subtype.type];
  const color = subtype.color || type.color;
  const label = !subtype.hideLabel ? subtype.description : type.label;

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

const formatGroup = (types, subtypes) => (group) =>
  `
    <a target="_top" href="${group.link}">${group.name}</a>
    <br/>
    <strong>
      ${types[group.type].label}${group.is_certified ? " certifié" : ""}
    </strong>
    ${group.subtypes
      .map((subtype) =>
        subtypes[subtype] && !subtypes[subtype].hideLabel
          ? `<small style='display:block;'>${subtypes[subtype].description}</small>`
          : "",
      )
      .join("")}
  `;

const getFormatPopups = (itemType, types, subtypes) => {
  types = types.reduce(
    (o, type) => ({
      ...o,
      [type.id]: type,
    }),
    {},
  );
  subtypes = subtypes.reduce(
    (o, subtype) => ({
      ...o,
      [subtype.id]: subtype,
    }),
    {},
  );
  return itemType === "groups"
    ? formatGroup(types, subtypes)
    : formatEvent(types, subtypes);
};

export default getFormatPopups;
