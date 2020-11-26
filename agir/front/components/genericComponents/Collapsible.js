import PropTypes from "prop-types";
import React, {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import styled from "styled-components";

import ExpandButton from "@agir/front/genericComponents/ExpandButton";

const FadingOverflowWrapper = styled.div`
  max-height: ${({ collapsed, maxHeight }) =>
    collapsed && maxHeight ? `${maxHeight}px` : "unset"};
  overflow: hidden;
  position: relative;
  font-size: 0.875rem;
  line-height: 1.6;

  &::after {
    content: "";
    display: block;
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: ${({ collapsed, maxHeight }) =>
      collapsed && maxHeight ? "30px" : "0"};
    background: linear-gradient(0deg, white 0%, transparent 200%);
  }
`;
const FadingOverflowCollapsible = (props) => {
  const { children, maxHeight, dangerouslySetInnerHTML, expanderLabel } = props;

  const wrapper = useRef(null);
  const [mayCollapse, setMayCollapse] = useState(false);
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
      setMayCollapse(false);
      return;
    }
    setMayCollapse(wrapper.current.offsetHeight > maxHeight);
  }, [content, maxHeight]);

  useEffect(() => {
    mayCollapse && setIsCollapsed(true);
  }, [mayCollapse]);

  return (
    <>
      {isHtmlString ? (
        <FadingOverflowWrapper
          ref={wrapper}
          collapsed={mayCollapse && isCollapsed}
          maxHeight={maxHeight}
          dangerouslySetInnerHTML={{ __html: content }}
        />
      ) : (
        <FadingOverflowWrapper
          ref={wrapper}
          collapsed={mayCollapse && isCollapsed}
          maxHeight={maxHeight}
        >
          {content}
        </FadingOverflowWrapper>
      )}
      {mayCollapse && isCollapsed && (
        <ExpandButton onClick={expand} label={expanderLabel} />
      )}
    </>
  );
};
FadingOverflowCollapsible.propTypes = {
  children: PropTypes.node,
  dangerouslySetInnerHTML: PropTypes.shape({
    __html: PropTypes.string,
  }),
  maxHeight: PropTypes.number,
  expanderLabel: PropTypes.string,
};
FadingOverflowCollapsible.defaultProps = {
  maxHeight: 300,
};

const StyledWrapper = styled.div`
  font-size: 0.875rem;
  line-height: 1.6;

  & > .hidden {
    ${({ collapsed }) => (collapsed ? "display: none" : "")};
  }
`;

const Collapsible = (props) => {
  const { children, maxHeight, dangerouslySetInnerHTML, expanderLabel } = props;

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
      {isCollapsed && <ExpandButton onClick={expand} label={expanderLabel} />}
    </>
  );
};
Collapsible.propTypes = {
  children: PropTypes.node,
  dangerouslySetInnerHTML: PropTypes.shape({
    __html: PropTypes.string,
  }),
  maxHeight: PropTypes.number,
  expanderLabel: PropTypes.string,
};
Collapsible.defaultProps = {
  maxHeight: 300,
};
const CollapsibleContainer = ({ fadingOverflow, ...props }) =>
  fadingOverflow ? (
    <FadingOverflowCollapsible {...props} />
  ) : (
    <Collapsible {...props} />
  );
CollapsibleContainer.propTypes = {
  fadingOverflow: PropTypes.bool,
};
CollapsibleContainer.defaultProps = {
  fadingOverflow: false,
};
export default CollapsibleContainer;
