"""
network_radar.py — Radar des connexions réseau actives pour JARVIS
psutil (connexions TCP) + ip-api.com batch (GeoIP, gratuit, sans clé).
"""
import psutil
import requests
import time

# ── Config ────────────────────────────────────────────────────────────────────
_LOCAL_LAT = 46.0   # Centre France (configurable)
_LOCAL_LON = 2.0
_CACHE_TTL = 3600   # 1h — les IPs bougent peu

# ── État interne ──────────────────────────────────────────────────────────────
_geo_cache: dict = {}

# ── Plages IP privées à ignorer ───────────────────────────────────────────────
_PRIVATE = (
    '127.', '10.', '192.168.', '169.254.',
    '172.16.', '172.17.', '172.18.', '172.19.',
    '172.20.', '172.21.', '172.22.', '172.23.',
    '172.24.', '172.25.', '172.26.', '172.27.',
    '172.28.', '172.29.', '172.30.', '172.31.',
    '0.0.0.0', '::',
)

# ── Niveaux de risque pays ────────────────────────────────────────────────────
_HIGH_RISK   = {'RU', 'KP', 'IR', 'BY', 'SY'}
_MEDIUM_RISK = {'CN', 'VN', 'PK', 'NG', 'CU'}


def _is_private(ip: str) -> bool:
    return any(ip.startswith(p) for p in _PRIVATE) or ':' in ip


def _process_name(pid) -> str:
    if not pid:
        return "Système"
    try:
        return psutil.Process(pid).name()
    except Exception:
        return "Inconnu"


def _evict_stale() -> None:
    now = time.time()
    stale = [ip for ip, v in _geo_cache.items() if now - v.get("ts", 0) > _CACHE_TTL]
    for ip in stale:
        del _geo_cache[ip]


def _batch_geoip(ips: list) -> None:
    """Résolution GeoIP via ip-api.com (batch 100 IPs/req, 45 req/min gratuit)."""
    to_resolve = [ip for ip in ips if ip not in _geo_cache]
    if not to_resolve:
        return
    for start in range(0, len(to_resolve), 100):
        chunk = to_resolve[start:start + 100]
        try:
            resp = requests.post(
                "http://ip-api.com/batch?fields=status,country,countryCode,lat,lon,isp,query",
                json=[{"query": ip} for ip in chunk],
                timeout=8
            )
            if resp.ok:
                for r in resp.json():
                    ip = r.get("query", "")
                    if r.get("status") == "success":
                        _geo_cache[ip] = {
                            "country": r.get("country", "Inconnu"),
                            "cc": r.get("countryCode", "??"),
                            "lat": float(r.get("lat", 0)),
                            "lon": float(r.get("lon", 0)),
                            "isp": r.get("isp", ""),
                            "ts": time.time()
                        }
                    else:
                        _geo_cache[ip] = {
                            "country": "Inconnu", "cc": "??",
                            "lat": 0.0, "lon": 0.0, "isp": "", "ts": time.time()
                        }
        except Exception as e:
            print(f"[RADAR] GeoIP error: {e}")


def get_radar_data() -> list:
    """Retourne les connexions TCP ESTABLISHED enrichies de géolocalisation."""
    _evict_stale()
    seen: dict = {}
    try:
        for conn in psutil.net_connections(kind='tcp'):
            if conn.status != 'ESTABLISHED' or not conn.raddr:
                continue
            ip = conn.raddr.ip
            if _is_private(ip) or ip in seen:
                continue
            seen[ip] = {"ip": ip, "port": conn.raddr.port, "process": _process_name(conn.pid)}
    except Exception as e:
        print(f"[RADAR] psutil error: {e}")
        return []

    if not seen:
        return []

    _batch_geoip(list(seen.keys()))

    result = []
    for ip, conn in seen.items():
        geo = _geo_cache.get(ip, {})
        lat, lon = geo.get("lat", 0), geo.get("lon", 0)
        if lat == 0 and lon == 0:
            continue
        cc = geo.get("cc", "??")
        risk = "high" if cc in _HIGH_RISK else ("medium" if cc in _MEDIUM_RISK else "normal")
        result.append({
            "ip": ip,
            "port": conn["port"],
            "process": conn["process"],
            "country": geo.get("country", "Inconnu"),
            "cc": cc,
            "lat": lat,
            "lon": lon,
            "isp": geo.get("isp", ""),
            "risk": risk
        })
    return result


def get_radar_summary(data: list) -> str:
    if not data:
        return "Aucune connexion externe active détectée, Monsieur."
    n = len(data)
    countries = list(set(c["country"] for c in data))
    high = [c for c in data if c["risk"] == "high"]
    txt = f"Radar réseau activé. {n} connexion{'s' if n > 1 else ''} active{'s' if n > 1 else ''} vers {len(countries)} pays."
    if high:
        procs = list(set(c["process"] for c in high))
        txt += f" Attention : {len(high)} connexion{'s' if len(high) > 1 else ''} à risque via {', '.join(procs)}."
    return txt
