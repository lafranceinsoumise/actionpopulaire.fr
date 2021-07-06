import React, { useState, useEffect } from "react";
import styled from "styled-components";

import axios from "@agir/lib/utils/axios";
import style from "@agir/front/genericComponents/_variables.scss";
import { Hide } from "@agir/front/genericComponents/grid";

import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import img_JLM_2022 from "@agir/front/genericComponents/logos/JLM_2022.jpg";
import img_AvenirEnCommun from "@agir/front/genericComponents/logos/AvenirEnCommun.jpg";
import img_Linsoumission from "@agir/front/genericComponents/logos/Linsoumission.jpg";
import img_Comparateur from "@agir/front/genericComponents/logos/Comparateur.jpg";

import nonReactRoutes from "@agir/front/globalContext/nonReactRoutes.config";

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
  margin-top: 23px;

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
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.5rem;

  ${RawFeatherIcon} {
    margin-left: 4px;
  }
`;

const ItemActionContainer = styled.div`
  box-shadow: 0px 0px 2px rgb(0 0 0 / 50%), 0px 3px 3px rgb(0 35 44 / 10%);
  border-radius: 0.5rem;
  overflow: hidden;
  width: 340px;
  display: inline-flex;
  flex-direction: column;
  margin-right: 1.5rem;
  margin-bottom: 1rem;
  color: ${style.black1000};

  > div:first-child {
    ${({ img }) => `
      background-image: url(${img});
      background-position: center;
      background-size: cover;
      height: 190px;
    `}
  }

  > div:last-child {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    flex-grow: 1;
    height: 82px;
    overflow: hidden;
    padding: 6px 16px;
  }
`;

const ListItemAction = styled.div`
  display: flex;
  // flex-wrap: wrap;
  max-width: 100%;
  overflow-y: hidden;
  overflow-x: auto;

  div:first-child {
    margin-left: 2px;
  }
`;

const ItemWebsiteContainer = styled.div`
  display: inline-flex;
  height: 65px;
  max-width: 388px;
  width: 100%;
  border-radius: 0.5rem;
  box-shadow: 0px 0px 2px rgb(0 0 0 / 50%), 0px 3px 3px rgb(0 35 44 / 10%);
  margin-right: 1.5rem;
  margin-bottom: 1rem;
  overflow: hidden;
  color: ${style.black1000};

  > div:first-child {
    width: 113px;
    ${({ img }) => `
      background-image: url(${img});
      background-position: center;
      background-size: cover;
    `}
  }

  > div:last-child {
    flex-grow: 1;
    justify-content: center;
    align-items: center;
    display: flex;
  }
`;

const ItemAction = ({ image, title, href }) => {
  return (
    <Link href={href}>
      <ItemActionContainer img={image}>
        <div />
        <div dangerouslySetInnerHTML={{ __html: title }}></div>
      </ItemActionContainer>
    </Link>
  );
};

const LinkInfoAction = () => (
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
);

const LinkMaterial = () => (
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
);

const ItemWebsite = ({ img, href, title }) => (
  <Link href={href}>
    <ItemWebsiteContainer img={img}>
      <div />
      <div>{title}</div>
    </ItemWebsiteContainer>
  </Link>
);

const WEBSITES = [
  {
    title: "Mélenchon 2022",
    img: img_JLM_2022,
    href: nonReactRoutes.jlm2022,
  },
  {
    title: "L'avenir en commun",
    img: img_AvenirEnCommun,
    href: nonReactRoutes.programme,
  },
  {
    title: "L'insoumission",
    img: img_Linsoumission,
    href: nonReactRoutes.linsoumission,
  },
  {
    title: "Comparateur de programme",
    img: img_Comparateur,
    href: nonReactRoutes.comparateur,
  },
];

const ToolsPage = () => {
  const [categories, setCategories] = useState([]);
  const [pages, setPages] = useState([]);

  const getPagesByCategory = async (id) => {
    const url = `https://infos.actionpopulaire.fr/wp-json/wp/v2/pages?per_page=100&_fields=categories,title,link,featured_media&categories=${id}`;
    const { data } = await axios.get(url);

    // Add featured image to pages
    let pages = [];
    let requests = data.map(async (p) => {
      const imageUrl = `https://infos.actionpopulaire.fr/wp-json/wp/v2/media/${p.featured_media}`;
      return axios.get(imageUrl).then((res) => {
        pages.push({
          ...p,
          img: res.data.guid.rendered,
          title: p.title.rendered,
        });
      });
    });

    return Promise.all(requests).then(() => {
      return pages;
    });
  };

  const getWPCategories = async () => {
    // TODO: filter by categories in query possible ?
    const url =
      "https://infos.actionpopulaire.fr/wp-json/wp/v2/categories/?per_page=100";
    let { data } = await axios.get(url);

    // Get only categories 15, 16, 17
    data = data.filter((e) => ([15, 16, 17].includes(e.id) ? e : null));
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
          <LinkMaterial />
        </Hide>
      </BlockTitle>

      <BlockContent></BlockContent>

      <Hide over>
        <LinkMaterial />
      </Hide>

      <Hide over>
        <hr />
      </Hide>

      <BlockTitle>
        <div>
          <RawFeatherIcon name="book-open" color={style.black1000} />
          <Title>Se former à l'action</Title>
        </div>

        <Hide under>
          <LinkInfoAction />
        </Hide>
      </BlockTitle>

      <BlockContent>
        {categories.map((category) => (
          <>
            <Subtitle key={category.id}>{category.name}</Subtitle>

            <ListItemAction>
              {pages[category.id]?.map((page) => (
                <ItemAction
                  image={page.img}
                  title={page.title}
                  href={page.link}
                />
              ))}
            </ListItemAction>
          </>
        ))}
      </BlockContent>

      <Hide over>
        <LinkInfoAction />
      </Hide>

      <Hide over>
        <hr />
      </Hide>

      <BlockTitle>
        <div>
          <RawFeatherIcon name="mouse-pointer" color={style.black1000} />
          <Title>Je m'informe en ligne</Title>
        </div>
      </BlockTitle>

      <BlockContent>
        {WEBSITES.map((w) => (
          <ItemWebsite img={w.img} href={w.href} title={w.title} />
        ))}
      </BlockContent>

      <Hide over>
        <hr />
      </Hide>

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
