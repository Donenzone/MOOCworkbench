from django.shortcuts import render
from .models import Package, PackageVersion
from django.views.generic.list import ListView
from django.views.generic import CreateView, DetailView

class PackageListView(ListView):
    model = Package

class PackageCreateView(CreateView):
    model = Package
    fields = ('__all__')

class PackageDetailView(DetailView):
    model = Package

class PackageVersionCreateView(CreateView):
    model = PackageVersion
    fields = ('__all__')
