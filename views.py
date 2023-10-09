from django.db.models.functions import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import os
import openai
from dotenv import load_dotenv
from .models import Conversation, Message

load_dotenv()

openai.api_key = os.environ.get('OPENAI_API_KEY')
models = ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4', 'gpt-4-32k']


def index(request):
    # Check if the user has a conversation cookie
    if 'conversation_id' in request.COOKIES:
        # If the user has a conversation cookie, get the conversation object
        conversation = Conversation.objects.get(id=request.COOKIES['conversation_id'])
        messages = conversation.message_set.all()
        # Create a list of messages
        message_list = []
        for message in messages:
            message_list.append({'role': message.role, 'content': message.text})

        return render(request, 'chatLLM/index.html', {'models': models, 'messages': message_list[3:]})
    else:
        # If the user does not have a conversation cookie, create a new conversation object
        conversation = Conversation.objects.create(date_started=datetime.datetime.today(), title='Main Conversation')

        conversation.save()

        # Initialize the conversation with a message from the system and an example message from the user
        Message.objects.create(text='You are a helpful assistant.', role='system', conversation=conversation)
        Message.objects.create(text='Who won the world series in 2020?', role='user', conversation=conversation)
        Message.objects.create(text='The Los Angeles Dodgers won the World Series in 2020.', role='assistant',
                               conversation=conversation)
        # Save the messages
        conversation.save()

        response = render(request, 'chatLLM/index.html', {'models': models})
        response.set_cookie('conversation_id', conversation.id)
        return response


def process_prompt(request):
    # Get the conversation object
    conversation = Conversation.objects.get(id=request.COOKIES['conversation_id'])

    # Get the prompt from the user
    prompt = request.POST.get('prompt')
    model = request.POST.get('selected_model')
    # Create a message object for the prompt
    Message.objects.create(text=prompt, role='user', conversation=conversation)

    # Get the messages from the conversation object
    messages = conversation.message_set.all()
    # Create a list of messages
    message_list = []
    for message in messages:
        message_list.append({'role': message.role, 'content': message.text})

    # Get the response from OpenAI
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=message_list,
        )
    except Exception as e:
        print(e)
        message_list.append({'role': 'assistant', 'content': 'Sorry, I am having trouble connecting to OpenAI.'})
        return render(request, 'chatLLM/htmx/chat.html', {'messages': message_list[3:], 'models': models})
    # Create a message object for the response
    Message.objects.create(text=response.choices[0].message.content, role='assistant', conversation=conversation)
    # Save the messages
    conversation.save()

    # Create a list of messages
    message_list.append({'role': 'assistant', 'content': response.choices[0].message.content})

    return render(request, 'chatLLM/htmx/chat.html', {'messages': message_list[3:], 'models': models})


def clear_conversation(request):
    # delete the conversation object, the cookie, and the messages, then redirect to the index
    conversation = Conversation.objects.get(id=request.COOKIES['conversation_id'])
    conversation.delete()
    response = HttpResponseRedirect(reverse('chat'))
    response.delete_cookie('conversation_id')
    return response
