from django.contrib import auth
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from chatbot.services.rag import build_index, search, build_prompt
from django.contrib.auth.decorators import login_required


from openai import OpenAI
from .models import Chat
from django.conf import settings


openai_api_key =settings.SECRET_KEY 
client = OpenAI(api_key=openai_api_key)

def ask_openai_with_docs(message, user):
    
    history = get_conversation_history(user)
    context_chunks = search(message, INDEX, CHUNKS)
    context = "\n\n".join(context_chunks)

    prompt = build_prompt(context, message)

    messages = [
        {
            "role": "system",
            "content": (
                "És um assistente jurídico eleitoral. "
                "Usa APENAS o contexto legal fornecido e o histórico da conversa."
                "Mantém coerência com respostas anteriores. "
                "Se não existir base legal, diz claramente."
            )
        }
    ]
    
    messages.extend(history)

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=messages,
        temperature=0.2  
    )
    return response.choices[0].message.content.strip()


# Create your views here.
@login_required(login_url='login')
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)


    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai_with_docs(message, request.user)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now)
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1==password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
            return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Password don't match" 
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

def get_conversation_history(user, limit=6):
   
    chats = (
        Chat.objects
        .filter(user=user)
        .order_by('-created_at')[:limit]
    )

    chats = reversed(chats)  # manter ordem cronológica

    history = []
    for chat in chats:
        history.append({"role": "user", "content": chat.message})
        history.append({"role": "assistant", "content": chat.response})

    return history


INDEX, CHUNKS = build_index()
