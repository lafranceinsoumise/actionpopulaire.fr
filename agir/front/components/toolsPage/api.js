import useSWR from "swr";

const WP_API_URL = "https://infos.actionpopulaire.fr/wp-json/wp/v2/";
const WP_PAGE_URL = `${WP_API_URL}pages?per_page=100&&_embed=wp:term,wp:featuredmedia`;
const CATEGORY_LIST = [15, 16, 17];

/** return [categories, pages] */
export const useWPPagesAndCategories = () => {
  const { data } = useSWR(
    `${WP_PAGE_URL}&categories=${CATEGORY_LIST.toString()}`,
    {
      revalidateOnFocus: false,
      refreshInterval: 0,
      refreshWhenHidden: false,
    }
  );

  let categories = [];
  const pages = data?.reduce((pagesSorted, page) => {
    const page_categories = page._embedded["wp:term"];
    const filtered_categories = page_categories.reduce((res, cat) => {
      const cat_filtered = cat.filter(
        (c) => c.taxonomy === "category" && CATEGORY_LIST.includes(c.id),
        []
      );
      return [...res, ...cat_filtered];
    }, []);

    // Add to category list
    const category = filtered_categories[0];
    categories[category.id] = { id: category.id, name: category.name };

    let title = page.title.rendered;
    if (title.length > 56) title = title.slice(0, 56) + "...";

    const embed = page._embedded["wp:featuredmedia"][0];
    const medias = embed.media_details?.sizes;
    const media = medias.medium_large || medias.medium || medias.large || embed;
    const image = media.source_url;

    const p = {
      id: page.id,
      title: title,
      img: image,
      link: page.link,
      category_id: category.id,
      category_name: category.name,
    };

    if (!pagesSorted[category.id]) pagesSorted[category.id] = [p];
    else pagesSorted[category.id].push(p);

    return pagesSorted;
  }, []);

  return [categories, pages];
};
