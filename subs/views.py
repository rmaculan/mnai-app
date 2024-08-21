from django.shortcuts import render, redirect

# Create your stripe subsrintion views here.
def subscribe(request):
    return render(request, 'subs/subscribe.html')
