from django.views.generic import TemplateView

class ReactAppView(TemplateView):
    template_name = "base.html"
    
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
