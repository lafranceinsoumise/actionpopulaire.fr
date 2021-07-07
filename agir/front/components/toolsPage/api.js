import axios from "@agir/lib/utils/axios";

const WP_API_URL = "https://infos.actionpopulaire.fr/wp-json/wp/v2/";
const WP_CATEGORIES_URL = `${WP_API_URL}categories/?per_page=100`;
const WP_PAGE_URL = `${WP_API_URL}pages?per_page=100&_fields=categories,title,link,featured_media`;
const WP_MEDIA_URL = `${WP_API_URL}media/`;

const getPagesByCategory = async (id) => {
  const { data: pages } = await axios.get(`${WP_PAGE_URL}&categories=${id}`);
  const requests = pages.map(async (p) => {
    const { data: media } = await axios.get(
      `${WP_MEDIA_URL}${p.featured_media}`
    );
    return {
      category_id: id,
      ...p,
      img: media?.guid?.rendered,
      title: p?.title?.rendered,
    };
  });
  const responses = await Promise.all(requests);
  return responses;
};

export const getWPCategories = async () => {
  // TODO: filter by category ids in query possible ?
  let { data: categories } = await axios.get(WP_CATEGORIES_URL);

  // Keep only 3 categories
  categories = categories.filter((e) => [15, 16, 17].includes(e.id));
  const requests = categories.map((c) => getPagesByCategory(c.id));
  const responses = await Promise.all(requests);

  const pages = responses.reduce((pagesSorted, page) => {
    pagesSorted[page[0].category_id] = page;
    return pagesSorted;
  }, []);
  return [categories, pages];
};
