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
      },
      options,
    );
    $element.select2(settings);
  };

  $.fn.hierarchicalSelect = function (options) {
    const settings = $.extend({}, options);
    $.each(this, function (i, element) {
      const $element = $(element);
      init($element, settings);
    });
    return this;
  };

  $(function () {
    // Initialize all autocomplete widgets except the one in the template
    // form used when a new formset is added.
    $(".hierarchical-select").not("[name*=__prefix__]").hierarchicalSelect();
  });

  $(document).on(
    "formset:added",
    (function () {
      return function (event, $newFormset) {
        return $newFormset.find(".hierarchical-select").hierarchicalSelect();
      };
    })(this),
  );
}
