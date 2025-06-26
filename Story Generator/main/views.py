from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.csrf import csrf_exempt
from .models import ChatHistory
import json
from llama_cpp import Llama
from huggingface_hub import hf_hub_download

# Load the model once during server startup
model_path = hf_hub_download(
    repo_id="microsoft/Phi-3-mini-4k-instruct-gguf",
    filename="Phi-3-mini-4k-instruct-q4.gguf"
)

llm = Llama(
    model_path=model_path,
    n_gpu_layers=18,    # Safe for 4GB VRAM
    n_batch=256,        # Prevent OOM errors
    n_threads=10,       # Adjust based on your CPU cores
    n_ctx=2048,
    offload_kqv=True,    # Save VRAM
    verbose=False
)

# Function to generate a short story
def generate_story(keywords):
    prompt = f"""<|user|>
    Generate a story using: {keywords}.
    Rules:
    1. Make it realistic
    2. Make it interesting
    4. Must add the {keywords} in the story
    5. Must be less than 150 words

    <|assistant|>
    """
    response = llm.create_completion(
        prompt=prompt,
        max_tokens=200,
        temperature=0.6,
        top_p=0.9,
        repeat_penalty=1.1,
        seed=42
    )
    return response["choices"][0]["text"]

# Main view
def home(request):
    return render(request, "main/home.html")  # Render frontend

# API for chatbot response
@csrf_exempt  
def get_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        if user_message=="hi":
            return JsonResponse({"response": "Hello, Enter a keyword & genre to generate story!"})
        else:
            # Extract keywords from user input
            keywords = user_message.lower().split()  

            # Generate a story using the model
            # print(keywords[0],keywords[1])
            bot_reply = generate_story([keywords])
             # Save to database
            ChatHistory.objects.create(
                user=request.user if request.user.is_authenticated else None,
                user_message=user_message,
                bot_response=bot_reply
            )

            return JsonResponse({"response": bot_reply})

    return JsonResponse({"response": "Invalid request"}, status=400)# views.py
def get_chat_history(request):
    chats = ChatHistory.objects.all().order_by('-created_at')[:50]  # Get last 50 entries
    history = [{
        'user_message': chat.user_message,
        'bot_response': chat.bot_response,
        'timestamp': chat.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for chat in chats]
    return JsonResponse({'history': history})