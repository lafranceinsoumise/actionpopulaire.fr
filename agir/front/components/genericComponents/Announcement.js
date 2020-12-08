import PropTypes from "prop-types";
import React, { useCallback, useRef } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

const Image = styled.div`
  flex: 0 0 130px;
  width: 100%;
  background-repeat: no-repeat;
  background-size: 0 0, cover;
  background-position: center center;
  border-radius: 8px;

  @media (max-width: ${style.collapse}px) {
    flex: 0 0 80px;
    height: 80px;
    border-radius: 0;
    background-size: cover, 0 0;
  }
`;

const Container = styled.article`
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  justify-content: flex-start;
  max-width: 255px;
  cursor: ${({ isClickable }) => (isClickable ? "pointer" : "default")};

  & + & {
    margin-top: 1.5rem;
  }

  div + div {
    margin-top: 1rem;
  }

  h3,
  p {
    line-height: 1.45;
    overflow: hidden;
  }

  h3 {
    display: block;
    margin: 0;
    margin-bottom: 0.125rem;
    font-size: 0.875rem;
    font-weight: 700;
    color: ${style.primary500};

    a,
    span {
      color: inherit;
    }
  }

  p {
    font-size: 0.75rem;
  }

  @media (max-width: ${style.collapse}px) {
    flex-flow: row nowrap;
    background-color: ${style.primary500};
    padding: 1rem;
    border-radius: 4px;
    max-width: 100%;
    height: 112px;

    & + & {
      margin-top: 0;
    }

    div {
      max-height: 72px;
      overflow: hidden;
    }

    div + div {
      margin-top: 0;
      margin-left: 1rem;
    }

    h3,
    p {
      color: white;
    }
  }
`;

const Announcement = (props) => {
  const { title, content, image, link } = props;
  const linkRef = useRef(null);
  const handleClick = useCallback(() => {
    linkRef.current && linkRef.current.click();
  }, []);
  return (
    <Container isClickable={!!link} onClick={handleClick}>
      {image && image.mobile && image.desktop ? (
        <Image
          aria-label={title}
          style={{
            backgroundImage: `url(${image.mobile}), url(${image.desktop})`,
          }}
        />
      ) : null}
      <div>
        <h3>
          {link ? (
            <a ref={linkRef} href={link}>
              {title}
            </a>
          ) : (
            <span>{title}</span>
          )}
        </h3>
        <p dangerouslySetInnerHTML={{ __html: content }} />
      </div>
    </Container>
  );
};

Announcement.propTypes = {
  title: PropTypes.string.isRequired,
  content: PropTypes.string.isRequired,
  image: PropTypes.shape({
    desktop: PropTypes.string.isRequired,
    mobile: PropTypes.string.isRequired,
  }),
  link: PropTypes.string,
};

export default Announcement;
