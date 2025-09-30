"""
Share Link Manager - One-time Secure Report Sharing

This module provides secure, time-limited share links for PDF reports,
following privacy-by-design principles.

Design Philosophy:
Security through simplicity - cryptographically secure tokens,
automatic expiration, single-use links. No complex permission systems.
"""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import secrets
import hashlib


@dataclass
class ShareLink:
    """A secure, time-limited share link for a report."""
    link_id: str
    session_id: str
    token_hash: str
    created_at: datetime
    expires_at: datetime
    accessed_at: Optional[datetime] = None
    access_count: int = 0
    max_access_count: int = 1  # One-time use by default
    is_active: bool = True

    def is_expired(self) -> bool:
        """Check if the link has expired."""
        return datetime.utcnow() > self.expires_at

    def is_exhausted(self) -> bool:
        """Check if the link has reached maximum access count."""
        return self.access_count >= self.max_access_count

    def can_access(self) -> bool:
        """Check if the link can still be accessed."""
        return (
            self.is_active and
            not self.is_expired() and
            not self.is_exhausted()
        )


class ShareLinkManager:
    """
    Manages secure share links for reports.

    Provides cryptographically secure, time-limited, single-use links
    for sharing PDF reports while maintaining privacy and security.
    """

    def __init__(self, default_ttl_hours: int = 24, token_length: int = 32):
        """
        Initialize share link manager.

        Args:
            default_ttl_hours: Default time-to-live for links in hours
            token_length: Length of generated tokens in bytes
        """
        self.default_ttl_hours = default_ttl_hours
        self.token_length = token_length

    def generate_share_link(
        self,
        session_id: str,
        ttl_hours: Optional[int] = None,
        max_access_count: int = 1
    ) -> tuple[ShareLink, str]:
        """
        Generate a new secure share link.

        Args:
            session_id: Assessment session ID
            ttl_hours: Time-to-live in hours (default: 24)
            max_access_count: Maximum number of accesses (default: 1)

        Returns:
            Tuple of (ShareLink object, plain token string)
            The plain token is only available at creation time!
        """
        # Generate cryptographically secure token
        token = secrets.token_urlsafe(self.token_length)

        # Hash the token for storage (never store plain tokens!)
        token_hash = self._hash_token(token)

        # Generate unique link ID
        link_id = secrets.token_urlsafe(16)

        # Calculate expiration
        ttl = ttl_hours or self.default_ttl_hours
        expires_at = datetime.utcnow() + timedelta(hours=ttl)

        # Create ShareLink object
        share_link = ShareLink(
            link_id=link_id,
            session_id=session_id,
            token_hash=token_hash,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            max_access_count=max_access_count,
            is_active=True
        )

        return share_link, token

    def verify_token(self, link: ShareLink, token: str) -> bool:
        """
        Verify if a token matches a share link.

        Args:
            link: ShareLink object
            token: Plain token to verify

        Returns:
            True if token is valid, False otherwise
        """
        if not link.can_access():
            return False

        token_hash = self._hash_token(token)
        return secrets.compare_digest(token_hash, link.token_hash)

    def revoke_link(self, link: ShareLink) -> ShareLink:
        """
        Revoke a share link, making it immediately invalid.

        Args:
            link: ShareLink to revoke

        Returns:
            Updated ShareLink object
        """
        link.is_active = False
        return link

    def record_access(self, link: ShareLink) -> ShareLink:
        """
        Record an access to a share link.

        Args:
            link: ShareLink being accessed

        Returns:
            Updated ShareLink object
        """
        link.access_count += 1
        link.accessed_at = datetime.utcnow()

        # Auto-deactivate if exhausted
        if link.is_exhausted():
            link.is_active = False

        return link

    def get_link_status(self, link: ShareLink) -> dict:
        """
        Get human-readable status of a share link.

        Args:
            link: ShareLink to check

        Returns:
            Dictionary with status information
        """
        now = datetime.utcnow()
        time_remaining = link.expires_at - now

        if not link.is_active:
            status = "已撤銷"
        elif link.is_expired():
            status = "已過期"
        elif link.is_exhausted():
            status = "已用盡"
        else:
            status = "有效"

        return {
            "status": status,
            "is_valid": link.can_access(),
            "created_at": link.created_at.isoformat(),
            "expires_at": link.expires_at.isoformat(),
            "time_remaining_hours": time_remaining.total_seconds() / 3600 if time_remaining.total_seconds() > 0 else 0,
            "access_count": link.access_count,
            "max_access_count": link.max_access_count,
            "accessed_at": link.accessed_at.isoformat() if link.accessed_at else None
        }

    def _hash_token(self, token: str) -> str:
        """
        Hash a token using SHA-256.

        Args:
            token: Plain token string

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    def generate_share_url(
        self,
        base_url: str,
        link_id: str,
        token: str
    ) -> str:
        """
        Generate full share URL for a report.

        Args:
            base_url: Base URL of the application
            link_id: Share link ID
            token: Plain token (only available at creation!)

        Returns:
            Complete share URL
        """
        return f"{base_url}/api/v1/reports/share/{link_id}?token={token}"

    def cleanup_expired_links(self, links: list[ShareLink]) -> list[ShareLink]:
        """
        Filter out expired and exhausted links.

        Args:
            links: List of ShareLink objects

        Returns:
            List of still-valid links
        """
        return [
            link for link in links
            if link.can_access()
        ]