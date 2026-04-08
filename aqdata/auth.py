import logging

import requests

logger = logging.getLogger(__name__)


def login(session: requests.Session, base_url: str, user: str, password: str) -> bool:
    """Login to AqData and return True on success. Session cookies are kept on the session object."""
    url = f"{base_url}/engine.php"
    params = {"class": "loginMorador", "method": "onLogin"}
    data = {"login": user, "senha": password}

    logger.info("Logging in as %s", user)
    resp = session.post(url, params=params, data=data)
    resp.raise_for_status()

    # Successful login redirects to MoradorPaginaExterna
    if "MoradorPaginaExterna" in resp.text:
        logger.info("Login successful")
        return True

    if "__adianti_error" in resp.text:
        logger.error("Login failed: server returned error")
        return False

    logger.error("Login failed: unexpected response")
    return False
