import subprocess

@kai_tool(name="physical_alert", description="Triggers device vibration and text-to-speech for critical system events.")
def physical_alert(title: str = "Alert", message: str = "System event triggered.", level: str = "info") -> dict:
    try:
        # Standard haptic feedback (500ms vibration)
        subprocess.run(["termux-vibrate", "-d", "500"], capture_output=True)
        
        # Audio feedback for high-priority alerts
        if level.lower() in ["warning", "error"] or "ERROR" in title.upper() or "WARNING" in title.upper():
            speech_text = f"Attention Operator. {title}: {message}"
            subprocess.run(["termux-tts-speak", speech_text], capture_output=True)
            
        return {"status": "success", "message": f"Physical alert dispatched for: {title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
