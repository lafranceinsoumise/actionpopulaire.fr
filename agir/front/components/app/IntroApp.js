import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import clamp from "lodash/clamp";
import { useSprings, animated } from "@react-spring/web";
import { useDrag } from "@use-gesture/react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import img1 from "@agir/front/genericComponents/images/introApp1.jpg";
import img2 from "@agir/front/genericComponents/images/introApp2.jpg";
import img3 from "@agir/front/genericComponents/images/introApp3.jpg";
import logo from "@agir/front/genericComponents/logos/action-populaire-logo.svg";

const Mark = styled.span`
  width: 1.5rem;
  height: 0.25rem;
  margin: 0.188rem;
  display: inline-block;
  transition: background-color 0.5s ease-in-out;
  background-color: ${(props) =>
    props.$active ? style.primary500 : style.black200};
`;

const WhiteTriangle = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none;

  &:before {
    content: "";
    display: block;
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 100%;
    background-color: #fff;
    height: 80px;
    clip-path: polygon(0px 100%, 100% 0px, 100% 100%, 0px 100%);
  }
`;

const StyledHeader = styled.header`
  position: relative;
`;

const StyledHeaderImage = styled(animated.div)`
  position: absolute;
  background-image: url(${({ $image }) => $image || logo});
  background-color: ${style.secondary500};
  background-size: ${({ $image }) => ($image ? "cover" : "210px auto")};
  background-position: center;
  background-repeat: no-repeat;
  width: 100%;
  height: 100%;
  will-change: transform;

  @media (max-height: 600px) {
    background-size: ${({ $image }) => ($image ? "cover" : "150px auto")};
  }
`;

const StyledMain = styled.main``;
const StyledMainContent = styled(animated.p)`
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  will-change: transform;
  padding: 1rem 2rem;
  font-size: 1rem;
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  justify-content: center;

  span,
  strong {
    display: block;
  }

  strong {
    color: ${style.primary500};
    font-weight: 700;
    font-size: 1.75em;
  }

  span {
    font-size: 1.2em;
    margin-top: 0.375rem;
  }

  @media (max-height: 600px) {
    font-size: 0.813rem;
  }
`;
const StyledActions = styled.div``;
const StyledFooter = styled.footer``;

const StyledButton = styled(Button)`
  max-width: 100%;
  width: 330px;
  height: 70px;
  font-size: 20px;
  margin-top: 2rem;
`;

const StyledSearchLink = styled(Link)`
  max-width: 100%;
  width: 330px;
  height: 70px;
  font-size: 20px;
  justify-content: center;
  margin-top: 0.5rem;
  font-size: 1rem;
  display: flex;
  align-items: center;

  &,
  &:hover,
  &:focus {
    color: ${style.black1000};
  }

  ${RawFeatherIcon} {
    margin-right: 0.5rem;
  }
`;

const StyledWrapper = styled.div`
  position: fixed;
  top: 0;
  z-index: ${style.zindexTopBar + 1};
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  flex-flow: column nowrap;
  text-align: center;
  justify-content: space-between;
  touch-action: none;

  & > * {
    flex: 0 0 auto;
    width: 100%;
  }

  ${StyledHeader} {
    flex: 0 1 calc(100vh - 358px);
    min-height: 290px;
  }

  ${StyledMain} {
    position: relative;
    width: 100%;
    flex: 1 1 200px;
  }

  ${StyledActions} {
    padding: 0 2rem;
    margin-top: auto;
    display: flex;
    flex-flow: column nowrap;
    justify-content: center;
    align-items: center;
  }

  ${StyledFooter} {
    display: flex;
    flex-flow: column nowrap;
    justify-content: center;
    align-items: center;
  }
`;

const items = [
  {
    header: img1,
    title: "Rencontrez",
    body: <>d'autres membres et agissez ensemble&nbsp;!</>,
  },
  {
    header: img2,
    title: "Agissez concrètement",
    body: (
      <>
        participez aux actions, diffusez notre programme et commandez du
        matériel
      </>
    ),
  },
  {
    header: img3,
    title: "Rejoignez ou créez",
    body: "un groupe d'action autour de vous !",
  },
  {},
];

const useImageLoad = () => {
  const loadedCount = useRef(0);
  const [isReady, setIsReady] = useState(false);
  const images = useMemo(
    () => items.map((item) => item.header).filter(Boolean),
    [],
  );
  useEffect(() => {
    const onReady = () => {
      loadedCount.current += 1;
      if (loadedCount.current === images.length) {
        setIsReady(true);
      }
    };
    const placeholders = images.map((picture) => {
      const img = new Image();
      img.addEventListener("load", onReady);
      img.src = picture;
      return img;
    });

    return () => {
      placeholders.forEach((picture) => {
        picture.removeEventListener("load", onReady);
      });
    };
  }, [images]);

  return isReady;
};

const IntroApp2 = () => {
  const isReady = useImageLoad();
  const [itemIndex, setItemIndex] = useState(0);
  const index = useRef(0);

  const [transitions, set] = useSprings(items.length, (i) => ({
    x: i * window.innerWidth,
    visibility: "visible",
  }));

  const handleNext = useCallback(() => {
    setItemIndex((state) => state + 1);
  }, []);

  const handleChange = useCallback((index) => {
    setItemIndex(index);
  }, []);

  const handleSet = useCallback(
    (active = false, xMovement = 0) => {
      set((i) => {
        if (i < index.current - 1 || i > index.current + 1) {
          return { visibility: "hidden" };
        }
        const x =
          (i - index.current) * window.innerWidth + (active ? xMovement : 0);
        return { x, visibility: "visible" };
      });
    },
    [set],
  );

  const bind = useDrag(
    ({
      active,
      movement: [xMovement],
      direction: [xDirection],
      distance: [xDistance],
      cancel,
    }) => {
      if (active && xDistance > window.innerWidth / 5) {
        const newIndex = clamp(
          index.current + (xDirection > 0 ? -1 : 1),
          0,
          items.length - 1,
        );
        index.current = newIndex;
        setItemIndex(newIndex);
        cancel(newIndex);
      }
      handleSet(active, xMovement);
    },
  );

  useEffect(() => {
    index.current = itemIndex;
    handleSet();
  }, [itemIndex, handleSet]);

  const isLast = !items[itemIndex + 1];

  return (
    <PageFadeIn ready={isReady}>
      <StyledWrapper {...bind()}>
        <StyledHeader>
          {transitions.map(({ x, display }, i) => {
            const { header } = items[i] || {};
            return (
              <StyledHeaderImage
                key={i}
                $image={header}
                style={{
                  display,
                  transform: x.interpolate((x) => `translate3d(${x}px,0,0)`),
                }}
              />
            );
          })}
          <WhiteTriangle />
        </StyledHeader>

        <StyledMain>
          {transitions.map(({ x, display }, i) => {
            const { title = null, body = null } = items[i] || {};
            return (
              <StyledMainContent
                key={i + "main"}
                style={{
                  display,
                  transform: x.interpolate((x) => `translate3d(${x}px,0,0)`),
                }}
              >
                {title && body ? (
                  <>
                    <strong>{title}</strong>
                    <span>{body}</span>
                  </>
                ) : (
                  <>
                    <StyledButton
                      color="primary"
                      link
                      route="signup"
                      style={{ marginTop: "0" }}
                    >
                      Je crée mon compte
                    </StyledButton>
                    <StyledButton
                      color="secondary"
                      style={{ marginTop: "0.5rem", marginLeft: "0px" }}
                      link
                      route="login"
                    >
                      Je me connecte
                    </StyledButton>
                  </>
                )}
              </StyledMainContent>
            );
          })}
        </StyledMain>

        <StyledActions>
          {isLast ? (
            <StyledSearchLink route="search">
              <RawFeatherIcon
                name="search"
                width="1rem"
                height="1rem"
                strokeWidth={2}
              />
              <span>Rechercher une action</span>
            </StyledSearchLink>
          ) : (
            <StyledButton color="secondary" onClick={handleNext}>
              Continuer
            </StyledButton>
          )}
        </StyledActions>

        <StyledFooter>
          {!isLast && (
            <div style={{ marginTop: "2rem" }}>
              {[0, 1, 2].map((i) => (
                <Mark
                  key={i}
                  $active={i === itemIndex}
                  onClick={() => handleChange(i)}
                />
              ))}
            </div>
          )}
        </StyledFooter>
      </StyledWrapper>
    </PageFadeIn>
  );
};

export default IntroApp2;
