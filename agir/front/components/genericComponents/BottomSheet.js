import PropTypes from "prop-types";
import React, {
  useCallback,
  useEffect,
  useRef,
  useState,
  Suspense,
} from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { lazy } from "@agir/front/app/utils";

const RSBS = lazy(() => import("./ReactSpringBottomSheet"));

const StyledBottomSheetFooter = styled.footer`
  &::before {
    content: "";
    display: block;
    width: calc(100% - 3rem);
    height: 1px;
    margin: 0 auto;
    background-color: ${style.black200};
  }

  button {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: white;
    box-shadow: none;
    border: none;
    height: 54px;
    font-size: 0.875rem;
    width: 100%;
    cursor: pointer;
  }
`;
const StyledBottomSheet = styled(RSBS)`
  [data-rsbs-overlay] {
    z-index: ${style.zindexPanel};
  }
  [data-rsbs-backdrop] {
    z-index: ${style.zindexPanel};
    background-color: rgba(0, 10, 44, 0.6);
  }
  [data-rsbs-footer] {
    padding: 0;
    box-shadow: none;
  }
`;

export const BottomSheet = (props) => {
  const { isOpen, onDismiss, shouldDismissOnClick, children } = props;
  const [isReady, setIsReady] = useState(false);
  const contentRef = useRef();

  const handleSpringStart = useCallback(
    (e) => {
      let content = contentRef.current;
      if (!content || !shouldDismissOnClick) {
        return;
      }
      const targets = content.querySelectorAll("a, button");
      if (e.type === "OPEN") {
        targets.forEach((element) => {
          element.addEventListener("click", onDismiss);
        });
      }
      if (e.type === "CLOSE") {
        targets.forEach((element) => {
          element.removeEventListener("click", onDismiss);
        });
      }
    },
    [onDismiss, shouldDismissOnClick],
  );

  useEffect(() => {
    isOpen && !isReady && setIsReady(true);
  }, [isOpen, isReady]);

  return (
    <Suspense fallback={null}>
      {isReady && (
        <StyledBottomSheet
          open={isOpen}
          onDismiss={onDismiss}
          onSpringStart={handleSpringStart}
          defaultSnap={({ minHeight }) => minHeight}
          snapPoints={({ maxHeight }) => [
            2 * (maxHeight / 3),
            maxHeight - maxHeight / 10,
            maxHeight / 3,
          ]}
          footer={
            <StyledBottomSheetFooter>
              <button onClick={onDismiss}>Fermer</button>
            </StyledBottomSheetFooter>
          }
        >
          <div ref={contentRef}>{children}</div>
        </StyledBottomSheet>
      )}
    </Suspense>
  );
};

BottomSheet.propTypes = {
  isOpen: PropTypes.bool,
  onDismiss: PropTypes.func,
  shouldDismissOnClick: PropTypes.bool,
  children: PropTypes.node,
};
export default BottomSheet;
