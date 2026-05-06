"""Authenticated httpx client for service-to-service calls on Cloud Run.

In Cloud Run: identity token comes from the Compute Metadata server.
Locally: identity token comes from the gcloud CLI.

The receiving Cloud Run service rejects calls without a valid signed token.
"""

from urllib.parse import urlparse

import httpx
from google.auth.transport.requests import AuthorizedSession, Request
from google.oauth2 import id_token as id_token_lib
from google.auth import compute_engine, default


def create_authenticated_client(remote_service_url: str, timeout: float = 600.0) -> httpx.AsyncClient:
    """Build an httpx.AsyncClient that signs every request with a Google ID token.

    The audience for the token is the root URL of the remote service (no path).
    """
    parsed = urlparse(remote_service_url)
    root_url = f"{parsed.scheme}://{parsed.netloc}"

    class _IdentityTokenAuth(httpx.Auth):
        def __init__(self, audience: str):
            self.audience = audience
            self.session: AuthorizedSession | None = None

        def _refresh(self) -> str:
            try:
                # In Cloud Run / GCE: metadata server credentials
                credentials = compute_engine.IDTokenCredentials(
                    request=Request(),
                    target_audience=self.audience,
                )
            except Exception:
                # Fallback: ADC (e.g. gcloud auth application-default login)
                credentials, _ = default()
                credentials = id_token_lib.IDTokenCredentials.from_service_account_info(
                    info={}, target_audience=self.audience,
                ) if hasattr(credentials, "service_account_email") else credentials

            credentials.refresh(Request())
            self.session = AuthorizedSession(credentials)
            return self.session.credentials.token

        def auth_flow(self, request):
            if self.session is None or not self.session.credentials.valid:
                token = self._refresh()
            else:
                token = self.session.credentials.token

            if token:
                request.headers["Authorization"] = f"Bearer {token}"
            yield request

    return httpx.AsyncClient(
        auth=_IdentityTokenAuth(root_url),
        follow_redirects=True,
        timeout=timeout,
    )
