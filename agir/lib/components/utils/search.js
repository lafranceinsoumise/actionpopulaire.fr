import _merge from "lodash/merge";
import MiniSearch from "minisearch";
import { useEffect, useMemo, useState } from "react";

const removeAccents = (str) =>
  str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");

export const DEFAULT_OPTIONS = {
  extractField: (document, fieldName) => {
    let text = document[fieldName];
    const doc = new DOMParser().parseFromString(text, "text/html");
    text = doc.body.textContent || text;
    text = removeAccents(text.toLowerCase());

    return text;
  },
  processTerm: (term, _fieldName) => removeAccents(term.toLowerCase()),
  searchOptions: {
    prefix: true,
    fuzzy: 0.2,
  },
};

export const useMiniSearch = (documents, options = {}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);

  const miniSearch = useMemo(
    () => {
      const opts = _merge(DEFAULT_OPTIONS, options);
      return new MiniSearch(opts);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const matchingDocuments = useMemo(
    () =>
      searchResults.map((doc) => ({
        ...documents.find((d) => d.id === doc.id),
        ...doc,
      })),
    [documents, searchResults],
  );

  useEffect(() => {
    miniSearch.removeAll();
    miniSearch.addAll(documents);
  }, [miniSearch, documents]);

  useEffect(() => {
    setSearchResults(miniSearch.search(searchTerm || MiniSearch.wildcard));
  }, [miniSearch, searchTerm]);

  return [searchTerm, setSearchTerm, matchingDocuments];
};
