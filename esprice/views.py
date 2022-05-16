from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def statistics(request):
    # Submit prediction and show all
    return render(request, "statistic.html")

def filter(request):
    # Submit prediction and show all
    return render(request, "filter.html")
