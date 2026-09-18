import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

class EmailService:
    """
    SMTP Email Service for sending marketing communications via Mailpit.
    Only internal Gateway code calls this with resolved real email.
    """

    def send_campaign_email(
        self,
        real_email: str,
        campaign_id: str,
        template_id: str,
        protected_recipient: str
    ) -> bool:
        """
        Deliver campaign email via local SMTP (Mailpit).
        Returns True on success, raises Exception on failure.
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"FLYYY.AI Campaign: {campaign_id} [{template_id}]"
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = real_email

        body_text = f"""
Hello,

This message was dispatched through the FLYYY.AI Privacy-Preserving Customer Data Platform.
- Campaign ID: {campaign_id}
- Template: {template_id}
- Recipient Token: {protected_recipient}

All downstream systems executed this workflow using exclusively the protected identifier.
"""
        msg.attach(MIMEText(body_text, "plain"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as server:
                server.sendmail(settings.SMTP_FROM_EMAIL, [real_email], msg.as_string())
            return True
        except Exception as e:
            # Re-raise without exposing real_email in error trace
            raise RuntimeError(f"SMTP delivery failed to deliver campaign {campaign_id}: {str(e)}")


email_service = EmailService()
