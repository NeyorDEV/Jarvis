import re

# 1. Read frontendNouveau index.html
with open('frontendNouveau/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract settings modal
modal_match = re.search(r'<!-- ══ SETTINGS MODAL ══════════════════════════════════ -->.*?(?=</body>)', content, re.DOTALL)
settings_modal = modal_match.group(0) if modal_match else ''

# Extract buttons
btn_match1 = re.search(r'<button id="fullscreen-btn".*?</button>', content)
btn_match2 = re.search(r'<button id="settings-button".*?</button>', content)
fullscreen_btn = btn_match1.group(0) if btn_match1 else ''
settings_btn = btn_match2.group(0) if btn_match2 else ''

# 2. Inject into frontend/index.html
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    user_html = f.read()

# Add buttons
if '<button id="fullscreen-btn"' not in user_html:
    user_html = user_html.replace('<button id="mute-button"', fullscreen_btn + '\n    <button id="mute-button"')
if '<button id="settings-button"' not in user_html:
    user_html = user_html.replace('<div id="update-banner">', settings_btn + '\n    <div id="update-banner">')

# Add modal before </body>
if 'id="settings-modal"' not in user_html:
    user_html = user_html.replace('</body>', settings_modal + '\n</body>')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(user_html)


# 3. Extract CSS
with open('frontendNouveau/src/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

css_modal_match = re.search(r'/\* ── Settings Modal ── \*/.*', css_content, re.DOTALL)
if css_modal_match:
    settings_css = css_modal_match.group(0)
    with open('frontend/src/style.css', 'a', encoding='utf-8') as f:
        f.write('\n' + settings_css)

# 4. Extract JS
with open('frontendNouveau/src/main.ts', 'r', encoding='utf-8') as f:
    js_content = f.read()

js_modal_match = re.search(r'const settingsButtonEl = document.getElementById\("settings-button"\).*?settingsModalEl.classList.remove\("visible"\);\s*\}\);', js_content, re.DOTALL)
js_ws_match = re.search(r'if \(data.type === "settings_data" && data.data\) \{.*?return;\s*\}', js_content, re.DOTALL)

with open('frontend/src/main.ts', 'r', encoding='utf-8') as f:
    user_js = f.read()

if js_modal_match and 'settingsButtonEl' not in user_js:
    user_js += '\n\n// SETTINGS LOGIC INJECTED\n' + js_modal_match.group(0) + '\n'

if js_ws_match and 'settings_data' not in user_js:
    # Inject before the switch or if statements handling ws messages
    user_js = user_js.replace('if (data.action === "display_image"', js_ws_match.group(0) + '\n\n      if (data.action === "display_image"')

# fullscreen logic
fs_logic = '''
document.getElementById("fullscreen-btn")?.addEventListener("click", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "toggle_fullscreen" }));
    }
});
document.getElementById("mute-button")?.addEventListener("click", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "toggle_mic" }));
    }
    const btn = document.getElementById("mute-button");
    if(btn) {
        const isMuted = btn.getAttribute("aria-pressed") === "true";
        btn.setAttribute("aria-pressed", isMuted ? "false" : "true");
        btn.style.backgroundColor = isMuted ? "" : "rgba(255, 0, 0, 0.3)";
        btn.style.borderColor = isMuted ? "" : "red";
    }
});
'''
if 'toggle_fullscreen' not in user_js:
    user_js += '\n' + fs_logic

with open('frontend/src/main.ts', 'w', encoding='utf-8') as f:
    f.write(user_js)

print("INJECTION SUCCESSFUL")
