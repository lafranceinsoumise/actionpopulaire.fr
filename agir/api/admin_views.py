from django.http.response import HttpResponse


def page_not_found_view(request, exception):
    response = HttpResponse(
        "<!DOCTYPE html><html><body><h1>Page non trouvée</h1></body></html>"
    )
    response.status_code = 404
    return response
