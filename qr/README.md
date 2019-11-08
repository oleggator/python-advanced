# QR Code Generator Bot
Generates QR codes and sends them to VK user

## Usage
1. Get [VK token](https://vk.com/dev/bots_docs)
2. Set environment variables
    ```bash
    export TOKEN= # VK token
    export USER_ID= # receiver's user id
    ```
3. Create venv and install dependencies
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4. Start
    ```bash
    python main.py
    ```
