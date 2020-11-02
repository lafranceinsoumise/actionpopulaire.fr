import { useState, useCallback, useEffect } from "react";

const useCopyToClipboard = (text = "", resetInterval = 5000) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = useCallback(() => {
    if (
      typeof navigator.clipboard === "undefined" ||
      typeof text !== "string"
    ) {
      setIsCopied(false);
      console.error(`Cannot copy ${typeof text} to clipboard.`);
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
