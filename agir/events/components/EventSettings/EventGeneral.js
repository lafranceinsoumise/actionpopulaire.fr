import PropTypes from "prop-types";
import React, { useState, useMemo, useEffect, useCallback } from "react";
import useSWR from "swr";

import { useToast } from "@agir/front/globalContext/hooks.js";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import RichTextField from "@agir/front/formComponents/RichText/RichTextField.js";
import ImageField from "@agir/front/formComponents/ImageField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Spacer from "@agir/front/genericComponents/Spacer.js";
// import HeaderPanel from "./HeaderPanel";
// import {
//   updateGroup,
//   getGroupPageEndpoint,
// } from "@agir/groups/groupPage/api.js";

// import { StyledTitle } from "./styledComponents.js";

const EventGeneral = (props) => {
  return <>EVENT GENERAL !!! </>;
};

// const EventGeneral = (props) => {
//   const { onBack, illustration, eventPk } = props;
//   const sendToast = useToast();

//     console.log("event general with pk : ", eventPk);

//   const { data: group, mutate } = useSWR(
//     // getGroupPageEndpoint("getGroup", { groupPk })
//   );

//   const [formData, setFormData] = useState({});
//   const [isLoading, setIsLoading] = useState(false);
  
//   useEffect(() => {
//   }, []);

//   return (
//     <form onSubmit={handleSubmit}>
//       {/* <HeaderPanel onBack={onBack} illustration={illustration} /> */}
//       <StyledTitle>Général</StyledTitle>

//       <Spacer size="1rem" />


//       <Spacer size="2rem" />
//       <Button color="secondary" $wrap disabled={isLoading}>
//         Enregistrer
//       </Button>
//     </form>
//   );
// };
// EventGeneral.propTypes = {
//   onBack: PropTypes.func,
//   illustration: PropTypes.string,
//   eventPk: PropTypes.string,
// };
export default EventGeneral;
