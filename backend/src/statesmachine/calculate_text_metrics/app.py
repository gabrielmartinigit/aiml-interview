# General
import os
import json
import boto3
from typing import Dict

# LLM
from langchain.llms.sagemaker_endpoint import (
    LLMContentHandler,
    SagemakerEndpoint,
)
from langchain import PromptTemplate, LLMChain

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3")

weasel_words = [
    "ai",
    "todo",
    "sobre",
    "todos",
    "quase",
    "sempre",
    "ao redor",
    "acreditar",
    "melhor",
    "maior",
    "pode",
    "consideravelmente",
    "poderia",
    "direcional",
    "permite",
    "mais rápido",
    "pouco",
    "frequente",
    "frequentemente",
    "geralmente",
    "maior",
    "mais alto",
    "esperança",
    "apenas",
    "muito",
    "mais baixo",
    "muitos",
    "material",
    "pode",
    "talvez",
    "poderia",
    "mais",
    "mais",
    "quase",
    "não-trivial",
    "frequentemente",
    "parceiros",
    "planejamento",
    "possivelmente",
    "provavelmente",
    "parece",
    "deveria",
    "significativo",
    "significativamente",
    "mais lento",
    "menor",
    "alguns",
    "em breve",
    "suporta",
    "pensar",
    "tentar",
    "geralmente",
    "pior",
    "seria",
    "fácil",
    "difícil",
    "drástico",
    "visar",
    "não-trivial",
    "não-trivial",
    "esmagador",
    "desproporcionalmente",
]

specific_words = [
    "raiva",
    "irritado",
    "ansioso",
    "certo",
    "preocupação",
    "preocupado",
    "confiança",
    "confiante",
    "deprimido",
    "desespero",
    "angústia",
    "angustiado",
    "dúvida",
    "temor",
    "elevado",
    "elevação",
    "animado",
    "empolgação",
    "medo",
    "sentiu",
    "frustrado",
    "frustração",
    "contente",
    "feliz",
    "esperança",
    "esperou",
    "alegria",
    "diversão",
    "nervoso",
    "pânico",
    "satisfeito",
    "aliviado",
    "alívio",
    "satisfeito",
    "assustado",
    "choque",
    "tristeza",
    "certo",
    "incerto",
    "chateado",
    "preocupação",
    "preocupado",
    "desejado",
    "mestre",
    "escravo",
    "mestre-escravo",
    "lista negra",
    "lista negra",
    "lista branca",
    "lista branca",
    "dias sombrios",
    "dias claros",
    "colocado na lista branca",
    "colocado na lista negra",
    "colocar na lista branca",
    "colocar na lista negra",
    "removerlista branca",
    "lista branca",
]

filler_words = [
    "novamente",
    "já",
    "de qualquer forma",
    "apareceu",
    "de volta",
    "ser capaz de",
    "começou",
    "acreditado",
    "considerado",
    "decidido",
    "devido ao fato de",
    "com a finalidade de",
    "com as finalidades de",
    "ouviu",
    "ideia",
    "para",
    "apenas",
    "sabia",
    "gostava",
    "faltava a habilidade de",
    "olhou",
    "notou",
    "apenas",
    "próprio",
    "fez parceria com",
    "fazendo parceria com",
    "ao invés",
    "real",
    "reconhecido",
    "percebeu",
    "viu",
    "parecia",
    "cheirou",
    "começou",
    "ainda",
    "suposto",
    "coisa",
    "pensou",
    "tocou",
    "entendeu",
    "até que",
    "observou",
    "com exceção de",
    "com possível exceção de",
    "imaginado",
]

metrics = {
    "wpm": 0,
    "fillers": [""],
    "weasel": [""],
    "specific_words": [""],
    "transcription": "",
    "feedback": "",
}


def calculate_wpm(text):
    return 0


def calculate_match_words(text):
    match_words_weasel = []
    match_words_specific = []
    match_words_filler = []
    compare = [weasel_words, specific_words, filler_words]

    for i, compare_words in enumerate(compare):
        for word in compare_words:
            if word in text:
                if i == 0:
                    match_words_weasel.append(word)
                elif i == 1:
                    match_words_specific.append(word)
                else:
                    match_words_filler.append(word)

    return match_words_weasel, match_words_specific, match_words_filler


class LLMHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        input_str = json.dumps(
            {
                "inputs": [
                    [
                        {
                            "role": "system",
                            "content": "Você é um mentor, ajude o mentorado.",
                        },
                        {"role": "user", "content": prompt},
                    ]
                ],
                "parameters": {**model_kwargs},
            }
        )
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generation"]["content"]


def generate_feedback(text):
    prompt_template = "De um feedback em português para a apresentação do mentorado destacando os pontos de melhoria. A apresentação do cadidato é a seguinte '{text}'"

    sm_llm = SagemakerEndpoint(
        endpoint_name="jumpstart-dft-meta-textgeneration-llama-2-70b-f",
        region_name="us-east-1",
        model_kwargs={
            "max_new_tokens": 2048,
            "top_p": 0.1,
            "temperature": 0.7,
        },
        content_handler=LLMHandler(),
        endpoint_kwargs={"CustomAttributes": "accept_eula=true"},
    )

    llm_chain = LLMChain(
        llm=sm_llm, prompt=PromptTemplate.from_template(prompt_template)
    )

    response = llm_chain(text)

    return response["text"]


def evaluate():
    return "test"


def lambda_handler(event, context):
    transcription_file = event["TranscriptionJob"]["Transcript"][
        "TranscriptFileUri"
    ]

    key = os.path.splitext(os.path.basename(transcription_file))
    s3.download_file(
        BUCKET, "transcription/" + key[0] + key[1], "/tmp/transcription.json"
    )
    file = open("/tmp/transcription.json")

    data = json.load(file)
    text = data["results"]["transcripts"][0]["transcript"]
    metrics["wpm"] = calculate_wpm(text)
    (
        metrics["weasel"],
        metrics["specific_words"],
        metrics["fillers"],
    ) = calculate_match_words(text)
    metrics["transcription"] = text
    metrics["feedback"] = generate_feedback(text)

    avaliation = evaluate()

    return {
        "statusCode": 200,
        "body": {"metrics": str(metrics), "avaliation": avaliation},
    }
