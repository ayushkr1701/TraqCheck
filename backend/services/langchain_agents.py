from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import Config
import json
import re

llm = AzureChatOpenAI(
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    api_key=Config.AZURE_OPENAI_API_KEY,
    api_version=Config.AZURE_OPENAI_API_VERSION,
    deployment_name=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
    temperature=0.3
)


class ResumeCheckerAgent:
    """
    Agent specialized in analyzing and extracting information from resumes
    """

    def __init__(self):
        self.llm = llm

    def extract_information(self, resume_text: str) -> dict:
        """
        Extracts structured information from resume text with confidence scores
        """
        prompt = ChatPromptTemplate.from_template(
            """You are an expert HR assistant specialized in resume analysis and information extraction.

Analyze the resume below and extract key information. Return ONLY a valid JSON object in this exact format:

{{
  "full_name": {{"value": "John Doe", "confidence": 0.95}},
  "email": {{"value": "john@example.com", "confidence": 0.99}},
  "phone": {{"value": "+91-9876543210", "confidence": 0.95}},
  "current_company": {{"value": "Tech Corp", "confidence": 0.92}},
  "designation": {{"value": "Senior Software Engineer", "confidence": 0.90}},
  "skills": {{"value": ["Python", "React", "AWS"], "confidence": 0.88}},
  "years_of_experience": 5,
  "education": "B.Tech Computer Science"
}}

Rules:
- Use null for any field not found
- Confidence scores should be between 0 and 1
- Skills should be an array of strings
- Years of experience should be a number
- Return ONLY the JSON, no other text

Resume Text:
{resume_text}"""
        )

        chain = prompt | self.llm

        response = chain.invoke({"resume_text": resume_text})

        try:
            content = response.content.strip()

            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()

            parsed_output = json.loads(content)

            return {
                "full_name": parsed_output.get("full_name", {"value": None, "confidence": 0}),
                "email": parsed_output.get("email", {"value": None, "confidence": 0}),
                "phone": parsed_output.get("phone", {"value": None, "confidence": 0}),
                "current_company": parsed_output.get("current_company", {"value": None, "confidence": 0}),
                "designation": parsed_output.get("designation", {"value": None, "confidence": 0}),
                "skills": parsed_output.get("skills", {"value": [], "confidence": 0}),
                "years_of_experience": parsed_output.get("years_of_experience"),
                "education": parsed_output.get("education")
            }
        except Exception as e:
            print(f"Parsing error: {str(e)}")
            print(f"Raw response: {response.content}")
            raise


class EmailWriterAgent:
    """
    Agent specialized in writing professional, personalized emails
    """

    def __init__(self):
        self.llm = llm

    def generate_document_request_email(self, candidate_info: dict) -> str:
        """
        Generates a personalized, professional email requesting identity documents
        """
        prompt = ChatPromptTemplate.from_template(
            """You are a professional HR communication specialist.

Your task is to write a polite, professional email requesting identity documents from a candidate.

Candidate Information:
- Name: {name}
- Email: {email}
- Phone: {phone}
- Company: {company}
- Designation: {designation}

Requirements:
1. Start with a professional subject line
2. Address the candidate by name
3. Mention that for further processing we need some documents
4. Clearly state that you need PAN Card and Aadhaar Card
5. Explain that these are required for verification purposes
6. Provide clear instructions on how to submit (via email or upload portal)
7. Maintain a warm, friendly yet professional tone
8. Keep it concise (3-4 paragraphs)
9. Include a professional closing with HR, TraqCheck

Format:
Subject: [Write a clear subject line]

[Email body]

Write the complete email now:"""
        )

        chain = prompt | self.llm

        response = chain.invoke({
            "name": candidate_info.get('full_name', 'Candidate'),
            "email": candidate_info.get('email', ''),
            "phone": candidate_info.get('phone', ''),
            "company": candidate_info.get('current_company', 'our organization'),
            "designation": candidate_info.get('designation', 'the position')
        })

        return response.content.strip()


class RequestSenderAgent:
    """
    Agent responsible for preparing and logging document requests
    """

    def __init__(self):
        self.llm = llm

    def prepare_request(self, candidate_info: dict, email_content: str) -> dict:
        """
        Prepares the document request with metadata and logging information
        """
        prompt = ChatPromptTemplate.from_template(
            """You are validating and preparing a document request.

Candidate Information:
- Name: {name}
- Email: {email}
- Phone: {phone}

Email Content:
{email_content}

Your task:
1. Verify the email is professional and appropriate
2. Confirm it includes clear instructions
3. Check if required documents (PAN, Aadhaar) are mentioned
4. Return a JSON object with: {{
    "is_valid": true/false,
    "request_type": "email" or "sms",
    "priority": "high", "medium", or "low",
    "summary": "One-line summary of the request"
}}"""
        )

        chain = prompt | self.llm

        response = chain.invoke({
            "name": candidate_info.get('full_name', 'Candidate'),
            "email": candidate_info.get('email', ''),
            "phone": candidate_info.get('phone', ''),
            "email_content": email_content
        })

        try:
            validation = json.loads(response.content)

            return {
                "candidate_email": candidate_info.get('email'),
                "candidate_phone": candidate_info.get('phone'),
                "message": email_content,
                "request_type": validation.get("request_type", "email"),
                "priority": validation.get("priority", "medium"),
                "summary": validation.get("summary", "Document request"),
                "is_valid": validation.get("is_valid", True)
            }
        except:
            return {
                "candidate_email": candidate_info.get('email'),
                "candidate_phone": candidate_info.get('phone'),
                "message": email_content,
                "request_type": "email",
                "priority": "medium",
                "summary": "Document request for identity verification",
                "is_valid": True
            }


class AgentOrchestrator:
    """
    Orchestrates multiple agents to work together in sequence
    """

    def __init__(self):
        self.resume_checker = ResumeCheckerAgent()
        self.email_writer = EmailWriterAgent()
        self.request_sender = RequestSenderAgent()

    def process_resume_and_request_documents(self, resume_text: str) -> dict:
        """
        Complete workflow: Extract info → Generate email → Prepare request
        """
        print("[ORCHESTRATOR] Step 1: Analyzing resume with ResumeCheckerAgent...")
        extracted_info = self.resume_checker.extract_information(resume_text)

        print("[ORCHESTRATOR] Step 2: Generating email with EmailWriterAgent...")
        candidate_info = {
            'full_name': extracted_info.get('full_name', {}).get('value'),
            'email': extracted_info.get('email', {}).get('value'),
            'phone': extracted_info.get('phone', {}).get('value'),
            'current_company': extracted_info.get('current_company', {}).get('value'),
            'designation': extracted_info.get('designation', {}).get('value')
        }
        email_content = self.email_writer.generate_document_request_email(candidate_info)

        print("[ORCHESTRATOR] Step 3: Preparing request with RequestSenderAgent...")
        request_data = self.request_sender.prepare_request(candidate_info, email_content)

        print("[ORCHESTRATOR] Workflow completed successfully!")

        return {
            "extracted_data": extracted_info,
            "request_message": email_content,
            "request_metadata": request_data
        }
