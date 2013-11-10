from django.shortcuts import render

def good(request):
    return render(request, "good.html", {})

def bad(request):
    return render(request, "bad.html", {})
