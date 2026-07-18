import asyncio
import unittest

from fastapi import HTTPException

from api import ewu_bot_webhook


class FakeRequest:
    def __init__(self, body: bytes, headers=None):
        self._body = body
        self.headers = headers or {}

    async def body(self) -> bytes:
        return self._body


class EwuBotWebhookSecurityTests(unittest.TestCase):
    def test_rejects_payload_larger_than_content_length_limit(self):
        request = FakeRequest(b"{}", headers={"content-length": str(ewu_bot_webhook.MAX_WEBHOOK_BODY_BYTES + 1)})

        with self.assertRaises(HTTPException) as ctx:
            with asyncio.Runner() as runner:
                runner.run(ewu_bot_webhook._read_webhook_body(request))

        self.assertEqual(ctx.exception.status_code, 413)

    def test_rejects_invalid_content_length(self):
        request = FakeRequest(b"{}", headers={"content-length": "invalid"})

        with self.assertRaises(HTTPException) as ctx:
            with asyncio.Runner() as runner:
                runner.run(ewu_bot_webhook._read_webhook_body(request))

        self.assertEqual(ctx.exception.status_code, 400)

    def test_rejects_payload_larger_than_actual_body_limit(self):
        request = FakeRequest(b"x" * (ewu_bot_webhook.MAX_WEBHOOK_BODY_BYTES + 1))

        with self.assertRaises(HTTPException) as ctx:
            with asyncio.Runner() as runner:
                runner.run(ewu_bot_webhook._read_webhook_body(request))

        self.assertEqual(ctx.exception.status_code, 413)

    def test_accepts_small_payload(self):
        request = FakeRequest(b'{"update_id":1}')

        with asyncio.Runner() as runner:
            body = runner.run(ewu_bot_webhook._read_webhook_body(request))

        self.assertEqual(body, b'{"update_id":1}')


if __name__ == "__main__":
    unittest.main()
