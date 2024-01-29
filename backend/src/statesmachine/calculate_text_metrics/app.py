# General
import re
import os
import json
import boto3

# LLM
from langchain.llms import Bedrock

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3")

LLM_MODEL_ID = "anthropic.claude-v2:1"

metrics = {
    "transcription": "",
    "feedback": "",
}

bedrock = boto3.client(
    "bedrock-runtime",
    endpoint_url="https://bedrock-runtime.us-east-1.amazonaws.com",
    region_name="us-east-1",
)

# Ask LLM
llm_mentor_response = Bedrock(
    model_id=LLM_MODEL_ID,
    model_kwargs={
        "max_tokens_to_sample": 8000,
        "temperature": 0.2,
        "top_p": 0.7,
    },
    client=bedrock,
)


def bedrock_feedback(perguntas, apresentacao):
    prompt_template_bedrock = f"""
    Human: Você é um professor. Avalie a simulação de entrevista do aluno e corrija as respostas das perguntas. A apresentação do cadidato é a seguinte:
    
    <perguntas>{perguntas}</perguntas>
    <apresentação>{apresentacao}</apresentação>
    
    A resposta deve seguir o seguinte formato:
    <avaliação>Avaliação geral e de boas práticas de apresentação</avaliação>
    <correção>Correção das respostas do aluno para as perguntas</correção>
    
    Assistant:
    """
    chain = llm_mentor_response(prompt_template_bedrock)
    return str(chain)


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
    apresentacao = data["results"]["transcripts"][0]["transcript"]
    perguntas = """"
    1- Cite um serviço de computação AWS;
    2- Como são cobrados os serviços AWS?;
    3- Onde posso armazenar aquivos em objeto na AWS?;
    """

    metrics["transcription"] = apresentacao
    feedback = bedrock_feedback(perguntas, apresentacao).replace('"', "`")
    
    avaliacao_pattern = re.compile(r'<avaliação>(.*?)<\/avaliação>', re.DOTALL)
    correcao_pattern = re.compile(r'<correção>(.*?)<\/correção>', re.DOTALL)
    avaliacao_match = avaliacao_pattern.search(feedback)
    correcao_match = correcao_pattern.search(feedback)
    metrics["avaliacao"] = avaliacao_match.group(1).strip()
    metrics["correcao"] = correcao_match.group(1).strip()

    return {
        "statusCode": 200,
        "body": {"metrics": str(metrics)},
    }
