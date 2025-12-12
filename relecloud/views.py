from django.shortcuts import render, HttpResponse
from django.urls import reverse_lazy
from . import models
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Avg

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    # Calcular popularidad basada en número de reviews y rating promedio
    all_destinations = models.Destination.objects.annotate(
        review_count=Count('destination_reviews'),
        avg_rating=Avg('destination_reviews__rating')
    ).order_by('-review_count', '-avg_rating')
    
    return render(request, 'destinations.html', {'destinations': all_destinations})

class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'

class CruiseDetailView(generic.DetailView):
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'



from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages

class InfoRequestCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'info_request_create.html'
    model = models.InfoRequest
    fields = ['name', 'email', 'cruise', 'notes']
    success_url = reverse_lazy('index')
    success_message = 'Thank you, %(name)s! We will email you when we have more information about %(cruise)s!'

    def form_valid(self, form):
        info = form.instance
        # Evitar duplicados: mismo email y crucero
        if models.InfoRequest.objects.filter(email=info.email, cruise=info.cruise).exists():
            messages.warning(self.request, "Ya has enviado una solicitud para este crucero. Espera nuestra respuesta antes de enviar otra.")
            return super().form_invalid(form)

        response = super().form_valid(form)
        subject = f"Nueva solicitud de información para {info.cruise}"
        message = (
            f"Se ha recibido una nueva solicitud de información.\n\n"
            f"Nombre: {info.name}\n"
            f"Email: {info.email}\n"
            f"Crucero: {info.cruise}\n"
            f"Notas: {info.notes}\n"
            f"Fecha: {info.created_at}"
        )
        recipient = ["miguigomez11@gmail.com"]  # Cambia esto por el email real de destino
        try:
            send_mail(
                subject,
                message,
                None,  # Usa el DEFAULT_FROM_EMAIL de settings.py
                recipient,
                fail_silently=False,
            )
            messages.success(self.request, "¡Solicitud enviada correctamente! Pronto recibirás información por email.")
        except BadHeaderError:
            messages.error(self.request, "Error: Cabecera de email inválida.")
        except Exception as e:
            messages.error(self.request, f"Error al enviar el email: {str(e)}")
        return response

class DestinationCreateView(generic.CreateView):
    template_name = 'destination_form.html'
    model = models.Destination
    fields = ['name', 'description']

class DestinationUpdateView(generic.UpdateView):
    template_name = 'destination_form.html'
    model = models.Destination
    fields = ['name', 'description']

class DestinationDeleteView(generic.DeleteView):
    template_name = 'destination_confirm_delete.html'
    model = models.Destination
    success_url = reverse_lazy('destinations')
    
