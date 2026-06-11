import sys, os
sys.path.insert(0, 'N:/JARVIS')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import time

steps = []

def mesure(label):
    steps.append((label, time.perf_counter()))

mesure("start")

import controller.homepod_controller as hc
mesure("homepod_controller")

import google.genai as genai
mesure("google.genai")

import speech_recognition as sr
mesure("speech_recognition")

import edge_tts
mesure("edge_tts")

import pygame
mesure("pygame")

from core.config import *
mesure("core.config")

import core.speech as speech
mesure("core.speech")

from module.alarm_manager import *
mesure("alarm_manager")

from module.memory_manager import _charger_historique_recent
mesure("memory_manager")

from controller.spotify_controller import *
mesure("spotify_controller")

from controller.deezer_controller import *
mesure("deezer_controller")

import plugins.tv_resolver
import plugins.local_resolver
import plugins.system_resolver
import plugins.extras
import plugins.globe_resolver
import plugins.memory_resolver
import plugins.list_manager
import plugins.time_resolver
import plugins.app_launcher_resolver
import plugins.dom_controller_resolver
import plugins.developer_resolver
import plugins.recipe_resolver
import plugins.os_autopilot_resolver
import plugins.local_mode_resolver
mesure("tous les plugins")

from module.google_services import *
mesure("google_services")

from module.vision_module import *
mesure("vision_module")

from module.sports_web import *
mesure("sports_web")

from module.vector_memory import ajouter_souvenir, rechercher_souvenirs
mesure("vector_memory (chromadb)")

from module.browser_service import AutonomousBrowser
mesure("browser_service")

from module.visual_web_agent import run_visual_agent, stop_visual_agent
mesure("visual_web_agent")

from module.image_generator import generer_image_ia
mesure("image_generator")

import pyaudio
mesure("pyaudio")

import websockets
mesure("websockets")

# Calcul des deltas
results = []
for i in range(1, len(steps)):
    dur = steps[i][1] - steps[i-1][1]
    results.append((steps[i][0], dur))

total = steps[-1][1] - steps[0][1]
print()
print("=== BENCHMARK IMPORTS ===")
for name, dur in sorted(results, key=lambda x: x[1], reverse=True):
    bar = "#" * int(dur * 10)
    print(f"  {dur:.3f}s  {bar}  {name}")
print(f"--- Total : {total:.3f}s ---")
