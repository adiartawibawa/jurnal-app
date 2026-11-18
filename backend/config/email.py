import logging
import smtplib
from email.message import EmailMessage

from config.config import settings

logger = logging.getLogger(__name__)


def send_email(*, to: str, subject: str, body: str) -> None:
    """Mengirim email lewat SMTP. Tidak pernah melempar error (hanya dicatat di log)."""
    # Tanpa SMTP_HOST: mode development mencetak isi email ke log agar mudah diuji.
    if not settings.SMTP_HOST:
        if settings.FASTAPI_ENV == "development":
            logger.warning("[EMAIL DEV] Ke: %s | Subjek: %s\n%s", to, subject, body)
        else:
            logger.error("SMTP_HOST belum diatur, email ke %s tidak terkirim", to)
        return

    message = EmailMessage()
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            if settings.SMTP_TLS:
                smtp.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except Exception:
        logger.exception("Gagal mengirim email ke %s", to)


def send_reset_password_email(*, to: str, token: str) -> None:
    """Menyusun dan mengirim email berisi tautan reset password."""
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    body = (
        "Halo,\n\n"
        "Kami menerima permintaan untuk mengatur ulang password akun Anda.\n"
        "Buka tautan berikut untuk membuat password baru:\n\n"
        f"{link}\n\n"
        f"Tautan ini berlaku selama {settings.RESET_TOKEN_EXPIRE_MINUTES} menit "
        "dan hanya bisa dipakai sekali.\n"
        "Jika Anda tidak memintanya, abaikan email ini; password Anda tidak berubah.\n"
    )
    send_email(to=to, subject=f"Reset password {settings.PROJECT_NAME}", body=body)