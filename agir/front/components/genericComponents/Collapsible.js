import PropTypes from "prop-types";
import React, {
  useCallback,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import styled from "styled-components";

import ExpandButton from "@agir/front/genericComponents/ExpandButton";

const StyledWrapper = styled.div`
  & > .hidden {
    ${({ collapsed }) => (collapsed ? "display: none" : "")};
  }
`;

const Collapsible = (props) => {
  const { children, maxHeight, dangerouslySetInnerHTML } = props;

  const wrapper = useRef(null);
  const [isCollapsed, setIsCollapsed] = useState(true);

  const [isHtmlString, content] = useMemo(() => {
    if (dangerouslySetInnerHTML && dangerouslySetInnerHTML.__html) {
      return [true, dangerouslySetInnerHTML.__html];
    }
    return [false, children || null];
  }, [children, dangerouslySetInnerHTML]);

  const expand = useCallback(() => {
    setIsCollapsed(false);
  }, []);

  useLayoutEffect(() => {
    if (!maxHeight || !content || !wrapper.current) {
      setIsCollapsed(false);
      return;
    }
    let children = [...wrapper.current.children];
    children.forEach((child) => {
      child.classList.remove("hidden");
    });
    let height = wrapper.current.offsetHeight;
    let shouldCollapse = false;
    while (height > maxHeight && children.length > 1) {
      children.pop().classList.add("hidden");
      height = wrapper.current.offsetHeight;
      shouldCollapse = true;
    }
    setIsCollapsed(shouldCollapse);
  }, [content, maxHeight]);

  return (
    <>
      {isHtmlString ? (
        <StyledWrapper
          ref={wrapper}
          collapsed={isCollapsed}
          dangerouslySetInnerHTML={{ __html: content }}
        />
      ) : (
        <StyledWrapper ref={wrapper} collapsed={isCollapsed}>
          {content}
        </StyledWrapper>
      )}
      {isCollapsed && <ExpandButton onClick={expand} />}
    </>
  );
};
Collapsible.propTypes = {
  children: PropTypes.node,
  dangerouslySetInnerHTML: PropTypes.shape({
    __html: PropTypes.string,
  }),
  maxHeight: PropTypes.number,
};
Collapsible.defaultProps = {
  maxHeight: 300,
};
export default Collapsible;
