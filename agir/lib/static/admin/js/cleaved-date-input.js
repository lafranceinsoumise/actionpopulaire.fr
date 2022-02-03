"use strict";
{
  const $ = django.jQuery;

  $.fn.cleaveDateInput = function () {
    this.each(function () {
      new Cleave(this, {
        date: true,
        datePattern: ["d", "m", "Y"],
      });
    });
  };

  $(function () {
    $(".cleaved-date-input").cleaveDateInput();
  });
  $(document).on(
    "formset:added",
    (function () {
      return function (event, $newFormset) {
        return $newFormset.find(".cleaved-date-input").cleaveDateInput();
      };
    })(this)
  );
}
