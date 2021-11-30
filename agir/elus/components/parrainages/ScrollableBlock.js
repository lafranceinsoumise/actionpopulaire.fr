/**
 * Une boîte avec défilement vertical
 *
 * L'intérêt de ce composant est que sa taille n'est pas influencée par son contenu, et qu'il peut donc être
 * dimensionné de façon purement externe.
 *
 * À l'inverse, le contenu peut être dimensionné en fonction du contenant.
 *
 * Il est réalisé en emboîtant deux éléments div : un élément interne positionné absolument, inséré dans un élément
 * externe avec un positionnement relatif, pour servir lui servir de bloc englobant. L'élément interne prend ainsi toute
 * la largeur et la hauteur du bloc englobant, mais sans influer sur sa taille.
 */

import React from "react";
import styled from "styled-components";
import PropTypes from "prop-types";

const ScrollableBlockLayout = styled.div`
  position: relative;

  & > div {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;

    overflow-y: scroll;
  }
`;

const ScrollableBlock = ({ children, ...props }) => (
  <ScrollableBlockLayout {...props}>
    <div>{children}</div>
  </ScrollableBlockLayout>
);
ScrollableBlock.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]),
};
ScrollableBlock.Layout = ScrollableBlockLayout;

export default ScrollableBlock;
