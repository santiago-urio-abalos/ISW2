from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from . import models
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
<<<<<<< HEAD
<<<<<<< HEAD
from reviews.models import Review  # Importamos los reviews
=======
>>>>>>> e87636e7 (Fix: Agregar annotate review_count y avg_rating para mostrar y ordenar por popularidad)
from django.views.generic import DetailView
from .models import Destination, Cruise, Purchase
from reviews.models import Review
from reviews.forms import ReviewForm
<<<<<<< HEAD
from .models import Destination
from relecloud.models import Cruise
from reviews.forms import ReviewForm  # si tienes un formulario
=======
from django.db.models import Count, Avg
>>>>>>> efece17a (PBI 1: Implementar cálculo de popularidad de destinos basado en reviews)
=======
from django.db.models import Count, Avg
from django.contrib.auth.decorators import login_required
>>>>>>> e87636e7 (Fix: Agregar annotate review_count y avg_rating para mostrar y ordenar por popularidad)


# Vistas básicas
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    # Calcular popularidad basada en número de reviews y rating promedio
    all_destinations = models.Destination.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count', '-avg_rating')
    
    return render(request, 'destinations.html', {'destinations': all_destinations})



# Detalle de un destino
class DestinationDetailView(DetailView):
    model = Destination
    template_name = 'destination_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        destination = self.object
        user = self.request.user

        # Todas las reviews de este destino
        reviews = Review.objects.filter(destination=destination)
        context['reviews'] = reviews
        context['average_rating'] = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # Comprobamos si el usuario ha comprado el destino
        purchased = False
        if user.is_authenticated:
            purchased = Purchase.objects.filter(user=user, destination=destination).exists()
        context['purchased'] = purchased

        return context


# Detalle de un crucero
class CruiseDetailView(DetailView):
    model = Cruise
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'



from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Reviews del destino al que pertenece este cruise
        # En CruiseDetailView
        reviews = Review.objects.filter(destination__in=self.object.destinations.all())
        context['reviews'] = reviews
        context['average_rating'] = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        return context


# Formulario de información
class InfoRequestCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'info_request_create.html'
    model = models.InfoRequest
    fields = ['name', 'email', 'cruise', 'notes']
    success_url = reverse_lazy('index')
    success_message = 'Thank you, %(name)s! We will email you when we have more information about %(cruise)s!'

<<<<<<< HEAD
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

=======
>>>>>>> 966ef054 (Cambios)
# CRUD de destinos
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


@login_required
def add_review(request, destination_id):
    destination = get_object_or_404(Destination, pk=destination_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.destination = destination
            review.save()
            return redirect('destination_detail', pk=destination.id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {'form': form, 'destination': destination})



@login_required
def buy_destination(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    user = request.user

    # Evitar compras duplicadas
    if not Purchase.objects.filter(user=user, destination=destination).exists():
        Purchase.objects.create(user=user, destination=destination)

    return redirect('destination_detail', pk=destination.id)

