# ChatGPT CLI

Command-line interface for the ChatGPT

## Installation

1. Create virtual environemnt and install requirements

    ```
    python3 -m venv venv
    pip3 install -r requirements.txt
    ```

2. Create file with OpenAI key

    ```
    OPENAI_KEY="<your openai key>"
    echo "OPENAI_KEY='${OPENAI_KEY}'" > .env
    ```

3. Active virtual enviroment and run the program

    ```
    source venv/bin/activate
    python3 chatgpt.py
    ```
