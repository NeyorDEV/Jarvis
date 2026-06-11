import psutil

for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['name'] and 'deezer' in proc.info['name'].lower():
            print(f"PID: {proc.info['pid']}, Name: {proc.info['name']}, Cmdline: {proc.info['cmdline']}")
    except Exception as e:
        pass
