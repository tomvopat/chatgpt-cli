import openai
import readline
from decouple import config

openai.api_key = config("OPENAI_KEY")
model = 'gpt-3.5-turbo'
log_file_name = 'chatgpt.log'

def logging(messages, filename):
    log_file = open(log_file_name, "a")
    log_file.write(str(messages))
    log_file.close()

def ask_chatgpt(messages):
    answer = openai.ChatCompletion.create(model=model, messages=messages)
    messages.append(answer.choices[0].message.to_dict())
    return messages

messages = []
total_tokens = 0

print(
'''Welcome to ChatGPT!
\t- type 'clear' to remove context
\t- type 'exit' to exit''')

while(True):
    if(not len(messages)):
        user_input = input("(new)> ")
    else:
        user_input = input("(follow: {})> ".format(total_tokens))

    user_input_trim = user_input.lower().strip()
    if(user_input_trim == 'clear'):
        messages = []
        print("--- new context ---")
        continue
    elif(user_input_trim == ''):
        print("empty prompt...")
        continue
    elif(user_input_trim == 'exit'):
        print("Bye!")
        break

    messages.append({'role': 'user', 'content': user_input})
    answer = openai.ChatCompletion.create(model=model, messages=messages)
    total_tokens = answer.usage.total_tokens
    messages.append(answer.choices[0].message.to_dict())

    print(messages[-1]['content'])
    logging(messages, log_file_name)
