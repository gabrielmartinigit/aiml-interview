# General
import re
import os
import json
import boto3

BUCKET = os.environ["BUCKET"]
s3 = boto3.client("s3")

LLM_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

metrics = {
    "transcription": "",
    "symptoms": "",
    "causes": "",
    "plan": "",
}

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
)


def bedrock_feedback(transcription):
    prompt_template = f"""Use a transcrição da consulta para auxiliar o médico.
    
    Aqui está a transcrição:
    <consulta>{transcription}</consulta>
    
    Aqui estão algumas regras importantes que você deve serguir para responder:
    - Identifique os sintomas e coloque sua resposta entre <sintomas></sintomas>
    - Análise a possíveis causas e coloque sua resposta entre <causas></causas>
    - Sugira possíveis exames relacionados aos sintomas e causas e coloque sua resposta entre <plano></plano>

    Pense sobre sua resposta antes de responder.
    """

    response = bedrock.invoke_model(
        modelId=LLM_MODEL_ID,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "system": "Você é um assistente médico muito experiente. Você é capaz de analisar a consulta médica de um paciente, entendendo os sintomas, possíveis causas e exames a serem feitos. Você auxilia o médico no entendimento do que pode estar acontencendo com o paciente.",
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt_template}],
                    }
                ],
                "temperature": 0.5,
            }
        ),
    )

    result = (
        json.loads(response.get("body").read())
        .get("content", [])[0]
        .get("text", "")
    )

    return result


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
    transcription = data["results"]["transcripts"][0]["transcript"]

    metrics["transcription"] = transcription
    assistant = bedrock_feedback(transcription).replace('"', "`")

    symptoms_pattern = re.compile(r"<sintomas>(.*?)<\/sintomas>", re.DOTALL)
    symptoms_match = symptoms_pattern.search(assistant)
    metrics["symptoms"] = symptoms_match.group(1).strip()

    causes_pattern = re.compile(r"<causas>(.*?)<\/causas>", re.DOTALL)
    causes_match = causes_pattern.search(assistant)
    metrics["causes"] = causes_match.group(1).strip()

    plan_pattern = re.compile(r"<plano>(.*?)<\/plano>", re.DOTALL)
    plan_match = plan_pattern.search(assistant)
    metrics["plan"] = plan_match.group(1).strip()

    return {
        "statusCode": 200,
        "body": {"metrics": str(metrics)},
    }
