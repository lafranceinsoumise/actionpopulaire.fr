from django.views.generic import TemplateView


class SuccessMessageView(TemplateView):
    template_name = 'front/success.html'
    title = None
    message = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.title
        context['message'] = self.message

        return context
