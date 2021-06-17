import { useCallback, useEffect, useState } from "react";
import { useCopyToClipboard as useCTC } from "react-use";

const useCopyToClipboard = (text = "", resetInterval = 5000) => {
  const [isCopied, setIsCopied] = useState(false);
  const [state, copyToClipboard] = useCTC();
  const { error } = state;

  const handleCopy = useCallback(() => {
    if (text) {
      copyToClipboard(text);
      setIsCopied(true);
    }
  }, [text, copyToClipboard]);

  useEffect(() => {
    setIsCopied(false);
  }, [text]);

  useEffect(() => {
    error && console.error(error?.message);
  }, [error]);

  useEffect(() => {
    let timeout;
    if (isCopied && resetInterval) {
      timeout = setTimeout(() => setIsCopied(false), resetInterval);
    }
    return () => {
      clearTimeout(timeout);
    };
  }, [isCopied, resetInterval, copyToClipboard]);

  return [isCopied, handleCopy];
};

export default useCopyToClipboard;
