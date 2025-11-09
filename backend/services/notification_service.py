class NotificationService:

    @staticmethod
    def send_email(to_email, subject, body):
        """
        Send email notification to candidate
        Future implementation: Integrate with SendGrid, AWS SES, or SMTP
        """
        print(f"[EMAIL NOTIFICATION]")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body[:100]}...")
        print("-" * 50)

        return {
            'sent': True,
            'method': 'email',
            'recipient': to_email,
            'status': 'simulated'
        }

    @staticmethod
    def send_sms(to_phone, message):
        """
        Send SMS notification to candidate
        Future implementation: Integrate with Twilio, AWS SNS
        """
        print(f"[SMS NOTIFICATION]")
        print(f"To: {to_phone}")
        print(f"Message: {message[:100]}...")
        print("-" * 50)

        return {
            'sent': True,
            'method': 'sms',
            'recipient': to_phone,
            'status': 'simulated'
        }

    @staticmethod
    def send_document_request(candidate_email, candidate_phone, message):
        """
        Send document request via email and/or SMS
        """
        results = []

        if candidate_email:
            email_result = NotificationService.send_email(
                to_email=candidate_email,
                subject="Document Submission Required",
                body=message
            )
            results.append(email_result)

        if candidate_phone:
            sms_message = f"Document required. Please check your email for details."
            sms_result = NotificationService.send_sms(
                to_phone=candidate_phone,
                message=sms_message
            )
            results.append(sms_result)

        return results
