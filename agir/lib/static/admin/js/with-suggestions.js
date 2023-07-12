"use strict";
{
  const $ = django.jQuery;
  const init = function ($element, options) {
    const settings = $.extend(
      {
        templateResult: function (data, container) {
          if (data.element) {
            $(container).addClass($(data.element).attr("class"));
          }
          return data.text;
        },
        tags: true,
      },
      options,
    );
    $element.select2(settings);
  };

  $.fn.withSuggestions = function (options) {
    const settings = $.extend({}, options);
    return this.pushStack(
      $.map(this, function (element) {
        const $element = $(element);
        const suggestions = $element.data("suggestions");

        if (suggestions) {
          if (
            $element.val() !== "" &&
            suggestions.indexOf($element.val()) === -1
          ) {
            suggestions.unshift($element.val());
          }
          suggestions.unshift("");

          const select = document.createElement("select");
          $(select)
            .append(
              suggestions.map((s) => {
                const option = document.createElement("option");
                $(option).text(s).attr("value", s);
                return option;
              }),
            )
            .attr({
              name: $element.attr("name"),
              id: $element.attr("id"),
            })
            .val($element.val())
            .data("maxlength", $element.attr("maxlength"))
            .insertAfter($element);
          $element.remove();
          init($(select), settings);
          return select;
        }
        return element;
      }),
    );
  };

  $(function () {
    // Initialize all autocomplete widgets except the one in the template
    // form used when a new formset is added.
    $(".with-suggestions").not("[name*=__prefix__]").withSuggestions();
  });

  $(document).on(
    "formset:added",
    (function () {
      return function (event, $newFormset) {
        return $newFormset.find(".with-suggestion").withSuggestions();
      };
    })(this),
  );
}
