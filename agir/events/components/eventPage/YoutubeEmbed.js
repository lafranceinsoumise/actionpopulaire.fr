import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

const StyledEmbed = styled.div`
  overflow: hidden;
  padding-bottom: 56.25%;
  position: relative;
  height: 0;
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.text50};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    border-radius: 0;
  }

  iframe {
    left: 0;
    top: 0;
    height: 100%;
    width: 100%;
    position: absolute;
  }
`;

const YoutubeEmbed = ({ id }) => (
  <StyledEmbed>
    <iframe
      width="796"
      height="450"
      src={`https://www.youtube.com/embed/${id}`}
      frameBorder="0"
      allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
      title="Video YouYube"
    />
  </StyledEmbed>
);

YoutubeEmbed.propTypes = {
  id: PropTypes.string.isRequired,
};

export default YoutubeEmbed;
