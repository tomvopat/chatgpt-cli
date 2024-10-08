import argparse
import openai
import decouple
import tiktoken
#import colorama
#from colorama import Fore, Style

openai.api_key = decouple.config("OPENAI_KEY")
LOG_FILE_NAME = 'chatgpt.log'
AVAILABLE_MODELS = [
    'gpt-3.5-turbo',
    'gpt-4',
    'gpt-4-turbo',
    'gpt-4o',
]
DEFAULT_MODEL = 'gpt-4o'

def temperature_check(value):
    fvalue = float(value)
    if fvalue < 0 or fvalue > 2:
        raise argparse.ArgumentTypeError("Value can be from 0 to 2.")
    return fvalue


def logging(content, filename):
    log_file = open(filename, "a")
    log_file.write(str(content))
    log_file.close()


def print_help():
    help_message = '''Instructions:
    /help   print help
    /new    start new context
    /exit   exit the program
    /tokens count number of used tokens
    '''
    print(help_message)

def read_input(is_new):
    # the colors don't work properly - second line overwrites the first one
    #prompt = bcolors.OKBLUE + "(new)> " + bcolors.ENDC
    prompt = "(new)> "
    if not is_new:
        #prompt = bcolors.OKBLUE + "(follow)> " + bcolors.ENDC
        prompt = "(follow)> "

    try:
        user_input = input(prompt)
    except EOFError:
        print()
        return (1, "EOF")

    user_input_trim = user_input.lower().strip()
    if user_input_trim == '/exit':
        return (1, "exit")
    elif user_input_trim == '/new':
        return (2, "new")
    elif user_input_trim == '/help':
        print_help()
        return (3, "help")
    elif user_input_trim == '':
        return (4, "no_input")
    elif user_input_trim == '/tokens':
        return (5, "stats")
    elif user_input[0] == '/':
        return (6, "uknown_command")
    else:
        return (0, user_input)


def count_tokens(message, model):
    enc = tiktoken.encoding_for_model(model)
    encoded_message = enc.encode(message)
    return len(encoded_message)


parser = argparse.ArgumentParser(
    prog='ChatGPT CLI',
    description='Command-line interface for ChatGPT')
parser.add_argument(
    '--file',
    help="File with input")
parser.add_argument(
    '--model',
    choices = AVAILABLE_MODELS,
    default=DEFAULT_MODEL,
    help="Which ChatGPT model to use")
parser.add_argument(
    '--temperature',
    type=temperature_check,
    help='Temperature of the GPT model. Float from 0 to 2',
    default=0)
args = parser.parse_args()

print('Welcome to ChatGPT! Type "/help" for help.')

file_input = ""
messages = []

if args.file:
    with open(args.file, 'r', encoding='utf-8') as f:
        file_input = f.read()
if len(file_input):
    messages.append({'role': 'user', 'content': file_input})
    print("(new)> file input...")

while (True):
    empty_messages = (len(messages) == 0)
    if empty_messages or (messages[-1]['role'] != 'user'):
        (exit_code, exit_message) = read_input(empty_messages)
        if exit_code == 0:
            messages.append({'role': 'user', 'content': exit_message})
        elif exit_code == 1:
            break
        elif exit_code == 2:
            messages = []
            continue
        elif exit_code == 3:
            continue
        elif exit_code == 4:
            continue
        elif exit_code == 5:
            token_count = 0
            for m in messages:
                token_count += count_tokens(m['content'], args.model)
            print(f"\t{token_count} tokens")
            continue
        elif exit_code == 6:
            print(f"error: {exit_message}")
            continue
        else:
            print(f"error: {exit_message}")
            exit()

    try:
        full_content = ""
        answer = openai.ChatCompletion.create(
            model=args.model,
            temperature=args.temperature,
            messages=messages,
            stream=True)
        for chunk in answer:
            finish_reason = str(chunk.choices[0]["finish_reason"])
            if finish_reason == "stop":
                break
            elif finish_reason == "None":
                delta = chunk.choices[0].delta
                if delta != {}:
                    full_content = full_content + delta.content
                    print(delta.content, end="")
            else:
                print("bad finish_reason:")
                print(chunk)
                exit()
        messages.append({'role': 'assistant', 'content': full_content})
        print()
    except Exception as err:
        print(err)
        exit()

    logging(messages, LOG_FILE_NAME)

print("Bye!")
