from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse, HttpResponse
import json
from lesson.settings import *
from django.views.decorators.csrf import csrf_exempt


def gettime(request):
    jsons = json.loads(request.body)
    action = jsons['action']

    today = datetime.now()
    data = [{'datetime':today}]
    resp = sendResponse(request, 200, data, action)
    return resp
# gettime

def dt_register(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    firstname = jsons['firstname']
    lastname = jsons['lastname']
    email = jsons['email']
    passw = jsons['passw']

    myCon = connectDB()
    cursor = myCon.cursor()
    
    query = F"""SELECT COUNT(*) AS usercount FROM t_user 
            WHERE email = '{email}' AND enabled = 1"""
    
    cursor.execute(query)
    columns = cursor.description
    respRow = [{columns[index][0]:column for index, 
        column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()

    if respRow[0]['usercount'] == 1:
        data = [{'email':email}]
        resp = sendResponse(request, 1000, data, action)
    else:
        token = generateStr(12)
        query = F"""INSERT INTO public.t_user(
	email, lastname, firstname, passw, regdate, enabled, token, tokendate)
	VALUES ('{email}', '{lastname}', '{firstname}', '{passw}'
    , NOW(), 0, '{token}', NOW() + interval \'1 day\');"""
        cursor1 = myCon.cursor()
        cursor1.execute(query)
        myCon.commit()
        cursor1.close()
        data = [{'email':email, 'firstname':firstname, 'lastname': lastname}]
        resp = sendResponse(request, 1001, data, action)
        

        sendMail(email, "Verify your email", F"""
                <html>
                <body>
                    <p>Ta amjilttai burtguulle. Doorh link deer darj burtgelee batalgaajuulna uu. Hervee ta manai sited burtguuleegui bol ene mailiig ustgana uu.</p>
                    <p> <a href="http://localhost:8001/check/?token={token}">Batalgaajuulalt</a> </p>
                </body>
                </html>
                """)

    return resp
# dt_register

def dt_login(request):
    jsons = json.loads(request.body)
    action = jsons['action']
    email = jsons['email']
    passw = jsons['passw']
    for item in jsons['prods']:
        item['prodname']


    myCon = connectDB()
    cursor = myCon.cursor()
    
    query = F"""SELECT COUNT(*) AS usercount FROM t_user 
            WHERE email = '{email}' AND enabled = 1 AND passw = '{passw}'"""
    
    cursor.execute(query)
    columns = cursor.description
    respRow = [{columns[index][0]:column for index, 
        column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()

    if respRow[0]['usercount'] == 1:
        myCon = connectDB()
        cursor1 = myCon.cursor()
        
        query = F"""SELECT email, firstname, lastname
                FROM t_user 
                WHERE email = '{email}' AND enabled = 1 AND passw = '{passw}'"""
        
        cursor1.execute(query)
        columns = cursor1.description
        respRow = [{columns[index][0]:column for index, 
            column in enumerate(value)} for value in cursor1.fetchall()]
        cursor1.close()
        
        email = respRow[0]['email']
        firstname = respRow[0]['firstname']
        lastname = respRow[0]['lastname']

        data = [{'email':email, 'firstname':firstname, 'lastname':lastname}]
        resp = sendResponse(request, 1002, data, action)
    else:
        data = [{'email':email}]
        resp = sendResponse(request, 1004, data, action)

    return resp
#dt_login

@csrf_exempt
def checkService(request):
    if request.method == "POST":
        try :
            jsons = json.loads(request.body)
        except json.JSONDecodeError:
            

            result = sendResponse(request, 3003, [], "no action")
            return JsonResponse(json.loads(result))
        action = jsons['action']

        if action == 'gettime':
            result = gettime(request)
            return JsonResponse(json.loads(result))
        elif action == 'register':
            result = dt_register(request)
            return JsonResponse(json.loads(result))
        elif action == 'login':
            result = dt_login(request)
            return JsonResponse(json.loads(result))
        else:
            result = sendResponse(request, 3001, [], action)
            return JsonResponse(json.loads(result))
    else:
        result = sendResponse(request, 3002, [], "no action")
        return JsonResponse(json.loads(result))
#checkService

@csrf_exempt
def checkToken(request):
    token = request.GET.get('token')
    myCon = connectDB()
    cursor = myCon.cursor()
    
    query = F"""SELECT COUNT(*) AS usertokencount, MIN(email) as email, MAX(firstname) as firstname, 
                    MIN(lastname) AS lastname 
            FROM t_user 
            WHERE token = '{token}' AND enabled = 0 AND NOW() <= tokendate """
    
    cursor.execute(query)
    columns = cursor.description
    respRow = [{columns[index][0]:column for index, 
        column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()

    if respRow[0]['usertokencount'] == 1:
        query = F"""UPDATE t_user SET enabled = 1 WHERE token = '{token}'"""
        cursor1 = myCon.cursor()
        cursor1.execute(query)
        myCon.commit()
        cursor1.close()

        tokenExpired = generateStr(30)
        email = respRow[0]['email']
        firstname = respRow[0]['firstname']
        lastname = respRow[0]['lastname']
        query = F"""UPDATE t_user SET token = '{tokenExpired}', tokendate = NOW() WHERE email = '{email}'"""
        cursor1 = myCon.cursor()
        cursor1.execute(query)
        myCon.commit()
        cursor1.close()
        
        data = [{'email':email, 'firstname':firstname, 'lastname':lastname}]
        resp = sendResponse(request, 1003, data, "verified")
        sendMail(email, "Tanii mail batalgaajlaa",  F"""
                <html>
                <body>
                    <p>Tanii mail batalgaajlaa. </p>
                </body>
                </html>
                """)
    else:
        
        data = []
        resp = sendResponse(request, 3004, data, "not verified")
    return JsonResponse(json.loads(resp))
#checkToken