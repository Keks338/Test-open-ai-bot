# # Создание потока
# from openai import OpenAI
# client = OpenAI()
#
# empty_thread = client.beta.threads.create()
# print(empty_thread)

# # Получение данных о потоке
# from openai import OpenAI
# client = OpenAI()
#
# my_thread = client.beta.threads.retrieve("thread_JfZdyGjNq8jiGjvrjkU99rzU")
# print(my_thread)


# # Изменение потока
# from openai import OpenAI
# client = OpenAI()
#
# my_updated_thread = client.beta.threads.update(
#   "thread_abc123",
#   metadata={
#     "modified": "true",
#     "user": "abc123"
#   }
# )
# print(my_updated_thread)


# # Удаление потока
# from openai import OpenAI
# client = OpenAI()
#
# response = client.beta.threads.delete("thread_Wu0xrXkLeGbMwCWuG3lHfD8R")
# print(response)
#
#
# thread_messages = client.beta.threads.messages.list("thread_Wu0xrXkLeGbMwCWuG3lHfD8R")
# print(thread_messages)
# # Итерируем по объекту `SyncCursorPage`
# for message in thread_messages:
#     print(message)
#     # Проверяем, что это сообщение от ассистента
#     if message.role == 'assistant':
#         # Проверяем, есть ли элементы в `content` и правильная ли структура
#         if message.content and len(message.content) > 0:
#             # Проверяем, что это текстовое сообщение и у него есть поле `text`
#             if message.content[0].type == "text" and "text" in message.content[0]:
#                 assistant_message = message.content[0].text.value
#                 print(f"Assistant: {assistant_message}")
#                 break
#         else:
#             print("Message content is empty or has an unexpected structure.")


