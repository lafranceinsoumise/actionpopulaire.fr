import axios from "@agir/lib/utils/axios";
import defaultAxios from "axios";

const SEARCH_URL = "/api/parrainages/chercher/";
const CODE_POSTAL_URL = "/api/parrainages/code-postal/";
const CREATE_URL = "/api/parrainages/";
const UPDATE_URL = "/api/parrainages/";

const DISCONNECTED_MESSAGE =
  "Vous n'êtes plus connectés à Action Populaire. Rechargez la page pour vours reconnecter.";

export const chercherElus = async (query, cancelToken = null) => {
  const params = new URLSearchParams([["q", query]]);

  try {
    const res = await axios.get(SEARCH_URL, {
      params,
      cancelToken: cancelToken,
      headers: { Accept: "application/json" },
    });

    return res.data;
  } catch (e) {
    if (defaultAxios.isCancel(e)) {
      return null;
    }
    throw new Error("Problème de connexion.");
  }
};

export const chercherCodePostal = async (query, cancelToken = null) => {
  const url = `${CODE_POSTAL_URL}${query}/`;

  try {
    const res = await axios.get(url, {
      cancelToken,
      headers: { Accept: "application/json" },
    });

    return res.data;
  } catch (e) {
    if (defaultAxios.isCancel(e)) {
      return null;
    }
    throw new Error("Problème de connexion.");
  }
};

export const creerRechercheParrainage = async (idElu) => {
  try {
    const res = await axios({
      method: "post",
      url: CREATE_URL,
      data: { elu: idElu },
      headers: { Accept: "application/json" },
    });

    return res.data;
  } catch (e) {
    if (e.response) {
      if (e.response.status === 403 || e.response.status === 401) {
        throw new Error(DISCONNECTED_MESSAGE);
      } else if (e.response.status === 422 || e.response.status === 400) {
        throw new Error(
          Object.keys(e.response.data)
            .map((k) => e.response.data[k])
            .join("\n"),
        );
      }
    }
    throw e;
  }
};

export const modifierParrainage = async (id, data) => {
  const url = `${UPDATE_URL}${id}/`;

  const formData = new FormData();
  for (const key of Object.keys(data)) {
    if (data[key] !== null) {
      formData.append(key, data[key]);
    }
  }
  try {
    const res = await axios({
      method: "put",
      url,
      data: formData,
      headers: {
        Accept: "application/json",
      },
    });
    return res.data;
  } catch (e) {
    if (e.response) {
      // le serveur a refusé le changement
      if (e.response.status === 403 || e.response.status === 401) {
        // personne déconnectée, on recharge la page
        throw new Error(DISCONNECTED_MESSAGE);
      } else if (e.response.status === 404) {
        throw new Error("Impossible de réaliser cette opération.");
      } else if (e.response.status === 400) {
        throw new Error(
          Object.keys(e.response.data)
            .map((k) => `${k} : ${e.response.data[k]}.`)
            .join("\n"),
        );
      }
    }
    throw e;
  }
};
