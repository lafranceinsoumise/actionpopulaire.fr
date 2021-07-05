import React, { useState, useEffect } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import axios from "@agir/lib/utils/axios";
import { Hide } from "@agir/front/genericComponents/grid";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const Container = styled.div`
  padding: 25px 85px;

  @media (max-width: ${style.collapse}px) {
    padding: 20px;
  }
`;

const BlockTitle = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 23px;

  > div:first-child {
    display: flex;
    align-items: center;
  }

  ${RawFeatherIcon} {
    margin-right: 6px;
  }
`;

const BlockContent = styled.div`
  margin-bottom: 20px;
`;

const Title = styled.div`
  font-weight: 700;
  font-size: 26px;
`;

const Subtitle = styled.div`
  font-weight: 600;
  font-size: 1rem;
  margin: 20px 0;
`;

const StyledButton = styled(Button)`
  height: 40px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 0.5rem;
`;

const ItemActionContainer = styled(Button)`
  border-radius: 4px;
  border: 1px solid black;

  // background-image
  background-color: blue;
  width: 100%;
  height: 240px;
`;

const ItemAction = ({ image, description }) => {
  return (
    <ItemActionContainer>
      <div>image background : {image}</div>
      <div>{description}</div>
    </ItemActionContainer>
  );
};

const ToolsPage = () => {
  const [categories, setCategories] = useState([]);
  const [pages, setPages] = useState([]);

  const getPagesByCategory = async (id) => {
    const url = `https://infos.actionpopulaire.fr/wp-json/wp/v2/pages?per_page=100&categories=${id}`;
    const { data } = await axios.get(url);
    return data;
  };

  const getWPCategories = async () => {
    const url =
      "https://infos.actionpopulaire.fr/wp-json/wp/v2/categories/?per_page=100";
    const { data } = await axios.get(url);
    setCategories(data);

    // Fill Pages by categories
    let pagesSorted = [];
    let requests = data.map(async (c) => {
      return getPagesByCategory(c.id).then((data) => {
        pagesSorted[c.id] = data;
      });
    });

    Promise.all(requests).then(() => {
      setPages(pagesSorted);
    });
  };

  useEffect(() => {
    getWPCategories();
  }, []);

  return (
    <Container>
      <BlockTitle>
        <div>
          <RawFeatherIcon name="shopping-bag" color={style.black1000} />
          <Title>Commandez du matériel</Title>
        </div>

        <Hide under>
          <StyledButton
            small
            as="Link"
            color="secondary"
            href="https://materiel.lafranceinsoumise.fr/"
            target="_blank"
          >
            Accéder au site matériel
            <RawFeatherIcon
              name="arrow-up-right"
              color={style.black1000}
              width="1.25rem"
            />
          </StyledButton>
        </Hide>
      </BlockTitle>

      <BlockContent></BlockContent>

      <BlockTitle>
        <div>
          <RawFeatherIcon name="book-open" color={style.black1000} />
          <Title>Se former à l'action</Title>
        </div>

        <Hide under>
          <StyledButton
            small
            as="Link"
            color="secondary"
            href="https://materiel.lafranceinsoumise.fr/"
            target="_blank"
          >
            Accéder au fiches pratiques
            <RawFeatherIcon
              name="arrow-up-right"
              color={style.black1000}
              width="1.25rem"
            />
          </StyledButton>
        </Hide>
      </BlockTitle>

      <BlockContent>
        {/* <Subtitle>Actions rapides en quelques clics !</Subtitle> */}

        {categories.map((category) => (
          <>
            <Subtitle key={category.id}>{category.name}</Subtitle>

            {pages[category.id]?.map((page) => (
              <>
                {page?.title?.rendered}
                <br />
              </>
            ))}
          </>
        ))}

        <ItemAction image="" description="Titre d'action" />
      </BlockContent>

      <BlockTitle>
        <div>
          <RawFeatherIcon name="mouse-pointer" color={style.black1000} />
          <Title>Je m'informe en ligne</Title>
        </div>
      </BlockTitle>

      <BlockContent></BlockContent>

      <BlockTitle>
        <div>
          <RawFeatherIcon name="help-circle" color={style.black1000} />
          <Title>Besoin d'aide ?</Title>
        </div>
      </BlockTitle>

      <BlockContent></BlockContent>
    </Container>
  );
};

export default ToolsPage;
