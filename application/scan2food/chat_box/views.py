# UNCOMENT THE CACHE IN get_chat_user FUNCTION


from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from .whatsapp_msg_utils import *
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse


# Create your views here.

@csrf_exempt
def webhook(request):
    if request.method == "GET":
        if request.GET.get("hub.verify_token") == VERIFY_TOKEN:
            return HttpResponse(request.GET.get("hub.challenge"))
        return HttpResponse("Verification token mismatch", 403)

    if request.method == "POST":
        
        data = json.loads(request.body)

        handle_incoming_message(data)
        return HttpResponse("Received", 200)



def get_chat_users(request):

    current_time = localtime(timezone.now())

    # Define yesterday 6:00 AM
    # yesterday_6am = (current_time - timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
    
    # GET THE PREVIOUS 24 HOUR TIME
    last_20_hours = current_time - timedelta(hours=20)

    # Define tomorrow 6:00 AM
    tomorrow_6am = (current_time + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)

    chat_users = ChatUser.objects.filter(
        last_msg_tym__gte=last_20_hours,
        last_msg_tym__lt=tomorrow_6am
    )

    chat_users = chat_users.filter(
        continue_chat=True
    )

    return_data = {}

    for user in chat_users:
        localized_time = localtime(user.last_msg_tym)
        theatre_data = user.last_theatre()
        user_data = {
            'pk': user.pk,
            'phone_number': user.phone_number,
            'msg_time': localized_time.strftime("%d-%b-%Y %I:%M %p"),
            'reply_required': user.reply_required,
            'continue_chat': user.continue_chat,
            'user_messages': [],
            'theatre_id': theatre_data['theatre_id'],
            'theatre_name': theatre_data['theatre_name'],
            'seat_id': theatre_data['seat_id'],
            'seat_name': theatre_data['seat_name'],
            'hall_name': theatre_data['hall_name'],
        }
        return_data[f"phone-{user.phone_number}"] = user_data

    return JsonResponse(return_data, safe=False)


@login_required
def send_whatsapp_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        phone_number = data['phone_number']

        context = data['message']

        reply_to_user(phone_number, context, True)
        
        save_message(phone_number=phone_number, context=context, msg_type='OUTGOING', notify=True, user_id=request.user.id)


        return JsonResponse({'status': 'done'})
    else:
        return JsonResponse({'status': 'method not allowed.'})
    

@login_required
def get_chats_from_order_id(request, pk):
    message = Message.objects.filter(order=pk).first()
    if not message:
        return StreamingHttpResponse(status=404)

    chat_user = message.chat_user

    def message_stream():
        yield f"data: {json.dumps({"phone_number": chat_user.phone_number, 'user_id': chat_user.pk})} \n\n"
        all_messages = chat_user.message_set.all()
        all_messages = all_messages.filter(pk__gte=message.pk).all()
        for msg in all_messages.iterator(chunk_size=100):
            data = msg.json_data()
            yield f"data: {json.dumps(data)}\n\n"

    return StreamingHttpResponse(
        message_stream(),
        content_type='text/event-stream'
    )













































# DELETE IT
def get_user_messages(request):
    phone_number = request.GET.get('phone_number')
    chat_user = ChatUser.objects.filter(
        phone_number=phone_number
    ).first()

    all_messages = chat_user.message_set.order_by("-time_stamp")[:10]
    
    return_data = []
    for message in all_messages:
        append_data = message.json_data()
        return_data.append(append_data)
    
    return JsonResponse(return_data, safe=False)

        
    
    

























# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
#                       HAVE TO DELETE THESE VIEWS   
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////

@login_required
def index(request):
    return render(request, 'chat-box/index.html')

