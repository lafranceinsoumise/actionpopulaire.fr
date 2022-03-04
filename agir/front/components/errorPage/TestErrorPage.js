import React from "react";

const TestErrorPage = () => {
  throw Error("Ceci est une erreur de test !");
  return <div />;
};

export default TestErrorPage;
