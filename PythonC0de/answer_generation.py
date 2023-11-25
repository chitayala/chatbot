import json
import logging
import openai
import os
import requests
import nltk

from hashlib import blake2b
from queries import *

hash = blake2b(digest_size=20)

nltk.data.path.append("/tmp")
nltk.download("stopwords", download_dir="/tmp")

# logging module
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s: [ %(message)s ]', '%m/%d/%Y %I:%M:%S %p')
console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)
stop = nltk.corpus.stopwords.words('english')

# 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
# org-pHcRTKVAfUH75PtoHXmOLLwz
try:
    openai.organization = os.environ["openai_organization_id"]
    openai.api_key = os.environ["openai_access_key"]
    logger.info("OpenAi app authentication success")
except Exception as e:
    logger.info("OpenAi app authentication failed - {}".format(e))


def moderation(question):
    logger.info("Filtering content for question - {}".format(question))
    response = openai.Moderation.create(input=question)
    output = response["results"][0]
    logger.info(output)
    logger.info(output["flagged"])
    return output["flagged"]


def getBusinessWebsiteData(businessId, question):
    orginalQues = question
    try:
        logger.info("stopwords removing")
        question = " ".join([word for word in question.lower().split() if word not in stop])
        logger.info("Stopword removed ques: {}".format(question))
    except Exception as e:
        logger.info("Error while removing stopwords - {}".format(e))
        custom_message = 'Error while generating answer for custom question'
        logger.info(custom_message)
        question = orginalQues

    try:
        logger.info("Fetching related business website data from cloudsearch")
        content = []

        cloudSearchUrl = """
        %s/2013-01-01/search?q=%s&q.parser=simple&q.options={"defaultOperator":"or"}&return=_all_fields,_score&sort=_score+desc
        """
        cloudSearchApi = os.environ['cloudSearchUrl']
        logger.info(cloudSearchUrl)
        logger.info((cloudSearchApi, question, businessId))
        logger.info(cloudSearchUrl % (cloudSearchApi, question))

        response = requests.get(url=cloudSearchUrl % (cloudSearchApi, question)).json()
        logger.info("Cloud search Response - {}".format(response))

        for item in response['hits']['hit'][:10]:
            content.append(item['fields']['answer'])

        if content:
            content = list(set(content))
            content = ' '.join(map(str, content))
            logger.info("Website data Content fetched successfully - {}".format(content))
            return content
        else:
            logger.info("Website data content not available")
            return None

    except Exception as e:
        content = ""
        logger.info("Error while fetching business website data from cloud search - {}".format(e))
        return content


def generateAnswer(question, businessId, user):
    try:
        # Hashing username for openai api logs
        hash.update(user.encode())
        hashedUser = hash.hexdigest()
        logger.info("Hashing user name {} - {}".format(user, hashedUser))

        businessWebsiteData = getBusinessWebsiteData(businessId, question)

        if businessWebsiteData:
            keywords = ''
            prompt = promptWithoutKeywords
            prompt = prompt.format(businessWebsiteData=businessWebsiteData, question=question)
        else:
            keywords = ''
            prompt = NoContentPromptWithoutKeywords.format(question=question)

        logger.info(f"Prompt -\n {prompt}")
        isContentFlagged = moderation(question)

        if not isContentFlagged:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                user=hashedUser
            )
            logger.info(response)
            generatedAnswer = response["choices"][0]["text"]
            logger.info(generatedAnswer)

        else:
            logger.info("Content is not safe")
            generatedAnswer = ''
        return generatedAnswer
    except Exception as e:
        logger.info("Error in generate answer function - {}".format(e))
        return ''


def lambda_handler(event, context):
    logger.info("Lambda function triggered")
    logger.info(event)
    if event["requestContext"]['http']['method'] == "POST":
        logger.info("Post call triggered")
        try:
            try:
                logger.info("Data parsing started")
                data = json.loads(event['body'])
                businessId = data['businessId']
                question = data['question'].strip()
                logger.info("Data parsing completed")
            except Exception as e:
                logger.info("exception occured: {}".format(str(e)))
                return json.dumps({"status": 400, "error": "Invalid Payload"})

            if question and question != '':
                logger.info("Started generating answer")
                answer = generateAnswer(question, businessId, 'bank_chatbot')
                answer = answer.replace('\n', '').strip()
                logger.info(f"Answer - {answer}")
            else:
                return json.dumps({"status": 400, "message": "QUESTION_CANNOT_BE_EMPTY"})
            return json.dumps({"status": 200, "question": question, "answer": answer})

        except Exception as e:
            logger.info("Error while Post call - {}".format(e))
            return json.dumps({"status": 400, 'message': 'FAILURE'})

    else:
        logger.info("Else logic executed")
        return json.dumps({"status": 400, 'message': 'FAILURE'})
