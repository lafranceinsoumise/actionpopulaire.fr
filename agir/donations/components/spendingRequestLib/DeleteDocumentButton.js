import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import Modal from "lib/bootstrap/Modal";
import Button from "lib/bootstrap/Button";
import { getCookie } from "lib/utils/cookies";

const Centerer = styled.div`
  display: flex;
  justify-content: center;
`;

const Spacer = styled.div`
  margin: 1em;
`;

class DeleteDocumentButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = { modalShown: false };
  }

  render() {
    return (
      <React.Fragment>
        <Button onClick={() => this.setState({ modalShown: true })}>
          <span className="fa fa-trash" />
        </Button>
        <Modal
          show={this.state.modalShown}
          onHide={() => this.setState({ modalShown: false })}
          title={`Voulez-vous vraiment supprimer le document ${
            this.props.documentName
          } ?`}
        >
          <Modal.Body>
            <form method="post" action={this.props.deleteUrl}>
              <input
                type="hidden"
                name="csrfmiddlewaretoken"
                value={getCookie("csrftoken")}
              />
              <Centerer>
                <Spacer>
                  <Button type="submit" bsStyle="danger">
                    Oui
                  </Button>
                </Spacer>
                <Spacer>
                  <Button onClick={() => this.setState({ modalShown: false })}>
                    Non
                  </Button>
                </Spacer>
              </Centerer>
            </form>
          </Modal.Body>
        </Modal>
      </React.Fragment>
    );
  }
}

DeleteDocumentButton.propTypes = {
  documentName: PropTypes.string,
  deleteUrl: PropTypes.string
};

export default DeleteDocumentButton;
