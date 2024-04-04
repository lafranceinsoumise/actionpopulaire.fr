import PropTypes from "prop-types";
import React, { useEffect } from "react";
import Helmet from "react-helmet";

import { useDispatch } from "@agir/front/globalContext/GlobalContext";
import { setPageTitle } from "@agir/front/globalContext/actions";

const DEFAULT_TYPE = "website";
const DEFAULT_TITLE = "Action Populaire";
const DEFAULT_DESCRIPTION =
  "Action Populaire est le réseau social d'action de la France insoumise.";
const DEFAULT_URL = "https://actionpopulaire.fr/";
const DEFAULT_IMAGE = "/static/front/assets/og_image_NSP.jpg";

export const usePageTitle = (title) => {
  const dispatch = useDispatch();

  useEffect(() => {
    title && dispatch(setPageTitle(title));
  }, [dispatch, title]);
};

const OpenGraphTags = (props) => {
  const {
    title,
    description = DEFAULT_DESCRIPTION,
    type = DEFAULT_TYPE,
    url = DEFAULT_URL,
    image = DEFAULT_IMAGE,
  } = props;

  const pageTitle = title ? `${title} — ${DEFAULT_TITLE}` : DEFAULT_TITLE;

  return (
    <Helmet title={pageTitle}>
      <meta property="og:locale" content="fr_FR" />
      <meta property="og:site_name" content="Action Populaire" />
      <meta property="fb:app" content="399717914004198" />
      <meta name="twitter:card" content="summary_large_image" />

      <meta name="title" content={pageTitle} />
      <meta property="og:title" content={pageTitle} />
      <meta name="twitter:title" content={pageTitle} />

      <meta name="description" content={description} />
      <meta property="og:description" content={description} />
      <meta name="twitter:description" content={description} />

      <meta property="og:url" content={url} />

      <meta property="og:type" content={type} />

      <meta property="og:image" content={image} />
      <meta property="og:image:secure_url" content={image} />
      <meta name="twitter:image" content={image} />
    </Helmet>
  );
};

OpenGraphTags.propTypes = {
  type: PropTypes.string,
  title: PropTypes.string,
  description: PropTypes.string,
  url: PropTypes.string,
  image: PropTypes.string,
};

export default OpenGraphTags;
