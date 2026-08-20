from cryptography.hazmat.primitives import serialization
from django.core.management.base import BaseCommand
from py_vapid import Vapid, b64urlencode


class Command(BaseCommand):
    help = "Render 환경변수에 넣을 VAPID 공개키와 개인키를 생성합니다."

    def handle(self, *args, **options):
        vapid = Vapid()
        vapid.generate_keys()

        private_value = vapid.private_key.private_numbers().private_value
        private_key = b64urlencode(private_value.to_bytes(32, "big"))
        public_key = b64urlencode(
            vapid.public_key.public_bytes(
                serialization.Encoding.X962,
                serialization.PublicFormat.UncompressedPoint,
            )
        )

        self.stdout.write(f"WEBPUSH_VAPID_PUBLIC_KEY={public_key}")
        self.stdout.write(f"WEBPUSH_VAPID_PRIVATE_KEY={private_key}")
        self.stderr.write(
            self.style.WARNING(
                "개인키는 Render 환경변수에만 저장하고 GitHub에 올리지 마세요."
            )
        )
