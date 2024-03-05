import { http, HttpResponse, delay } from "msw";
import React from "react";

import MessageCard from "./MessageCard";

const mockComments = {
  count: 3,
  previous: null,
  next: null,
  results: [
    {
      id: "comment-0",
      author: {
        id: "Isabelle",
        displayName: "Isabelle Guérini",
      },
      text: "Est-ce que c’est possible de commencer un peu plus tard ? Ma fille termine le karaté et j’arriverai à la maison tout juste...",
      created: "2021-01-09 12:30:00",
      attachment: null,
    },
    {
      id: "comment-1",
      author: {
        id: "Isabelle",
        displayName: "Isabelle Guérini",
      },
      text: "Est-ce que c’est possible de commencer un peu plus tard ?\n\nMa fille termine le karaté et j’arriverai à la maison tout juste...",
      created: "2022-01-09 12:30:00",
      attachment: {
        name: "document.pdf",
        file: "https://picsum.photos/640/360",
      },
    },
    {
      id: "comment-2",
      author: {
        id: "Isabelle",
        displayName: "Isabelle Guérini",
      },
      text: "Est-ce que c’est possible de commencer un peu plus tard ?\n\nMa fille termine le karaté et j’arriverai à la maison tout juste...",
      created: "2023-01-09 12:30:00",
      attachment: {
        name: "image.jpg",
        file: "https://picsum.photos/640/360",
      },
    },
  ],
};

export default {
  component: MessageCard,
  title: "Generic/MessageCard",
  parameters: {
    layout: "padded",
    msw: {
      handlers: [
        http.get("/api/groupes/messages/:message/comments/", ({ params }) => {
          delay("real");
          return HttpResponse.json(
            params.message === "no-comment"
              ? { count: 0, results: [] }
              : mockComments,
          );
        }),
        http.get("/api/groupes/messages/:message/participants/", () => {
          delay("real");
          return HttpResponse.json({
            total: 1789,
            active: [
              {
                id: "Bill",
                displayName: "Bill Murray",
                image: "https://loremflickr.com/200/200",
                isAuthor: true,
              },
            ],
          });
        }),
      ],
    },
  },
};

const Template = (args) => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [comments, setComments] = React.useState(args.comments);
  const handleDeleteComment = React.useCallback(async (comment) => {
    setIsLoading(true);
    await new Promise((resolve) => {
      setTimeout(() => {
        setComments((state) => state.filter((m) => m.id !== comment.id));
        setIsLoading(false);
        resolve();
      }, 2000);
    });
  }, []);
  const handleComment = React.useCallback(
    async (messageContent) => {
      setIsLoading(true);
      await new Promise((resolve) => {
        setTimeout(() => {
          setComments((state) => [
            ...state,
            {
              text: messageContent,
              author: args.user,
              id: String(Date.now()),
              created: new Date().toUTCString(),
            },
          ]);
          setIsLoading(false);
          resolve();
        }, 2000);
      });
    },
    [args.user],
  );
  return (
    <MessageCard
      {...args}
      onDeleteComment={handleDeleteComment}
      onComment={handleComment}
      comments={comments}
      isLoading={isLoading}
    />
  );
};

export const Default = Template.bind({});
Default.args = {
  user: {
    id: "Bill",
    displayName: "Bill Murray",
    image: "https://loremflickr.com/200/200",
  },
  messageURL: "#message",
  groupURL: "#group",
  message: {
    id: "message",
    created: "2021-01-09 12:00:00",
    group: {
      name: "Comités d'appui et de travail pour une Vienne Insoumise",
    },
    author: {
      id: "Bill",
      displayName: "Bill Murray",
      image: "https://loremflickr.com/200/200",
    },
    text: "Bonjour à tous les nouveaux membres ! Pour que tout le monde puisse vous connaître, je vous propose qu’on se rejoigne ensemble sur Zoom vendredi vers 20h.\n\nEst-ce que l’horaire convient à tout le monde ?",
    linkedEvent: {
      id: "12343432423",
      name: "Cortège France insoumise à la marche contre la fourrure 2020",
      rsvp: "CO",
      startTime: "2021-01-15 12:00:00",
      endTime: "2021-01-15 15:00:00",
      duration: 2,
      locationName: "Place de la République",
      locationAddress: "Place de la République\n75011 Paris",
      shortLocation: "Place de la République, 75011, Paris",
      routes: {
        join: "#join",
        cancel: "#cancel",
        compteRendu: "#compteRendu",
        details: "#details",
      },
      groups: [{ id: "A", name: "Groupe d'action 1" }],
    },
  },
};

export const NoComments = Template.bind({});
NoComments.args = {
  ...Default.args,
  message: {
    ...Default.args.message,
    id: "no-comment",
  },
};

export const NoEvent = Template.bind({});
NoEvent.args = {
  ...Default.args,
  message: {
    ...Default.args.message,
    linkedEvent: null,
  },
};

export const MultilineMessage = Template.bind({});
MultilineMessage.args = {
  ...Default.args,
  message: {
    ...Default.args.message,
    text: `
      Un message
      sur
      plusieurs lignes.
      Point.
    `,
  },
};

export const WithAttachment = Template.bind({});
WithAttachment.args = {
  ...Default.args,
  message: {
    ...Default.args.message,
    attachment: {
      name: "document.pdf",
      file: "https://picsum.photos/640/360",
    },
  },
};

export const WithImage = Template.bind({});
WithImage.args = {
  ...Default.args,
  message: {
    ...Default.args.message,
    attachment: {
      name: "image.jpg",
      file: "https://picsum.photos/640/360",
    },
  },
};
