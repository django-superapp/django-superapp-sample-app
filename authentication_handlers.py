from datetime import timedelta
from typing import Optional

from allauth.socialaccount.providers.sms.models import SMSVerification
from django.conf import settings
from django.utils import timezone
from prelude_python_sdk import Prelude


class PreludeSMSVerificationHandler:
    CODE_EXPIRY_MINUTES = 10

    @classmethod
    def create_verification(cls, request, phone_number: str, code: Optional[str] = None) -> SMSVerification:
        """
        Create a new verification code for the given phone number.
        Returns the generated code.
        """

        prelude_client = Prelude(
            api_token=settings.PRELUDE_API_TOKEN,
        )

        # Delete any existing unverified codes for this number
        SMSVerification.objects.filter(
            phone_number=phone_number,
            verified=False
        ).delete()

        is_returning_user = SMSVerification.objects.filter(phone_number=phone_number, verified=True).exists()

        try:
            verification = prelude_client.verification.create(
                target={
                    "type": "phone_number",
                    "value": phone_number,
                },
                signals={
                    "ip": request.META.get('REMOTE_ADDR'),
                    "is_returning_user": is_returning_user or True,
                },
            )
        except Exception as e:
            raise Exception(e.body.get('message'))

        if verification.status == "blocked":
            raise Exception("Failed to send verification code", verification.message)

        code = verification.id

        # Create new verification record
        sms_verification = SMSVerification.objects.create(
            phone_number=phone_number,
            code=code,
            verified=False
        )
        return sms_verification


    @classmethod
    def verify_code(cls, request, verification_id: str, code: str) -> Optional[SMSVerification]:
        """
        Verify the code for the given verification_id.
        Returns True if verification successful, False otherwise.
        """
        # Calculate expiry cutoff time
        expiry_cutoff = timezone.now() - timedelta(minutes=cls.CODE_EXPIRY_MINUTES)

        prelude_client = Prelude(
            api_token=settings.PRELUDE_API_TOKEN,
        )

        try:
            verification = SMSVerification.objects.get(
                id=verification_id,
                verified=False,
                created_at__gt=expiry_cutoff
            )

            verification_check = prelude_client.verification.check(
                code=code,
                target={
                    "type": "phone_number",
                    "value": verification.phone_number.as_e164,
                },
            )

            # Mark as verified
            verification.verified = verification_check.status == "success"
            verification.save()

            if verification_check.status != "success":
                return None

            return verification

        except SMSVerification.DoesNotExist:
            return None

    @classmethod
    def cleanup_expired(cls):
        """
        Delete expired verification records.
        Can be run periodically via management command or celery task.
        """
        # expiry_cutoff = timezone.now() - timedelta(minutes=cls.CODE_EXPIRY_MINUTES)
        # SMSVerification.objects.filter(created_at__lt=expiry_cutoff).delete()
        pass
