function selectAllWhenFocusing(e) {
  e.target.setSelectionRange(0, e.target.value.length);
}

function setUpCopyBoxes() {
  const copyboxes = document.querySelectorAll(".copybox");

  Array.prototype.map.call(copyboxes, function (copybox) {
    copybox.addEventListener("focus", selectAllWhenFocusing);

    if (navigator.clipboard) {
      const button = document.createElement("button");
      button.className = "btn btn-default";
      button.innerHTML = '<i class="fa fa-copy"></i>';
      const buttonContainer = document.createElement("span");
      buttonContainer.classList.add("input-group-btn");
      buttonContainer.appendChild(button);
      copybox.parentNode.appendChild(buttonContainer);
      button.addEventListener("click", function () {
        navigator.clipboard.writeText(copybox.value);
      });
    }
  });
}

document.addEventListener("turbolinks:load", setUpCopyBoxes);
