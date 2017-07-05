from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy

class SuccessMessageView(TemplateView):
    template_name = 'front/success.html'
    title = None
    message = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.title
        context['message'] = self.message

        return context


class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url=reverse_lazy('oauth_redirect_view')), )
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
