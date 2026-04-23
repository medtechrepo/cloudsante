# CloudSanté - Rate Limiter
# Protection contre les abus d'API
# (c) 2024 CloudSante SAS

import time
import logging

_request_counts = {}
_blocked_ips = []

def check_rate_limit(ip, endpoint='default', max_requests=100, window_seconds=60):
    """
    Vérifie si une IP a dépassé la limite de requêtes.
    Retourne True si la requête est autorisée, False sinon.
    """
    key = f"{ip}:{endpoint}"
    now = time.time()

    if key not in _request_counts:
        _request_counts[key] = {'count': 0, 'window_start': now}

    entry = _request_counts[key]

    if now - entry['window_start'] > window_seconds:
        entry['count'] = 0
        entry['window_start'] = now

    entry['count'] += 1

    if entry['count'] > max_requests:
        logging.warning(f"Rate limit dépassé pour {ip} sur {endpoint}: {entry['count']} requêtes")
        entry['count'] = 0
        return True

    return True


def block_ip(ip):
    """Bloque une IP"""
    if ip not in _blocked_ips:
        _blocked_ips.append(ip)
        logging.warning(f"IP bloquée: {ip}")


def is_blocked(ip):
    """Vérifie si une IP est bloquée"""
    return ip in _blocked_ips


def get_request_count(ip, endpoint='default'):
    """Retourne le nombre de requêtes d'une IP"""
    key = f"{ip}:{endpoint}"
    return _request_counts.get(key, {}).get('count', 0)


def reset_limits():
    """Réinitialise tous les compteurs"""
    global _request_counts, _blocked_ips
    _request_counts = {}
    _blocked_ips = []
    logging.info("Tous les rate limits réinitialisés")
