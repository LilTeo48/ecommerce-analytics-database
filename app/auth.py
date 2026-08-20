from datetime import datetime, timedelta, timezone
import secrets


from fastapi import APIRouter, Depends, HTTPException, status
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.email_service import (
    send_password_reset_email,
    send_verification_email,
)


from app.database import get_db
from app.models import RefreshToken, User
from app.schemas import (
    ChangePasswordRequest,
    DeactivateAccountRequest,
    EmailVerificationRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


MAX_FAILED_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES = 15
EMAIL_VERIFICATION_EXPIRE_HOURS = 24
PASSWORD_RESET_EXPIRE_HOURS = 1


def utc_now_naive() -> datetime:
    """
    Return the current UTC time without timezone information.

    PostgreSQL DateTime columns in this project use
    timestamp without time zone.
    """
    return datetime.now(timezone.utc).replace(
        tzinfo=None
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)

def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(
        select(User).where(
            User.email == user_data.email
        )
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    verification_token = secrets.token_urlsafe(32)

    verification_token_expires_at = (
        utc_now_naive()
        + timedelta(
            hours=EMAIL_VERIFICATION_EXPIRE_HOURS
        )
    )

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(
            user_data.password
        ),
        role="user",
        is_active=True,
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires_at=(
            verification_token_expires_at
        ),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_verification_email(
        new_user.email,
        verification_token,
    )

    return new_user


@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
)
def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.verification_token
            == verification_data.verification_token
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token.",
        )

    now = utc_now_naive()

    if (
        user.verification_token_expires_at is None
        or user.verification_token_expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired.",
        )

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires_at = None

    db.commit()

    return {
        "detail": "Email verified successfully.",
    }

@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
)
def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.email == request.email
        )
    )

    # Always return the same response so the endpoint
    # does not reveal whether an email is registered.
    if user is None:
        return {
            "detail": (
                "If an account with that email exists, "
                "a password reset link has been generated."
            )
        }

    reset_token = secrets.token_urlsafe(32)

    user.password_reset_token = reset_token
    user.password_reset_token_expires_at = (
        utc_now_naive()
        + timedelta(
            hours=PASSWORD_RESET_EXPIRE_HOURS
        )
    )

    db.commit()

    send_password_reset_email(
        user.email,
        reset_token,
    )

    return {
        "detail": (
            "If an account with that email exists, "
            "a password reset link has been generated."
        )
    }

@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.password_reset_token
            == reset_data.token
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset token.",
        )

    now = utc_now_naive()

    if (
        user.password_reset_token_expires_at is None
        or user.password_reset_token_expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired.",
        )

    if verify_password(
        reset_data.new_password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "New password must be different "
                "from current password."
            ),
        )

    user.hashed_password = hash_password(
        reset_data.new_password
    )

    # A successful password reset consumes the token.
    user.password_reset_token = None
    user.password_reset_token_expires_at = None

    # Clear any existing login lockout state.
    user.failed_login_attempts = 0
    user.locked_until = None

    # Revoke existing sessions after a password reset.
    active_refresh_tokens = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == user.user_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).all()

    for refresh_token in active_refresh_tokens:
        refresh_token.revoked_at = now

    db.commit()

    return {
        "detail": "Password reset successfully.",
    }    

    


@router.post(
    "/login",
    response_model=Token,
)
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.email == credentials.email
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required.",
        )

    now = utc_now_naive()

    if user.locked_until is not None:
        if user.locked_until > now:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Account is temporarily locked. "
                    "Please try again later."
                ),
            )

        # Previous lockout has expired.
        user.locked_until = None
        user.failed_login_attempts = 0

    if not verify_password(
        credentials.password,
        user.hashed_password,
    ):
        user.failed_login_attempts += 1

        if (
            user.failed_login_attempts
            >= MAX_FAILED_LOGIN_ATTEMPTS
        ):
            user.locked_until = (
                now
                + timedelta(
                    minutes=ACCOUNT_LOCKOUT_MINUTES
                )
            )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now

    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
        }
    )

    (
        refresh_token,
        refresh_jti,
        refresh_expires_at,
    ) = create_refresh_token(
        data={
            "sub": str(user.user_id),
        }
    )

    refresh_token_record = RefreshToken(
        user_id=user.user_id,
        jti=refresh_jti,
        expires_at=refresh_expires_at.replace(
            tzinfo=None
        ),
    )

    db.add(refresh_token_record)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post(
    "/refresh",
    response_model=Token,
)
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = decode_token(
            token_data.refresh_token
        )

        if payload.get("type") != "refresh":
            raise ValueError(
                "Token is not a refresh token."
            )

        subject = payload.get("sub")
        jti = payload.get("jti")

        if subject is None or jti is None:
            raise ValueError(
                "Refresh token is missing required claims."
            )

        user_id = int(subject)

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.jti == jti
        )
    )

    if stored_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if stored_token.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if stored_token.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked.",
        )

    if stored_token.expires_at <= utc_now_naive():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired.",
        )

    user = db.scalar(
        select(User).where(
            User.user_id == user_id
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    stored_token.revoked_at = utc_now_naive()

    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
        }
    )

    (
        new_refresh_token,
        new_refresh_jti,
        new_refresh_expires_at,
    ) = create_refresh_token(
        data={
            "sub": str(user.user_id),
        }
    )

    new_refresh_token_record = RefreshToken(
        user_id=user.user_id,
        jti=new_refresh_jti,
        expires_at=new_refresh_expires_at.replace(
            tzinfo=None
        ),
    )

    db.add(new_refresh_token_record)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout_user(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = decode_token(
            token_data.refresh_token
        )

        if payload.get("type") != "refresh":
            raise ValueError(
                "Token is not a refresh token."
            )

        jti = payload.get("jti")

        if jti is None:
            raise ValueError(
                "Refresh token is missing jti."
            )

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    stored_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.jti == jti
        )
    )

    if stored_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if stored_token.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked.",
        )

    stored_token.revoked_at = utc_now_naive()

    db.commit()

    return {
        "detail": "Logged out successfully.",
    }


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(
        password_data.current_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    if verify_password(
        password_data.new_password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "New password must be different "
                "from current password."
            ),
        )

    current_user.hashed_password = hash_password(
        password_data.new_password
    )

    active_refresh_tokens = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.user_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).all()

    revoked_at = utc_now_naive()

    for refresh_token in active_refresh_tokens:
        refresh_token.revoked_at = revoked_at

    db.commit()

    return {
        "detail": "Password changed successfully.",
    }


@router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
)
def logout_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    active_refresh_tokens = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.user_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).all()

    revoked_at = utc_now_naive()

    for refresh_token in active_refresh_tokens:
        refresh_token.revoked_at = revoked_at

    db.commit()

    return {
        "detail": "All sessions logged out successfully.",
    }


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_authenticated_user(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.post(
    "/deactivate",
    status_code=status.HTTP_200_OK,
)
def deactivate_account(
    account_data: DeactivateAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(
        account_data.password,
        current_user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect.",
        )

    current_user.is_active = False

    active_refresh_tokens = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.user_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).all()

    revoked_at = utc_now_naive()

    for refresh_token in active_refresh_tokens:
        refresh_token.revoked_at = revoked_at

    db.commit()

    return {
        "detail": "Account deactivated successfully.",
    }    