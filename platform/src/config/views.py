
from django.shortcuts import render

def staticbundle(request):
  return render(request, '../frontend/src/build/index.html')