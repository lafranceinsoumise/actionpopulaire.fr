import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";
import { useEventsByDay } from "@agir/events/common/hooks";
import useCopyToClipboard from "@agir/front/genericComponents/useCopyToClipboard";
import { simpleDate } from "@agir/lib/utils/time";
import { textifiyEvents } from "./common";

const StyledText = styled.p`
  margin: -0.5rem 0 1rem;
  em {
    font-style: normal;
    font-size: 0.875rem;
    color: ${({ theme }) => theme.text700};
  }
`;

const StyledPre = styled.pre`
  white-space: pre-wrap;
  font-size: 0.875rem;
  font-family: ${(props) => props.theme.fontFamilyBase};
  line-height: 1.5;
  padding: 1rem;
  border: 1px solid ${(props) => props.theme.text100};
  border-radius: ${(props) => props.theme.borderRadius};
`;

const EventTextList = ({ events, timing, displayZips }) => {
  const eventsByDay = useEventsByDay(events, (date) => simpleDate(date, false));
  const text = useMemo(
    () => textifiyEvents(eventsByDay, timing, displayZips),
    [eventsByDay, timing, displayZips],
  );
  const [isCopied, copy] = useCopyToClipboard(text);

  const handleDoubleClick = useCallback((e) => {
    const pre = e.target.closest("PRE");
    if (pre) {
      const range = new Range();
      range.setStart(pre, 0);
      range.setEnd(pre, 1);
      document.getSelection().removeAllRanges();
      document.getSelection().addRange(range);
    }
  }, []);

  if (Array.isArray(events) && events.length > 0) {
    return (
      <>
        <StyledText>
          <em>Copiez-collez ce texte dans les canaux de discussion</em>
        </StyledText>
        <Button
          block
          color={isCopied ? "success" : "secondary"}
          icon={isCopied ? "check" : "copy"}
          onClick={copy}
          disabled={!text}
        >
          {isCopied ? "Copié" : "Copier"}
        </Button>
        <StyledPre onDoubleClick={handleDoubleClick}>{text}</StyledPre>
      </>
    );
  }

  return null;
};

EventTextList.propTypes = {
  events: PropTypes.array,
  timing: PropTypes.oneOf(["week", "month"]),
  displayZips: PropTypes.bool,
};

export default EventTextList;
