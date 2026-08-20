import os

import resend


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv(
    "EMAIL_FROM",
    "E-Commerce API <onboarding@resend.dev>",
)
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000",
)


def configure_resend() -> None:
    if not RESEND_API_KEY:
        raise RuntimeError(
            "RESEND_API_KEY environment variable is not configured."
        )

    resend.api_key = RESEND_API_KEY


def send_verification_email(
    email: str,
    verification_token: str,
) -> None:
    configure_resend()

    verification_url = (
        f"{FRONTEND_URL}/verify-email"
        f"?token={verification_token}"
    )

    params: resend.Emails.SendParams = {
        "from": EMAIL_FROM,
        "to": [email],
        "subject": "Verify your email",
        "html": (
            "<h2>Verify your email</h2>"
            "<p>Thanks for creating an account.</p>"
            "<p>Use the link below to verify your email address:</p>"
            f'<p><a href="{verification_url}">'
            "Verify Email"
            "</a></p>"
            "<p>This verification link expires in 24 hours.</p>"
        ),
    }

    resend.Emails.send(params)


def send_password_reset_email(
    email: str,
    password_reset_token: str,
) -> None:
    configure_resend()

    reset_url = (
        f"{FRONTEND_URL}/reset-password"
        f"?token={password_reset_token}"
    )

    params: resend.Emails.SendParams = {
        "from": EMAIL_FROM,
        "to": [email],
        "subject": "Reset your password",
        "html": (
            "<h2>Reset your password</h2>"
            "<p>We received a request to reset your password.</p>"
            "<p>Use the link below to choose a new password:</p>"
            f'<p><a href="{reset_url}">'
            "Reset Password"
            "</a></p>"
            "<p>This password reset link expires in 1 hour.</p>"
            "<p>If you did not request a password reset, "
            "you can ignore this email.</p>"
        ),
    }

    resend.Emails.send(params)