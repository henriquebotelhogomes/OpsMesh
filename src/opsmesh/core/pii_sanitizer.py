"""OpsMesh PII Sanitizer Middleware with RFC 1918 VPC Preservation."""

import ipaddress
import re
from typing import Any

# Regexes para dados pessoais e credenciais
CPF_REGEX = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
CNPJ_REGEX = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
JWT_REGEX = re.compile(r"\beyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*\b")
BEARER_REGEX = re.compile(r"Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", re.IGNORECASE)
CREDENTIAL_KEY_REGEX = re.compile(
    r"(?i)(password|passwd|secret|api[_-]?key|token|auth_token)\s*[:=]\s*['\"]?([^'\"\s,]+)['\"]?"
)
IP_CANDIDATE_REGEX = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")


def _is_luhn_valid(card_number: str) -> bool:
    """Valida número de cartão via algoritmo de Luhn."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            d = d * 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def _mask_public_ips(text: str) -> str:
    """Mascara apenas IPs públicos WAN, preservando IPs privados RFC 1918."""
    matches = list(IP_CANDIDATE_REGEX.finditer(text))
    if not matches:
        return text

    result = []
    last_idx = 0
    for m in matches:
        ip_str = m.group(0)
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            # Se for IP de rede privada (10.x, 172.16-31.x, 192.168.x, 127.x), PRESERVA
            if ip_obj.is_private or ip_obj.is_loopback:
                result.append(text[last_idx : m.end()])
            else:
                result.append(text[last_idx : m.start()])
                result.append("[REDACTED_PUBLIC_IP]")
        except ValueError:
            result.append(text[last_idx : m.end()])
        last_idx = m.end()

    result.append(text[last_idx:])
    return "".join(result)


def sanitize_text(text: str) -> str:
    """Sanitiza string com dados sensíveis sem comprometer a topologia de cluster."""
    if not text:
        return ""

    # 1. Credenciais explícitas (senhas, API keys em URLs ou connection strings)
    text = CREDENTIAL_KEY_REGEX.sub(r"\1=[REDACTED_CREDENTIAL]", text)
    text = BEARER_REGEX.sub("Bearer [REDACTED_TOKEN]", text)
    text = JWT_REGEX.sub("[REDACTED_JWT]", text)

    # 2. Documentos pessoais brasileiros (LGPD)
    text = CPF_REGEX.sub("[REDACTED_CPF]", text)
    text = CNPJ_REGEX.sub("[REDACTED_CNPJ]", text)

    # 3. E-mails de clientes
    text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)

    # 4. Cartões de Crédito (detecção com Luhn)
    potential_cards = re.findall(r"\b(?:\d[ -]*?){13,19}\b", text)
    for candidate in potential_cards:
        clean = "".join(filter(str.isdigit, candidate))
        if _is_luhn_valid(clean):
            text = text.replace(candidate, "[REDACTED_CARD]")

    # 5. Mascaramento inteligente de IPs
    text = _mask_public_ips(text)

    return text


def sanitize_payload(obj: Any, preserve_rfc1918: bool = True) -> Any:
    """Aplica sanitização recursiva em dicts, listas e strings."""
    if isinstance(obj, str):
        return sanitize_text(obj)
    elif isinstance(obj, dict):
        return {k: sanitize_payload(v, preserve_rfc1918) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_payload(item, preserve_rfc1918) for item in obj]
    return obj


# Alias for backward/forward compatibility
sanitize_pii = sanitize_payload

__all__ = ["sanitize_text", "sanitize_payload", "sanitize_pii"]
