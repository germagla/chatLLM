from django.http import HttpResponse
from django.shortcuts import render
import os
import openai
from dotenv import load_dotenv

# Create your views here.
load_dotenv()

openai.api_key = os.environ.get('OPENAI_API_KEY')
model = 'gpt-3.5-turbo'

prompt = ''
conversation = []


def index(request):
    global conversation
    conversation = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Who won the world series in 2020?'},
        {'role': 'assistant', 'content': 'The Los Angeles Dodgers won the World Series in 2020.'},
        # ... more messages ...
    ]

    return render(request, 'chatLLM/index.html', {'model': model})


def process_prompt(request):
    # global prompt

    prompt = request.POST.get('prompt')
    messages = request.POST.get('messages')

    conversation.append({'role': 'user', 'content': prompt})

    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation,
    )
    conversation.append(response.choices[0].message)
    for item in conversation:
        if item['role'] == 'assistant':
            item['role'] = f'{model}'

    return render(request, 'chatLLM/htmx/chat.html', {'messages': conversation[3:], 'model': model})

    # return HttpResponse(response.choices[0].message)
