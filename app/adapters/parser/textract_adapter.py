import os
from dotenv import load_dotenv, find_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.documentintelligence.models import AnalyzedDocument

_ = load_dotenv(find_dotenv())

endpoint = os.environ['endpoint']
key = os.environ['key']

def analyze_invoice(file_path):
    client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
    with open(file_path, 'rb') as f: 
        poller = client.begin_analyze_document("prebuilt-invoice", body = f)
    return poller.result() 



