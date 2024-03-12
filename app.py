import PyPDF2
from flask import Flask, render_template, request
import os
import openai

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt_text = "Eres un experto en analisis médicos, el texto anterior son los resultados de un examen médico, quiero que solo me expliques si hay algun valor fuera de lo común, debes saludarme antes de comenzar a explicarme mi resultado médico, y concluir tu respuesta diciendo que lo mejor es ir al médico para tener un reporte exacto pero esta es una aproximación"


@app.route('/')
def generate():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        pdf_text = extract_text_from_pdf(file)
        explanation = chat_development(pdf_text)
        return render_template('result.html', explanation=explanation)

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def chat_development(user_message):
    conversation = build_conversation(user_message)
    try:
        assistant_message = generate_assistant_message(conversation)
    except openai.error.RateLimitError as e:
        assistant_message = "Rate limit exceeded. Sleeping for a bit..."

    return assistant_message


def build_conversation(user_message):
    return [
        {"role": "system",
         "content": "Eres un experto en analisis médicos, el texto anterior son los resultados de un examen médico, quiero que solo me expliques si hay algun valor fuera de lo común, debes saludarme antes de comenzar a explicarme mi resultado médico, y concluir tu respuesta diciendo que lo mejor es ir al médico para tener un reporte exacto pero esta es una aproximación"},
        {"role": "user", "content": user_message}
    ]


def generate_assistant_message(conversation):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )
    return response['choices'][0]['message']['content']

if __name__ == '__main__':
    app.run(debug=True)
