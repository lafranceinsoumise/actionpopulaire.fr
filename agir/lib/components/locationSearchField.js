import axios from "@agir/lib/utils/axios";

const nominatim_url = "https://nominatim.openstreetmap.org/search";

function getResults(query) {
  return axios
    .get(nominatim_url, {
      params: {
        q: query,
        format: "jsonv2",
      },
    })
    .then(function (res) {
      if (res.status === 200) {
        return res.data;
      } else {
        throw new Error("Impossible de contacter le service de localisation !");
      }
    });
}

function createLinkElement(text, handler) {
  const a = document.createElement("a");
  a.appendChild(document.createTextNode(text));
  if (handler) {
    a.href = "#";
    a.addEventListener("click", handler);
  }
  const li = document.createElement("li");
  li.appendChild(a);
  return li;
}

export default function (input) {
  const form = input.form;
  const dropdownDiv = input.parentElement;
  const resultList = document.createElement("ul");

  dropdownDiv.classList.add("dropdown");
  resultList.classList.add("dropdown-menu");

  const lonField = document.querySelector('input[name="lon"]');
  const latField = document.querySelector('input[name="lat"]');

  function setCoordinates(d) {
    lonField.value = d.lon;
    latField.value = d.lat;
  }

  const submitButton = form.querySelector('input[type="submit"]');

  document.addEventListener("click", function () {
    dropdownDiv.classList.remove("open");
  });
  dropdownDiv.addEventListener("click", function (e) {
    e.stopPropagation();
  });

  submitButton.addEventListener("click", function (event) {
    // prevent form from being submitted
    event.preventDefault();

    submitButton.disabled = true;
    const query = input.value;

    while (resultList.firstChild) {
      resultList.removeChild(resultList.firstChild);
    }

    getResults(query).then(
      function (results) {
        if (results.length === 0) {
          resultList.appendChild(createLinkElement("Pas de résultats..."));
          dropdownDiv.appendChild(resultList);
          dropdownDiv.classList.add("open");
        } else if (results.length === 1) {
          setCoordinates(results[0]);
          form.submit();
        } else {
          results.slice(0, 10).forEach(function (d) {
            resultList.appendChild(
              createLinkElement(d.display_name, function (e) {
                e.preventDefault();
                setCoordinates(d);
                input.value = d.display_name;
                form.submit();
              })
            );
          });
          dropdownDiv.appendChild(resultList);
          dropdownDiv.classList.add("open");
        }

        submitButton.disabled = false;
      },
      function (_error) {
        resultList.appendChild(
          createLinkElement(
            "Erreur de connexion au serveur de géolocalisation... Réessayez plus tard."
          )
        );
        dropdownDiv.appendChild(resultList);
        dropdownDiv.classList.add("open");
        submitButton.disabled = false;
      }
    );
  });
}

export { getResults };
