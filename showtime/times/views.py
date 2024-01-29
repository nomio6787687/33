from django.http import JsonResponse
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def showtime(request):
    if request.method=="POST":
        data=json.loads(request.body)
        action=data.get("action")
        if action=="gettime":
            time= datetime.now()
            return JsonResponse({"time":time})
        else:
            return JsonResponse({"message":"invalid action"})
        