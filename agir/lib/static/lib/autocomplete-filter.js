/* global django */
(function ($) {
  $(function () {
    $("#changelist-filter select.select-filter").on("change", function () {
      const value = $(this).val() || "";
      const name = this.name;
      window.location.search = makeSearch(window.location.search, name, value);
    });
  });
})(django.jQuery);

function makeSearch(currentSearch, name, value) {
  if (currentSearch === "") {
    return "?" + encodeURIComponent(name) + "=" + encodeURIComponent(value);
  }

  const searchParams = currentSearch
    .slice(1)
    .split("&")
    .map(function (searchPart) {
      return searchPart.split("=");
    })
    .filter(function (searchAssignment) {
      return searchAssignment.length === 2;
    })
    .map(function (searchAssignment) {
      return [
        decodeURIComponent(searchAssignment[0]),
        decodeURIComponent(searchAssignment[1]),
      ];
    })
    .filter(function (searchAssignment) {
      return searchAssignment[0] !== name;
    });

  searchParams.push([name, value]);

  return (
    "?" +
    searchParams
      .map(function (paramAssignment) {
        return [
          encodeURIComponent(paramAssignment[0]),
          encodeURIComponent(paramAssignment[1]),
        ].join("=");
      })
      .join("&")
  );
}
