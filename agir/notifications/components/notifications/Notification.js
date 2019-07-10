import React from "react";
import styled from "styled-components";
import PropTypes from "prop-types";
import moment from "moment";

const NotificationBox = styled.li`
  border-top: 1px solid #bbb;
`;

const NotificationLink = styled.a`
  margin: 0;
  padding: 3px 20px;
  white-space: normal !important;
  display: flex !important;
  align-items: center;
  color: #333 !important;

  ${props =>
    props.status === "C"
      ? `
      &:hover {
        background-color: #EEE !important;
      }
      `
      : `

      background-color: rgba(0,152,182,0.20);
      &:hover {
        background-color: rgba(0,152, 182, 0.40) !important;
      }
    `}

  & p + p {
    margin-top: 5px;
  }

  p {
    margin-bottom: 0;
  }
`;

const Icon = styled.i`
  display: block;
  width: 30px;
  height: 30px;
  margin-right: 10px;
  font-size: 16px;
  line-height: 30px;
  flex-shrink: 0;
  text-align: center;

  @media (min-width: 992px) {
    color: rgba(0, 152, 182, 1);
  }
`;

const Date = styled.div`
  font-size: 0.8em;
  margin-top: 0;
  color: #888;
`;

const Notification = ({ id, created, content, icon, status, link }) => (
  <NotificationBox>
    <NotificationLink
      status={status}
      href={link}
      onClick={e => {
        e.currentTarget.href = `/notification/${id}/`;
      }}
    >
      <Icon className={"fa fa-" + icon} />
      <div>
        <div dangerouslySetInnerHTML={{ __html: content }} />
        <Date>{moment(created).fromNow()}</Date>
      </div>
    </NotificationLink>
  </NotificationBox>
);

Notification.propTypes = {
  id: PropTypes.number.isRequired,
  content: PropTypes.string.isRequired,
  created: PropTypes.string.isRequired,
  icon: PropTypes.string.isRequired,
  link: PropTypes.string.isRequired,
  status: PropTypes.string.isRequired
};

export default Notification;
