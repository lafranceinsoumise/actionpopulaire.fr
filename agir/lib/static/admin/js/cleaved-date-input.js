"use strict";
{
  const $ = django.jQuery;

  function formatDate(d) {
    const day = d.getDate().toString().padStart(2, "0");
    const month = (d.getMonth() + 1).toString().padStart(2, "0");
    const year = d.getFullYear();

    return `${day}/${month}/${year}`;
  }

  $.fn.cleaveDateInput = function () {
    this.each(function () {
      new Cleave(this, {
        date: true,
        datePattern: ["d", "m", "Y"],
      });

      if ($(this).data("today")) {
        const input = this;
        $(
          '<span class="datetimeshortcuts"><a href="#">Aujourd\'hui</button></span>',
        )
          .click(function (e) {
            e.preventDefault();
            input.value = formatDate(new Date());
          })
          .insertAfter(this);
      }

      return this;
    });
  };

  $(function () {
    $(".cleaved-date-input").cleaveDateInput();
  });
  $(document).on(
    "formset:added",
    (function () {
      return function (_event, $newFormset) {
        return $newFormset.find(".cleaved-date-input").cleaveDateInput();
      };
    })(this),
  );
}
