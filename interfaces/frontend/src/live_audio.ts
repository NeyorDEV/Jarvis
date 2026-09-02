/**
 * LiveAudioEngine : Gestionnaire WebAudio HTML5 bi-directionnel full-duplex pour JARVIS.
 * Capture micro 16kHz PCM (in) et lecture 24kHz PCM (out) avec visualiseur 3D Orbe.
 */
export class LiveAudioEngine {
  private audioCtx: AudioContext | null = null;
  private micStream: MediaStream | null = null;
  private scriptNode: ScriptProcessorNode | null = null;
  private isLiveActive = false;
  private wsSendCallback: ((data: any) => void) | null = null;
  private audioQueue: AudioBuffer[] = [];
  private isPlaying = false;
  private nextStartTime = 0;
  
  // Callback d'animation pour l'orbe 3D
  public onVolumeUpdate: ((volume: number) => void) | null = null;
  constructor(wsSendCallback: (data: any) => void) {
    this.wsSendCallback = wsSendCallback;
  }
  /**
   * Démarrage de la capture micro et de la session Live Audio.
   */
  async startLiveSession(): Promise<boolean> {
    try {
      this.audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      this.micStream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, sampleRate: 16000 } });
      const source = this.audioCtx.createMediaStreamSource(this.micStream);
      this.scriptNode = this.audioCtx.createScriptProcessor(2048, 1, 1);
      source.connect(this.scriptNode);
      this.scriptNode.connect(this.audioCtx.destination);
      this.scriptNode.onaudioprocess = (event) => {
        if (!this.isLiveActive) return;
        const inputBuffer = event.inputBuffer.getChannelData(0);
        
        // Calcul du volume pour alimenter l'orbe 3D
        let sum = 0;
        for (let i = 0; i < inputBuffer.length; i++) {
                      sum += inputBuffer[i] * inputBuffer[i];
        }
        const rms = Math.sqrt(sum / inputBuffer.length);
        if (this.onVolumeUpdate) {
          this.onVolumeUpdate(Math.min(1.0, rms * 4.0));
        }
        // Conversion Float32 vers Int16 PCM (16kHz)
        const pcmInt16 = new Int16Array(inputBuffer.length);
        for (let i = 0; i < inputBuffer.length; i++) {
          const s = Math.max(-1, Math.min(1, inputBuffer[i]));
          pcmInt16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        // Envoi du bloc PCM encodé en base64 au serveur WebSocket
        const base64PCM = this.arrayBufferToBase64(pcmInt16.buffer);
        if (this.wsSendCallback) {
          this.wsSendCallback({
            type: "audio_chunk",
            data: base64PCM
          });
        }
      };
      this.isLiveActive = true;
      console.log("[LIVE AUDIO] Capture micro 16kHz active !");
      return true;
    } catch (err) {
      console.error("[LIVE AUDIO ERROR] Échec d'accès au micro :", err);
      return false;
    }
  }
  /**
   * Reçoit un paquet audio PCM 24kHz du serveur Gemini et le joue immédiatement.
   */
  async playIncomingPCM(pcmBase64: string, sampleRate = 24000) {
    if (!this.audioCtx) {
      this.audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
    }
        try {
      const rawBytes = this.base64ToArrayBuffer(pcmBase64);
      const int16Array = new Int16Array(rawBytes);
      const float32Array = new Float32Array(int16Array.length);
      for (let i = 0; i < int16Array.length; i++) {
        float32Array[i] = int16Array[i] / 32768.0;
      }
      const audioBuffer = this.audioCtx.createBuffer(1, float32Array.length, sampleRate);
      audioBuffer.getChannelData(0).set(float32Array);
      const bufferSource = this.audioCtx.createBufferSource();
      bufferSource.buffer = audioBuffer;
      bufferSource.connect(this.audioCtx.destination);
      const currentTime = this.audioCtx.currentTime;
      if (this.nextStartTime < currentTime) {
        this.nextStartTime = currentTime;
      }
      bufferSource.start(this.nextStartTime);
      this.nextStartTime += audioBuffer.duration;
      // Faire vibrer l'orbe pendant la parole de JARVIS
      if (this.onVolumeUpdate) {
        this.onVolumeUpdate(0.6 + Math.random() * 0.4);
      }
    } catch (e) {
      console.error("[LIVE AUDIO PLAYBACK ERROR]", e);
    }
  }
  /**
   * Arrêt complet du flux et fermeture du micro.
   */
  stopLiveSession() {
    this.isLiveActive = false;
    if (this.scriptNode) {
      this.scriptNode.disconnect();
      this.scriptNode = null;
    }
        if (this.micStream) {
      this.micStream.getTracks().forEach(t => t.stop());
      this.micStream = null;
    }
    if (this.audioCtx) {
      this.audioCtx.close();
      this.audioCtx = null;
    }
    console.log("[LIVE AUDIO] Session Live arrêtée.");
  }
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }
  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }
}