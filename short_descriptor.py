import ollama

def make_description(file_path):
    data = ""
    with open(file_path, 'r', encoding='utf-8') as file:
        data += file.read()

    response = ollama.chat(model='llama3.1', messages=[
        {
            "role": 'system',
            'content': 'Пиши краткое содержание текста'
        },
        {
            'role': 'user',
            'content': data
        }
    ])

    OllamaResponse=response['message']['content']
    return OllamaResponse
