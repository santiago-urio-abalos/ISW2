from django.shortcuts import render
from django.urls import reverse_lazy
from . import models
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from reviews.models import Review  # Importamos los reviews
from django.views.generic import DetailView
from .models import Destination, Cruise, Purchase
from reviews.models import Review
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from reviews.forms import ReviewForm
from .models import Destination
from relecloud.models import Cruise
from reviews.forms import ReviewForm  # si tienes un formulario


# Vistas básicas
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def destinations(request):
    all_destinations = models.Destination.objects.all()
    return render(request, 'destinations.html', { 'destinations': all_destinations})



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

