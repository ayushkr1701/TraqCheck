from openai import AzureOpenAI
from config import Config

class AIAgent:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION
        )
        self.deployment_name = Config.AZURE_OPENAI_DEPLOYMENT_NAME

    def generate_document_request(self, candidate_data):
        name = candidate_data.get('full_name', 'Candidate')
        email = candidate_data.get('email', '')
        phone = candidate_data.get('phone', '')
        company = candidate_data.get('current_company', 'our organization')
        designation = candidate_data.get('designation', 'the position')

        system_prompt = """You are a professional HR assistant helping collect identity documents from candidates.
Generate a professional, friendly email requesting PAN and Aadhaar documents.

Requirements:
- Address the candidate by name
- Mention their applied position/company if available
- Clearly list required documents: PAN card and Aadhaar card
- Provide submission instructions
- Maintain professional yet warm tone
- Keep message concise (3-4 paragraphs)
- Include a subject line

Format:
Subject: [subject line]

[Email body]"""

        user_prompt = f"""Generate a document request email for:
Name: {name}
Email: {email}
Phone: {phone}
Company: {company}
Designation: {designation}"""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            message = response.choices[0].message.content.strip()
            return message

        except Exception as e:
            raise Exception(f"Failed to generate document request: {str(e)}")
