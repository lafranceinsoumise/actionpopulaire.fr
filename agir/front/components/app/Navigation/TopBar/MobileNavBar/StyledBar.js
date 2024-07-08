import styled from "styled-components";

import Link from "@agir/front/app/Link";

export const IconLink = styled(Link)``;

const StyledBar = styled.div`
  width: 100%;
  height: 100%;
  background-color: ${(props) => props.theme.background0};
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;

  & > * {
    flex: 0 0 auto;
  }

  & > h1,
  & > h2 {
    margin: 0;
    padding: 0 16px;
    flex: 1 1 auto;
    text-align: center;
  }

  & > h1 {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 0;
  }

  & > h2 {
    font-size: 16px;
    line-height: 1.5;
    font-weight: 500;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow-x: hidden;
    text-align: left;
  }

  ${IconLink} {
    display: flex;
    height: 32px;
    width: 32px;
    align-items: center;
    color: ${(props) => props.theme.text1000};
    line-height: 0;
  }
`;

export default StyledBar;
