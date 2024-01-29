from django.http import JsonResponse
from datetime import datetime

def showtime(request):
    time= datetime.now()
    return JsonResponse({"time":time})


