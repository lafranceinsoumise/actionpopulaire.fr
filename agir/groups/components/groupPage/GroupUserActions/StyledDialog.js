import styled from "styled-components";

const StyledDialog = styled.div`
  padding: 0 1rem;

  header {
    margin: 0;
    padding: 0;

    h3 {
      margin: 0;
      line-height: 1.5;
    }
  }

  article {
    padding: 0.75rem 0 1rem;
    font-size: 0.875rem;
    line-height: 1.5;

    strong {
      font-weight: 600;
    }
  }

  footer {
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
`;

export default StyledDialog;
