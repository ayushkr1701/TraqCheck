import os
import json
from openai import AzureOpenAI
from config import Config

class AIExtractor:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION
        )
        self.deployment_name = Config.AZURE_OPENAI_DEPLOYMENT_NAME

    def extract_candidate_info(self, resume_text):
        prompt = f"""Extract the following information from the resume text below and provide confidence scores (0-1) for each field:

- Full Name
- Email Address
- Phone Number
- Current Company (most recent employer)
- Current Designation (job title)
- Skills (as a list)
- Years of Experience (total)
- Education (highest degree)

Resume Text:
{resume_text}

Return ONLY a valid JSON object in this exact format:
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

Important: If a field is not found, set value to null and confidence to 0. Ensure valid JSON format."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from resumes. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )

            response_text = response.choices[0].message.content.strip()

            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            extracted_data = json.loads(response_text)

            return extracted_data

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"AI extraction failed: {str(e)}")

    def validate_and_normalize_data(self, extracted_data):
        normalized = {}

        for field in ['full_name', 'email', 'phone', 'current_company', 'designation', 'skills']:
            if field in extracted_data and isinstance(extracted_data[field], dict):
                normalized[field] = extracted_data[field]
            else:
                normalized[field] = {'value': None, 'confidence': 0.0}

        normalized['years_of_experience'] = extracted_data.get('years_of_experience', None)
        normalized['education'] = extracted_data.get('education', None)

        return normalized
