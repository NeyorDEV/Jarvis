import time
import asyncio
import subprocess
import os
import requests
import re
from datetime import datetime
import contextlib

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import uiautomation as auto
except ImportError:
    auto = None

# Chemins d'installation de Deezer
DEEZER_EXE = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop\Deezer.exe"
DEEZER_DIR = r"C:\Users\mylan\AppData\Local\Programs\deezer-desktop"

_cached_deezer_pids = []

def _initialize_com():
    """Initialise COM en MTA pour le thread actuel si ce n'est pas déjà fait."""
    import ctypes
    try:
        ctypes.windll.ole32.CoInitializeEx(None, 0)
    except:
        try:
            ctypes.windll.ole32.CoInitialize(None)
        except:
            pass

def _get_deezer_pids():
    """Récupère rapidement les PIDs de Deezer.exe via les processus actifs."""
    global _cached_deezer_pids
    import psutil
    
    # Vérifier si les PIDs en cache sont toujours valides
    if _cached_deezer_pids:
        valides = []
        for pid in _cached_deezer_pids:
            try:
                if psutil.pid_exists(pid):
                    p = psutil.Process(pid)
                    if 'deezer' in p.name().lower():
                        valides.append(pid)
            except:
                pass
        if valides:
            return valides
            
    deezer_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'deezer' in proc.info['name'].lower():
                deezer_pids.append(proc.info['pid'])
        except:
            pass
            
    _cached_deezer_pids = deezer_pids
    return deezer_pids

def _attendre_deezer_prete(timeout=8.0):
    """Attend dynamiquement que le contrôle principal de Deezer soit accessible."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        ctrl = get_deezer_main_control()
        if ctrl:
            try:
                children = ctrl.GetChildren()
                if children:
                    print(f"[DEEZER] Prêt détecté après {time.time() - t0:.2f}s.")
                    return ctrl
            except:
                pass
        time.sleep(0.15)
    print(f"[DEEZER] Timeout attente prête après {timeout}s.")
    return get_deezer_main_control()

def get_deezer_main_control():
    """Trouve le DocumentControl (Chrome_RenderWidgetHostHWND) principal de Deezer."""
    if not auto:
        return None
    try:
        _initialize_com()
        import win32gui
        import win32process
        
        deezer_pids = _get_deezer_pids()
        if not deezer_pids:
            return None
            
        render_hwnds = []
        def enum_windows_callback(hwnd, extra):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid in deezer_pids:
                def child_callback(child_hwnd, _):
                    c_class = win32gui.GetClassName(child_hwnd)
                    if c_class == "Chrome_RenderWidgetHostHWND":
                        render_hwnds.append(child_hwnd)
                    return True
                try:
                    win32gui.EnumChildWindows(hwnd, child_callback, None)
                except:
                    pass
            return True

        win32gui.EnumWindows(enum_windows_callback, None)
        
        best_ctrl = None
        max_buttons = -1
        
        for r_hwnd in render_hwnds:
            try:
                # Activer l'accessibilité Chromium
                win32gui.SendMessage(r_hwnd, 0x003D, 0, 0xFFFFFFFC)
            except:
                pass
                
            try:
                ctrl = auto.ControlFromHandle(r_hwnd)
                if ctrl and ctrl.Exists(0.1):
                    buttons_count = 0
                    def count_buttons(c):
                        nonlocal buttons_count
                        if c.ControlTypeName == "ButtonControl":
                            buttons_count += 1
                        for child in c.GetChildren():
                            count_buttons(child)
                    count_buttons(ctrl)
                    
                    if buttons_count > max_buttons:
                        max_buttons = buttons_count
                        best_ctrl = ctrl
            except:
                pass
                
        return best_ctrl
    except Exception as e:
        print(f"[DEEZER UIA] Erreur get_deezer_main_control : {e}")
    return None

def _sauter_deezer_accessible():
    """Vérifie si Deezer tourne avec l'accessibilité activée."""
    return get_deezer_main_control()

def _focus_deezer():
    """Met la fenêtre Deezer au premier plan."""
    try:
        ctrl = get_deezer_main_control()
        if ctrl:
            top = ctrl.GetTopLevelControl()
            if top:
                import win32gui, win32con
                hwnd = top.NativeWindowHandle
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    try: top.SetActive()
                    except: pass
                    try: top.SetFocus()
                    except: pass
                    try: win32gui.SetForegroundWindow(hwnd)
                    except: pass
                    time.sleep(0.3)
                    return True
    except Exception as e:
        print(f"[DEEZER UIA] Échec _focus_deezer UIA: {e}")
        
    try:
        import win32gui, win32con
        candidats = []
        def _cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                titre = win32gui.GetWindowText(hwnd)
                if "Deezer" in titre:
                    candidats.append(hwnd)
        win32gui.EnumWindows(_cb, None)
        if not candidats:
            return False
        hwnd = candidats[0]
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.4)
        return True
    except Exception:
        return False

def _restore_focus(hwnd):
    """Restaure le focus sur la fenêtre d'origine."""
    if not hwnd:
        return
    try:
        import win32gui
        import win32con
        import ctypes
        if not win32gui.IsWindow(hwnd):
            return
        active_now = win32gui.GetForegroundWindow()
        if active_now == hwnd:
            return
        # Simulation touche Alt pour contourner restriction SetForegroundWindow
        ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)
        time.sleep(0.01)
        ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"[DEEZER UIA] Impossible de restaurer le focus : {e}")

@contextlib.contextmanager
def prevent_focus_theft():
    """Contexte empêchant Deezer de voler le focus actif de l'utilisateur."""
    modified_hwnds = []
    try:
        import win32gui
        import win32process
        import win32con
        
        deezer_pids = _get_deezer_pids()
        if deezer_pids:
            hwnds = []
            def enum_windows_callback(hwnd, extra):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid in deezer_pids:
                    classname = win32gui.GetClassName(hwnd)
                    if "Chrome_WidgetWin" in classname:
                        hwnds.append(hwnd)
                return True
            win32gui.EnumWindows(enum_windows_callback, None)
            
            for hwnd in hwnds:
                try:
                    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    if not (style & 0x08000000): # WS_EX_NOACTIVATE
                        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | 0x08000000)
                        win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
                                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | 
                                              win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED | 
                                              win32con.SWP_NOACTIVATE)
                        modified_hwnds.append((hwnd, style))
                except:
                    pass
    except Exception as e:
        print(f"[DEEZER UIA] Échec prevent_focus_theft : {e}")
        
    try:
        yield
    finally:
        for hwnd, old_style in modified_hwnds:
            try:
                import win32gui
                import win32con
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, old_style)
                win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
                                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | 
                                      win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED | 
                                      win32con.SWP_NOACTIVATE)
            except:
                pass

def _clic_control(btn):
    """Effectue un clic sur un contrôle UIA de manière silencieuse (background)."""
    with prevent_focus_theft():
        hwnd_before = None
        try:
            import win32gui
            hwnd_before = win32gui.GetForegroundWindow()
        except:
            pass

        try:
            rect = btn.BoundingRectangle
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            if width <= 0 or height <= 0:
                print(f"[DEEZER UIA] Clic ignoré : dimensions nulles ({width}x{height})")
                return False
                
            # 1. LegacyIAccessible (virtuel, n'affecte pas le focus)
            try:
                legacy_pat = btn.GetLegacyIAccessiblePattern()
                if legacy_pat:
                    legacy_pat.DoDefaultAction()
                    time.sleep(0.1)
                    active_now = win32gui.GetForegroundWindow()
                    if active_now != hwnd_before and hwnd_before != 0:
                        _restore_focus(hwnd_before)
                    return True
            except Exception as e:
                pass

            # 2. InvokePattern
            try:
                pattern = btn.GetInvokePattern()
                if pattern:
                    pattern.Invoke()
                    _restore_focus(hwnd_before)
                    return True
            except Exception as e:
                pass

            # 3. Fallback clic physique
            try:
                btn.Click(simulateMove=False)
                _restore_focus(hwnd_before)
                return True
            except Exception as e:
                pass
                
            return False
        except Exception as ex:
            print(f"[DEEZER UIA] Erreur clic contrôle : {ex}")
            return False

def find_player_button(deezer_ctrl, button_names):
    """Trouve un bouton du player principal."""
    buttons = []
    def _collect_buttons(control):
        if control.ControlTypeName == "ButtonControl":
            name = control.Name or ""
            if name in button_names or any(b in name for b in button_names):
                buttons.append(control)
        for child in control.GetChildren():
            _collect_buttons(child)
            
    _collect_buttons(deezer_ctrl)
    
    for btn in buttons:
        parent = btn.GetParentControl()
        if parent:
            sibling_names = [c.Name for c in parent.GetChildren() if c.ControlTypeName == "ButtonControl"]
            if "Suivant" in sibling_names or "Précédent" in sibling_names:
                return btn
    if buttons:
        return buttons[0]
    return None

def find_page_play_button(deezer_ctrl, button_names):
    """Recherche le bouton de lecture au sein de la page."""
    buttons = []
    def _collect_buttons(control):
        if control.ControlTypeName == "ButtonControl":
            name = control.Name or ""
            if name in button_names or any(b in name for b in button_names):
                try:
                    rect = control.BoundingRectangle
                    if rect.right - rect.left > 0:
                        buttons.append(control)
                except:
                    pass
        for child in control.GetChildren():
            _collect_buttons(child)
            
    _collect_buttons(deezer_ctrl)
    
    page_buttons = []
    for btn in buttons:
        parent = btn.GetParentControl()
        is_player_bar = False
        if parent:
            sibling_names = [c.Name for c in parent.GetChildren() if c.ControlTypeName == "ButtonControl"]
            if "Suivant" in sibling_names or "Précédent" in sibling_names:
                is_player_bar = True
        if not is_player_bar:
            page_buttons.append(btn)
            
    if page_buttons:
        return page_buttons[0]
    if buttons:
        return buttons[0]
    return None

def _uia_clic_bouton(noms_boutons):
    """Recherche le bouton dans le lecteur et clique dessus."""
    if not auto:
        return False
    try:
        deezer_ctrl = get_deezer_main_control()
        if not deezer_ctrl:
            return False
        btn = find_player_button(deezer_ctrl, noms_boutons)
        if btn:
            return _clic_control(btn)
    except Exception as e:
        print(f"[DEEZER UIA] Échec clic bouton {noms_boutons} : {e}")
    return False

def _uia_clic_bouton_page_dynamique(noms_boutons, timeout=12, wait_for_title=None):
    """Attend le chargement de la page et clique sur son bouton de lecture."""
    if not auto:
        return False
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            deezer_ctrl = get_deezer_main_control()
            if deezer_ctrl:
                if wait_for_title:
                    doc_title = deezer_ctrl.Name or ""
                    if wait_for_title.lower() not in doc_title.lower() and "deezer" not in doc_title.lower():
                        time.sleep(0.25)
                        continue
                        
                btn = find_page_play_button(deezer_ctrl, noms_boutons)
                if btn:
                    if _clic_control(btn):
                        return True
        except:
            pass
        time.sleep(0.3)
    return False

def _uia_clic_bouton_piste_album(track_title, artist_name=None, timeout=20):
    """Trouve et clique la ligne d'un morceau sur la page album ou playlist."""
    if not auto:
        return False
    t0 = time.time()
    track_title_lower = track_title.lower()
    while time.time() - t0 < timeout:
        try:
            deezer_ctrl = get_deezer_main_control()
            if deezer_ctrl:
                def _find_track_row_button(c, depth=0):
                    if depth > 15:
                        return None
                    ctype = c.ControlTypeName or ""
                    name = c.Name or ""
                    if ctype == "ButtonControl" and name.lower().startswith("écouter"):
                        if track_title_lower in name.lower():
                            if not artist_name or artist_name.lower() in name.lower():
                                try:
                                    rect = c.BoundingRectangle
                                    if (rect.right - rect.left) > 0 and (rect.bottom - rect.top) > 0:
                                        return c
                                except:
                                    pass
                    for child in c.GetChildren():
                        res = _find_track_row_button(child, depth + 1)
                        if res:
                            return res
                    return None
                
                btn = _find_track_row_button(deezer_ctrl)
                if btn:
                    return _clic_control(btn)
        except:
            pass
        time.sleep(0.3)
    return False

def _uia_taper_dans_recherche(query):
    """Saisit du texte dans l'EditControl de recherche sans voler le focus."""
    if not auto:
        return False
    try:
        _initialize_com()
        with prevent_focus_theft():
            deezer_ctrl = get_deezer_main_control()
            if not deezer_ctrl:
                return False
                
            search_edit = None
            def _find_edit(c, depth=0):
                if c.ControlTypeName == "EditControl" and depth < 15:
                    name = c.Name or ""
                    auto_id = c.AutomationId or ""
                    if name == "Rechercher" or "search" in auto_id.lower() or name.lower() == "search":
                        return c
                if depth < 15:
                    for child in c.GetChildren():
                        res = _find_edit(child, depth + 1)
                        if res:
                            return res
                return None
            search_edit = _find_edit(deezer_ctrl)
            
            if not search_edit:
                print("[DEEZER UIA] Barre de recherche introuvable")
                return False
                
            # Tenter via ValuePattern
            try:
                val_pat = search_edit.GetValuePattern()
                if val_pat:
                    val_pat.SetValue(query)
                    time.sleep(1.8)
                    return True
            except:
                pass
                
            # Tenter via LegacyIAccessiblePattern
            try:
                legacy_pat = search_edit.GetLegacyIAccessiblePattern()
                if legacy_pat:
                    legacy_pat.SetValue(query)
                    time.sleep(1.8)
                    return True
            except:
                pass
                
    except Exception as e:
        print(f"[DEEZER UIA] Échec saisie recherche : {e}")
    return False

def _ouvrir_uri_deezer(uri):
    """Ouvre une URI Deezer native en arrière-plan."""
    try:
        subprocess.Popen(["explorer", uri], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[DEEZER UIA] Échec ouverture URI {uri} : {e}")

async def deezer_ouvrir():
    """Lance Deezer s'il n'est pas ouvert en s'assurant que l'accessibilité soit active."""
    try:
        _initialize_com()
        import win32gui
        import win32process
        import win32con
        import psutil
        
        deezer_pids = _get_deezer_pids()
        hwnd = None
        if deezer_pids:
            def enum_windows_callback(h, extra):
                nonlocal hwnd
                _, pid = win32process.GetWindowThreadProcessId(h)
                if pid in deezer_pids:
                    classname = win32gui.GetClassName(h)
                    if "Chrome_WidgetWin" in classname:
                        if not win32gui.GetParent(h):
                            hwnd = h
                            return False
                return True
            try:
                win32gui.EnumWindows(enum_windows_callback, None)
            except:
                pass

        if hwnd:
            try:
                if not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNOACTIVATE)
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    _attendre_deezer_prete(3.0)
            except:
                pass
            return "Deezer est déjà ouvert et accessible, mylane."

        # Si processus présent mais pas de fenêtre accessible, on le redémarre
        if deezer_pids:
            for pid in deezer_pids:
                try: psutil.Process(pid).kill()
                except: pass
            time.sleep(1.5)

        if os.path.exists(DEEZER_EXE):
            hwnd_before = None
            try: hwnd_before = win32gui.GetForegroundWindow()
            except: pass
            
            subprocess.Popen(
                [DEEZER_EXE, "--force-renderer-accessibility"],
                cwd=DEEZER_DIR,
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            _attendre_deezer_prete(8.0)
            if hwnd_before and hwnd_before != 0:
                _restore_focus(hwnd_before)
            return "Deezer lancé en mode accessible, mylane."
        else:
            hwnd_before = None
            try: hwnd_before = win32gui.GetForegroundWindow()
            except: pass
            subprocess.Popen(
                ["explorer", "deezer:"],
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            _attendre_deezer_prete(6.0)
            if hwnd_before and hwnd_before != 0:
                _restore_focus(hwnd_before)
            return "Deezer lancé via protocole standard, mylane."
    except Exception as e:
        return f"Je n'ai pas réussi à ouvrir Deezer : {e}"

async def deezer_lecture_pause():
    """Bascule Play/Pause en arrière-plan sans vol de focus."""
    await deezer_ouvrir()
    try:
        ctrl = get_deezer_main_control()
        if ctrl:
            top = ctrl.GetTopLevelControl()
            hwnd = top.NativeWindowHandle if top else None
            if hwnd:
                import win32gui
                WM_APPCOMMAND = 0x0319
                APPCOMMAND_MEDIA_PLAY_PAUSE = 14
                lParam = APPCOMMAND_MEDIA_PLAY_PAUSE << 16
                win32gui.PostMessage(hwnd, WM_APPCOMMAND, hwnd, lParam)
                return "Lecture/Pause sur Deezer, mylane."
    except:
        pass
        
    try:
        res = await asyncio.to_thread(_uia_clic_bouton, ["Écouter", "Pause", "Mettre en pause"])
        if res:
            return "Lecture/Pause sur Deezer, mylane."
    except:
        pass
        
    if pyautogui:
        pyautogui.press('playpause')
    return "Lecture/Pause sur Deezer, mylane."

async def deezer_suivant():
    """Piste suivante en arrière-plan sans vol de focus."""
    await deezer_ouvrir()
    try:
        ctrl = get_deezer_main_control()
        if ctrl:
            top = ctrl.GetTopLevelControl()
            hwnd = top.NativeWindowHandle if top else None
            if hwnd:
                import win32gui
                WM_APPCOMMAND = 0x0319
                APPCOMMAND_MEDIA_NEXTTRACK = 11
                lParam = APPCOMMAND_MEDIA_NEXTTRACK << 16
                win32gui.PostMessage(hwnd, WM_APPCOMMAND, hwnd, lParam)
                return "Piste suivante sur Deezer, mylane."
    except:
        pass
        
    try:
        res = await asyncio.to_thread(_uia_clic_bouton, ["Suivant"])
        if res:
            return "Piste suivante sur Deezer, mylane."
    except:
        pass
        
    if pyautogui:
        pyautogui.press('nexttrack')
    return "Piste suivante sur Deezer, mylane."

async def deezer_precedent():
    """Piste précédente en arrière-plan sans vol de focus."""
    await deezer_ouvrir()
    try:
        ctrl = get_deezer_main_control()
        if ctrl:
            top = ctrl.GetTopLevelControl()
            hwnd = top.NativeWindowHandle if top else None
            if hwnd:
                import win32gui
                WM_APPCOMMAND = 0x0319
                APPCOMMAND_MEDIA_PREVTRACK = 12
                lParam = APPCOMMAND_MEDIA_PREVTRACK << 16
                win32gui.PostMessage(hwnd, WM_APPCOMMAND, hwnd, lParam)
                time.sleep(0.15)
                win32gui.PostMessage(hwnd, WM_APPCOMMAND, hwnd, lParam)
                return "Piste précédente sur Deezer, mylane."
    except:
        pass
        
    try:
        res = await asyncio.to_thread(_uia_clic_bouton, ["Précédent"])
        if res:
            return "Piste précédente sur Deezer, mylane."
    except:
        pass
        
    if pyautogui:
        pyautogui.press('prevtrack')
        time.sleep(0.15)
        pyautogui.press('prevtrack')
    return "Piste précédente sur Deezer, mylane."

async def deezer_stop():
    """Arrête la lecture (Pause)."""
    await deezer_ouvrir()
    try:
        def _stop_uia():
            deezer_ctrl = get_deezer_main_control()
            if deezer_ctrl:
                btn = find_player_button(deezer_ctrl, ["Écouter", "Pause", "Mettre en pause"])
                if btn:
                    if btn.Name in ["Pause", "Mettre en pause"]:
                        if _clic_control(btn):
                            return "Musique mise en pause sur Deezer, mylane."
                    elif btn.Name == "Écouter":
                        return "La musique est déjà en pause, mylane."
            return None
            
        res = await asyncio.to_thread(_stop_uia)
        if res:
            return res
    except:
        pass
        
    if pyautogui:
        pyautogui.press('playpause')
    return "Musique mise en pause sur Deezer, mylane."

async def deezer_volume(direction, paliers=4):
    """Monte ou baisse le volume général du PC."""
    if not pyautogui:
        return "Volume impossible, pyautogui non disponible."
    time.sleep(0.2)
    for _ in range(int(paliers)):
        if direction in ("monter", "up", "augmenter", "plus"):
            pyautogui.press('volumeup')
        else:
            pyautogui.press('volumedown')
        time.sleep(0.05)
    msg = "Volume monté" if direction in ("monter", "up", "augmenter", "plus") else "Volume baissé"
    return f"{msg}, mylane."

async def deezer_rechercher(recherche):
    """Recherche intelligente d'un morceau, album, artiste ou playlist, et lance la lecture."""
    recherche_lower = recherche.lower().strip()
    type_recherche = "track"
    query = recherche
    
    if "playlist" in recherche_lower:
        type_recherche = "playlist"
        query = recherche_lower.replace("la playlist", "").replace("ma playlist", "").replace("playlist", "").strip()
    elif "artiste" in recherche_lower or "groupe" in recherche_lower:
        type_recherche = "artist"
        query = recherche_lower.replace("l'artiste", "").replace("l'artiste", "").replace("artiste", "").replace("groupe", "").strip()
    elif "album" in recherche_lower:
        type_recherche = "album"
        query = recherche_lower.replace("l'album", "").replace("album", "").strip()
    
    if not query:
        query = recherche
        type_recherche = "track"
        
    print(f"[DEEZER] Recherche type={type_recherche} pour : '{query}'")
    
    try:
        # 1. Résolution via l'API Deezer
        if type_recherche == "playlist":
            url = f"https://api.deezer.com/search/playlist?q={requests.utils.quote(query)}"
        elif type_recherche == "artist":
            url = f"https://api.deezer.com/search/artist?q={requests.utils.quote(query)}"
        elif type_recherche == "album":
            url = f"https://api.deezer.com/search/album?q={requests.utils.quote(query)}"
        else:
            url = f"https://api.deezer.com/search?q={requests.utils.quote(query)}"
            
        resp = await asyncio.to_thread(requests.get, url, timeout=5)
        if resp.status_code != 200:
            return f"Je n'ai pas trouvé '{recherche}' sur Deezer, mylane."
            
        data = resp.json()
        results = data.get("data", [])
        if not results:
            return f"Je n'ai pas trouvé '{recherche}' sur Deezer, mylane."
            
        first_result = results[0]
        res_id = first_result.get("id")
        
        if type_recherche == "playlist":
            name = first_result.get("title")
            artist = ""
            msg = f"C'est parti mylane, je lance la playlist « {name} » sur Deezer."
        elif type_recherche == "artist":
            name = first_result.get("name")
            artist = name
            msg = f"C'est parti mylane, je lance les titres de l'artiste « {name} » sur Deezer."
        elif type_recherche == "album":
            name = first_result.get("title")
            artist = first_result.get("artist", {}).get("name", "")
            msg = f"C'est parti mylane, je lance l'album « {name} » de {artist} sur Deezer."
        else:
            name = first_result.get("title")
            artist = first_result.get("artist", {}).get("name", "")
            album_id = first_result.get("album", {}).get("id")
            msg = f"C'est parti mylane, je lance « {name} » de {artist} sur Deezer."
            
        # 2. Exécution avec contrôle d'accessibilité
        await deezer_ouvrir()
        
        with prevent_focus_theft():
            if type_recherche == "track":
                search_query = f"{name} {artist}"
                if _uia_taper_dans_recherche(search_query):
                    ok = _uia_clic_bouton_piste_album(name, artist, timeout=10)
                    if ok:
                        time.sleep(1.5)
                        return msg
                
                # Fallback album
                if album_id:
                    _ouvrir_uri_deezer(f"deezer://album/{album_id}")
                    ok = _uia_clic_bouton_piste_album(name, artist, timeout=20)
                    if ok:
                        time.sleep(0.5)
                        _ouvrir_uri_deezer(f"deezer://track/{res_id}")
                        return msg
                        
                # Fallback page track
                _ouvrir_uri_deezer(f"deezer://track/{res_id}")
                _uia_clic_bouton_page_dynamique(["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"], timeout=12, wait_for_title=name)
                return msg
                
            elif type_recherche == "playlist":
                # Vérifier la barre latérale en premier
                deezer_ctrl = get_deezer_main_control()
                elem_playlist = None
                if deezer_ctrl:
                    query_lower = query.lower().strip()
                    def _find_sidebar(c, depth=0):
                        nonlocal elem_playlist
                        if elem_playlist or depth > 8:
                            return
                        try:
                            rect = c.BoundingRectangle
                            if rect.left >= 350 or rect.top >= 940:
                                return
                            n = c.Name or ""
                            ctype = c.ControlTypeName or ""
                            if ctype in ("DataItemControl", "TextControl", "HyperlinkControl"):
                                if query_lower in n.lower() and rect.right < 350:
                                    elem_playlist = c
                                    return
                        except:
                            pass
                        for child in c.GetChildren():
                            _find_sidebar(child, depth + 1)
                            
                    _find_sidebar(deezer_ctrl)
                    
                if elem_playlist:
                    if _clic_control(elem_playlist):
                        _trier_si_playlist("playlist")
                        _uia_clic_bouton_page_dynamique(
                            ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"],
                            12, wait_for_title=query
                        )
                        time.sleep(1.5)
                        return f"C'est parti mylane, je lance votre playlist « {query} » sur Deezer."
                
                # Navigation directe via URI
                _ouvrir_uri_deezer(f"deezer://playlist/{res_id}")
                _trier_si_playlist(f"deezer://playlist/{res_id}")
                _uia_clic_bouton_page_dynamique(
                    ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"],
                    12, wait_for_title=name
                )
                return msg
                
            elif type_recherche == "artist":
                _ouvrir_uri_deezer(f"deezer://artist/{res_id}")
                _uia_clic_bouton_page_dynamique(
                    ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause", "Mix de l'artiste"],
                    12, wait_for_title=name
                )
                return msg
                
            elif type_recherche == "album":
                _ouvrir_uri_deezer(f"deezer://album/{res_id}")
                _uia_clic_bouton_page_dynamique(
                    ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"],
                    12, wait_for_title=name
                )
                return msg
                
        return msg
    except Exception as e:
        return f"Erreur lors de la recherche Deezer : {e}"

def _sort_playlist_dechronologique(deezer_ctrl):
    """Détecte le tri actuel de la playlist et clique sur 'AJOUTÉ' pour trier en déchronologique."""
    try:
        header_added = auto.HeaderControl(searchFromControl=deezer_ctrl, Name="AJOUTÉ")
        if not header_added.Exists(0.5):
            return False
            
        btn = header_added.ButtonControl(Name="AJOUTÉ")
        if not btn.Exists(0.5):
            return False
            
        tracks = []
        def find_tracks(ctrl):
            if ctrl.ControlTypeName == "CustomControl" and ctrl.Name and "Écouter" in ctrl.Name:
                tracks.append(ctrl.Name)
            for child in ctrl.GetChildren():
                find_tracks(child)
                if len(tracks) >= 15:
                    return
        find_tracks(deezer_ctrl)
        
        date_pattern = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')
        dates = []
        for t in tracks:
            found = date_pattern.findall(t)
            if found:
                try:
                    dt = datetime.strptime(found[0], "%d/%m/%Y")
                    dates.append(dt)
                except: pass
                
        first_dt = None
        current_sort = 'inconnu'
        for dt in dates:
            if first_dt is None:
                first_dt = dt
            elif dt != first_dt:
                if first_dt < dt:
                    current_sort = 'asc'
                else:
                    current_sort = 'desc'
                break
                
        if current_sort in ('asc', 'inconnu'):
            _clic_control(btn)
            time.sleep(1.0)
            return True
        return False
    except Exception as e:
        print(f"[DEEZER UIA] Erreur tri : {e}")
        return False

def _trier_si_playlist(uri):
    """Détecte le chargement de la playlist et applique le tri déchronologique."""
    if "playlist" not in uri.lower():
        return
    try:
        t0 = time.time()
        deezer_ctrl = None
        while time.time() - t0 < 8:
            try:
                deezer_ctrl = get_deezer_main_control()
                if deezer_ctrl:
                    header = auto.HeaderControl(searchFromControl=deezer_ctrl, Name="AJOUTÉ")
                    if header.Exists(0.1):
                        break
            except:
                pass
            time.sleep(0.5)
            
        if deezer_ctrl:
            _sort_playlist_dechronologique(deezer_ctrl)
    except Exception as e:
        print(f"[DEEZER] Échec tri auto : {e}")

async def deezer_lancer_playlist(url=None):
    """Lance la playlist configurée ou par défaut, puis démarre la lecture."""
    try:
        playlist_url = url or os.getenv("DEEZER_PLAYLIST_URL")
        
        if playlist_url:
            if "link.deezer.com" in playlist_url:
                try:
                    r = await asyncio.to_thread(requests.head, playlist_url, allow_redirects=True, timeout=5)
                    playlist_url = r.url
                except:
                    pass
            if "/playlist/" in playlist_url:
                p_id = playlist_url.split("/playlist/")[-1].split("?")[0]
                deezer_uri = f"deezer://playlist/{p_id}"
            else:
                deezer_uri = playlist_url
                
            _ouvrir_uri_deezer(deezer_uri)
            _trier_si_playlist(deezer_uri)
            
            # Clic lecture
            await asyncio.to_thread(
                _uia_clic_bouton_page_dynamique,
                ["Écouter", "Reprendre", "À l'écoute", "Pause", "Mettre en pause"],
                12
            )
            time.sleep(1.5)
            return True
        else:
            await deezer_ouvrir()
            with prevent_focus_theft():
                time.sleep(1)
                await asyncio.to_thread(_uia_clic_bouton, ["Écouter", "Pause", "Mettre en pause"])
                time.sleep(1.5)
                return True
    except Exception as e:
        print(f"[DEEZER] Erreur lancement playlist : {e}")
        return False

def deezer_obtenir_titre_encours():
    """Extrait le titre et l'artiste en cours depuis le DocumentControl UIA de Deezer."""
    if not auto:
        return None
    try:
        _initialize_com()
        deezer_ctrl = get_deezer_main_control()
        if not deezer_ctrl:
            return None
        title = deezer_ctrl.Name
        if title and " - Deezer" in title:
            song_info = title.replace(" - Deezer", "").strip()
            if " - " in song_info:
                parts = song_info.split(" - ", 1)
                return {
                    "title": parts[0].strip(),
                    "artist": parts[1].strip(),
                    "status": "Playing"
                }
            return {"title": song_info, "artist": "Deezer", "status": "Playing"}
    except:
        pass
    return None
