import axios from "@agir/lib/utils/axios";

const WP_API_URL = "https://infos.actionpopulaire.fr/wp-json/wp/v2/";
const WP_CATEGORIES_URL = `${WP_API_URL}categories/?per_page=100`;
const WP_PAGE_URL = `${WP_API_URL}pages?per_page=100&_fields=categories,title,link,featured_media`;
const WP_MEDIA_URL = `${WP_API_URL}media/`;

const getPagesByCategory = async (id) => {
  const { data: pages } = await axios.get(`${WP_PAGE_URL}&categories=${id}`);
  const requests = pages.map(async (page) => {
    const { data: media } = await axios.get(
      `${WP_MEDIA_URL}${page.featured_media}`
    );
    return {
      category_id: id,
      ...page,
      img: media?.guid?.rendered,
      title: page?.title?.rendered,
    };
  });
  return await Promise.all(requests);
};

export const getWPCategories = async () => {
  const { data: categories } = await axios.get(
    `${WP_CATEGORIES_URL}&include=15,16,17`
  );

  const requests = categories.map((category) =>
    getPagesByCategory(category.id)
  );
  const responses = await Promise.all(requests);

  const pages = responses.reduce((pagesSorted, page) => {
    pagesSorted[page[0].category_id] = page;
    return pagesSorted;
  }, []);
  return [categories, pages];
};
