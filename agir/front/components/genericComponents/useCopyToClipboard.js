import { useCallback, useEffect, useState } from "react";

const useCopyToClipboard = (text = "", resetInterval = 5000) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = useCallback(() => {
    if (
      typeof text !== "string" ||
      typeof window === "undefined" ||
      (typeof navigator.clipboard === "undefined" &&
        typeof document.execCommand === "undefined")
    ) {
      return;
    }

    if (typeof navigator.clipboard === "undefined") {
      const inputEl = document.createElement("input");
      inputEl.value = text;
      inputEl.width = "0";
      inputEl.height = "0";
      document.body.appendChild(inputEl);
      inputEl.select();
      setIsCopied(document.execCommand("copy"));
      document.body.removeChild(inputEl);
      return;
    }

    navigator.clipboard
      .writeText(String(text))
      .then(() => {
        setIsCopied(true);
      })
      .catch((e) => {
        setIsCopied(false);
        console.error(e.message);
      });
  }, [text]);

  useEffect(() => {
    setIsCopied(false);
  }, [text]);

  useEffect(() => {
    let timeout;
    if (isCopied && resetInterval) {
      timeout = setTimeout(() => setIsCopied(false), resetInterval);
    }
    return () => {
      clearTimeout(timeout);
    };
  }, [isCopied, resetInterval]);

  return [isCopied, handleCopy];
};

export default useCopyToClipboard;
