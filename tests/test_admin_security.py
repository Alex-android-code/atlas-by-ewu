import os
import unittest
from types import SimpleNamespace

from fastapi import HTTPException

from api import app as app_module


def request(cookies=None, headers=None, host="unit-test", scheme="https"):
    return SimpleNamespace(
        cookies=cookies or {},
        headers=headers or {},
        client=SimpleNamespace(host=host),
        url=SimpleNamespace(scheme=scheme),
    )


class AdminSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_env = {
            "ATLAS_ADMIN_PASSWORD": os.environ.pop("ATLAS_ADMIN_PASSWORD", None),
            "ATLAS_ADMIN_PASSWORD_HASH": os.environ.pop("ATLAS_ADMIN_PASSWORD_HASH", None),
            "ATLAS_ADMIN_TOKEN": os.environ.pop("ATLAS_ADMIN_TOKEN", None),
        }
        app_module._ADMIN_SESSIONS.clear()
        app_module._ADMIN_LOGIN_ATTEMPTS.clear()

    def tearDown(self) -> None:
        for key, value in self.previous_env.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)
        app_module._ADMIN_SESSIONS.clear()
        app_module._ADMIN_LOGIN_ATTEMPTS.clear()

    def test_legacy_atlas_password_is_not_valid_without_env_secret(self):
        self.assertFalse(app_module._valid_admin_password("atlas"))

    def test_env_admin_token_can_authorize_service_requests(self):
        os.environ["ATLAS_ADMIN_TOKEN"] = "secret-token"

        self.assertTrue(app_module._is_admin_authorized(request(headers={"x-atlas-admin-token": "secret-token"})))
        self.assertFalse(app_module._is_admin_authorized(request(headers={"x-atlas-admin-token": "wrong"})))

    def test_crm_list_endpoints_require_admin(self):
        protected_handlers = (
            app_module.get_dashboard,
            app_module.list_candidates,
            app_module.list_employers,
            app_module.list_vacancies,
            app_module.list_matches,
            app_module.list_activity,
        )

        for handler in protected_handlers:
            with self.subTest(handler=handler.__name__):
                with self.assertRaises(HTTPException) as ctx:
                    handler(request())
                self.assertEqual(ctx.exception.status_code, 403)

    def test_admin_login_rate_limit_blocks_repeated_attempts(self):
        for _ in range(app_module.ADMIN_LOGIN_LIMIT_PER_MINUTE):
            app_module._enforce_admin_login_rate_limit("1.2.3.4")

        with self.assertRaises(HTTPException) as ctx:
            app_module._enforce_admin_login_rate_limit("1.2.3.4")

        self.assertEqual(ctx.exception.status_code, 429)


if __name__ == "__main__":
    unittest.main()
