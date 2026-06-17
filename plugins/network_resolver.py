"""
network_resolver.py — Commandes vocales pour le radar réseau JARVIS
"""
import asyncio
import json
import unicodedata
import builtins

_radar_active = False
_radar_task = None


def _clean(t: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', t)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()


async def _broadcast(data: dict) -> None:
    if builtins.CONNECTED_CLIENTS:
        msg = json.dumps(data)
        await asyncio.gather(
            *[ws.send(msg) for ws in builtins.CONNECTED_CLIENTS],
            return_exceptions=True
        )


async def _radar_loop() -> None:
    global _radar_active
    while _radar_active:
        try:
            from module.network_radar import get_radar_data
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, get_radar_data)
            await _broadcast({"action": "network_radar_update", "connections": data})
        except asyncio.CancelledError:
            break
        except RuntimeError as e:
            if "shutdown" in str(e) or "closed" in str(e):
                break
            print(f"[RADAR] Loop error: {e}")
        except Exception as e:
            print(f"[RADAR] Loop error: {e}")
        try:
            await asyncio.sleep(6)
        except asyncio.CancelledError:
            break


async def resoudre_connexions_reseau(cmd: str):
    global _radar_active, _radar_task
    t = _clean(cmd)

    if not any(m in t for m in ["radar", "reseau", "connexion", "connexions", "trafic"]):
        return None

    mots_hide = ["cache", "ferme", "stop", "arrete", "desactive", "masque", "quitte", "coupe", "eteins"]
    if any(m in t for m in mots_hide):
        _radar_active = False
        if _radar_task and not _radar_task.done():
            _radar_task.cancel()
        await _broadcast({"action": "network_radar_hide"})
        return "Radar réseau désactivé, Monsieur."

    mots_show = ["montre", "affiche", "active", "lance", "ouvre", "voir", "demarre", "radar reseau", "connexions"]
    if any(m in t for m in mots_show) or t == "radar":
        from module.network_radar import get_radar_data, get_radar_summary
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, get_radar_data)
        await _broadcast({"action": "network_radar_show", "connections": data})
        _radar_active = True
        if _radar_task and not _radar_task.done():
            _radar_task.cancel()
        _radar_task = asyncio.create_task(_radar_loop())
        return get_radar_summary(data)

    return None


builtins.resoudre_connexions_reseau = resoudre_connexions_reseau
