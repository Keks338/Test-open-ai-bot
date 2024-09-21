from celery import shared_task
from .models import BotUser
import os
import dotenv
import openai

dotenv.load_dotenv()

@shared_task
def remove_thread(thread_id):
    client = openai.OpenAI()
    user_record = BotUser.objects.get(thread_id=thread_id)
    print(client.beta.threads.delete(thread_id))
    user_record.thread_id = ""
    user_record.save()

@shared_task
def update_asst_db():
    client = openai.OpenAI()
    assistant = client.beta.assistants.update(
        assistant_id=os.getenv('Assistant_id'),
        tool_resources={"file_search": {"vector_store_ids": [os.getenv('Vector_store_docx_id')]}},
    )
    print(assistant)

