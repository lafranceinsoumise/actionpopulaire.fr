import { dateFromISOString, displayHumanDate } from "@agir/lib/utils/time";

export default function getFormatPopups(types, subtypes) {
  function formatEvent(event) {
    var subtype = subtypes.find(function (type) {
      return type.id === event.subtype;
    });
    var type = types.find(function (type) {
      return type.id === subtype.type;
    });
    return (
      '<a href="/evenements/' +
      event.id +
      '/" style="color:' +
      (subtype.color ? subtype.color : type.color) +
      ';">' +
      event.name +
      "</a><br /><strong>" +
      (subtype.hideLabel ? type.label : subtype.description) +
      "</strong><br />" +
      displayHumanDate(dateFromISOString(event.start_time))
    );
  }

  function formatGroup(group) {
    var displayableSubtypes = subtypes
      .filter(function (subtype) {
        return group.subtypes.indexOf(subtype.id) !== -1 && !subtype.hideLabel;
      })
      .map(function (subtype) {
        return subtype.description;
      });
    var type = types.find(function (type) {
      return type.id === group.type;
    });
    return (
      '<a href="/groupes/' +
      group.id +
      '">' +
      group.name +
      "</a><br><strong>" +
      type.label +
      "</strong>" +
      (displayableSubtypes.length
        ? "<br>" + displayableSubtypes.join(" &bull; ")
        : "")
    );
  }

  return { groups: formatGroup, events: formatEvent };
}
