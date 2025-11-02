"""
Session Manager FastAPI Server
VCA 1.0 - Phase 1
"""

import asyncio
import uuid
import io
import wave
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

# Import modules
from config.settings import get_settings
from utils.logger import setup_logger
from stt.providers.openai_whisper import OpenAIWhisperProvider
from tts.providers.openai_tts import OpenAITTSProvider
from session.vad import VoiceActivityDetector
from session.stop_phrases import StopPhraseDetector
from session.manager import SessionManager, SessionState

# Initialize FastAPI app
app = FastAPI(title="VCA Session Manager", version="1.0.0")

# Global instances
settings = None
logger = None
stt_provider = None
tts_provider = None
vad = None
stop_phrase_detector = None
session_manager = None


@app.on_event("startup")
async def startup():
    """Initialize components on startup"""
    global settings, logger, stt_provider, tts_provider, vad, stop_phrase_detector, session_manager

    # Load settings
    settings = get_settings()

    # Setup logger
    logger = setup_logger(
        name="session_manager",
        level=settings.get('logging.level', 'INFO'),
        log_file=settings.get('logging.file'),
        console=settings.get('logging.console', True)
    )

    logger.info("Starting VCA Session Manager...")

    # Initialize STT provider
    stt_config = {
        'api_key': settings.get('openai.api_key'),
        'model': settings.get('openai.stt.model', 'whisper-1'),
        'language': settings.get('openai.stt.language', 'en'),
        'temperature': settings.get('openai.stt.temperature', 0.0)
    }
    stt_provider = OpenAIWhisperProvider(stt_config)
    logger.info(f"Initialized STT: {stt_provider}")

    # Initialize TTS provider
    tts_config = {
        'api_key': settings.get('openai.api_key'),
        'model': settings.get('openai.tts.model', 'tts-1'),
        'voice': settings.get('openai.tts.voice', 'nova'),
        'speed': settings.get('openai.tts.speed', 1.0)
    }
    tts_provider = OpenAITTSProvider(tts_config)
    logger.info(f"Initialized TTS: {tts_provider}")

    # Initialize VAD
    vad_config = settings.get('session.vad', {})
    vad = VoiceActivityDetector(
        sample_rate=vad_config.get('sample_rate', 16000),
        frame_duration_ms=vad_config.get('frame_duration', 30),
        aggressiveness=vad_config.get('aggressiveness', 3),
        silence_threshold_sec=vad_config.get('silence_timeout', 2.0)
    )
    logger.info(f"Initialized VAD: {vad}")

    # Initialize stop phrase detector
    stop_phrases = settings.get('session.stop_phrases', ["that's all", "goodbye"])
    stop_phrase_detector = StopPhraseDetector(stop_phrases)
    logger.info(f"Initialized stop phrase detector: {stop_phrase_detector}")

    # Initialize session manager
    max_duration = settings.get('session.max_session_duration', 300)
    session_manager = SessionManager(max_session_duration=max_duration)
    logger.info(f"Initialized session manager (max_duration={max_duration}s)")

    logger.info("Session Manager ready!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "version": "1.0.0",
        "active_sessions": session_manager.get_active_sessions_count() if session_manager else 0
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "stt": stt_provider is not None,
            "tts": tts_provider is not None,
            "vad": vad is not None,
            "session_manager": session_manager is not None
        },
        "active_sessions": session_manager.get_active_sessions_count() if session_manager else 0
    }


@app.websocket("/audio-stream")
async def audio_stream(websocket: WebSocket):
    """
    WebSocket endpoint for audio streaming.

    Protocol:
        Client → Server (JSON): {"type": "session_start", "device_id": "..."}
        Client → Server (Binary): Audio chunks (PCM16, 16kHz, mono, 30ms frames)
        Server → Client (JSON): {"type": "transcript", "text": "..."}
        Server → Client (JSON): {"type": "response_text", "text": "..."}
        Server → Client (Binary): Audio response (MP3)
        Client → Server (JSON): {"type": "session_end", "reason": "..."}
    """
    await websocket.accept()
    logger.info(f"WebSocket connection accepted from {websocket.client}")

    session_id = str(uuid.uuid4())
    session = None

    try:
        # Wait for session start message
        data = await websocket.receive()
        logger.debug(f"Received data: {data}")

        if "text" in data:
            import json
            logger.debug(f"Received text: {data['text']}")
            message = json.loads(data["text"])
            logger.debug(f"Parsed message: {message}")

            if message.get("type") == "session_start":
                device_id = message.get("device_id", "unknown")
                session = session_manager.create_session(session_id, device_id)
                session.state = SessionState.LISTENING

                logger.info(f"Session started: {session}")

                # Send acknowledgment
                await websocket.send_json({
                    "type": "session_started",
                    "session_id": session_id
                })
        else:
            logger.warning(f"Received non-text data: {data}")

        if not session:
            logger.error("No session_start message received")
            await websocket.close(code=1003, reason="session_start required")
            return

        # Audio processing loop
        vad.reset()

        while True:
            data = await websocket.receive()

            # Handle binary audio data
            if "bytes" in data:
                audio_chunk = data["bytes"]
                session.append_audio(audio_chunk)

                # Process with VAD (30ms frames = 960 bytes @ 16kHz PCM16)
                if len(audio_chunk) == vad.frame_size:
                    is_speech, is_end_of_speech = vad.process_frame(audio_chunk)

                    if is_end_of_speech:
                        # End of speech detected - process accumulated audio
                        logger.info(f"End of speech detected (session {session_id})")

                        session.state = SessionState.PROCESSING
                        await websocket.send_json({
                            "type": "status",
                            "state": "processing"
                        })

                        # Convert audio buffer to WAV format for Whisper API
                        wav_buffer = create_wav(session.audio_buffer, sample_rate=16000)

                        # Transcribe with STT
                        try:
                            result = await stt_provider.transcribe(wav_buffer)
                            transcript = result.text

                            logger.info(f"Transcript: '{transcript}'")
                            session.transcript = transcript

                            # Send transcript to client
                            await websocket.send_json({
                                "type": "transcript",
                                "text": transcript
                            })

                            # Check for stop phrase
                            if stop_phrase_detector.is_stop_phrase(transcript):
                                matched = stop_phrase_detector.get_matched_phrase(transcript)
                                logger.info(f"Stop phrase detected: '{matched}'")

                                await websocket.send_json({
                                    "type": "session_ending",
                                    "reason": "stop_phrase",
                                    "matched_phrase": matched
                                })

                                break

                            # Generate response (Phase 2 will add LLM here)
                            # For now, echo back a simple response
                            response_text = f"You said: {transcript}"
                            session.response = response_text

                            await websocket.send_json({
                                "type": "response_text",
                                "text": response_text
                            })

                            # Synthesize TTS
                            session.state = SessionState.RESPONDING
                            tts_result = await tts_provider.synthesize(response_text)

                            logger.info(f"TTS generated ({len(tts_result.audio_bytes)} bytes)")

                            # Send audio response
                            await websocket.send_bytes(tts_result.audio_bytes)

                            # Back to listening state
                            session.state = SessionState.LISTENING
                            session.clear_audio_buffer()
                            vad.reset()

                            await websocket.send_json({
                                "type": "status",
                                "state": "listening"
                            })

                        except Exception as e:
                            logger.error(f"Error processing audio: {e}", exc_info=True)
                            await websocket.send_json({
                                "type": "error",
                                "message": str(e)
                            })

            # Handle text messages (session control)
            elif "text" in data:
                import json
                message = json.loads(data["text"])

                if message.get("type") == "session_end":
                    reason = message.get("reason", "client_request")
                    logger.info(f"Session ending (reason: {reason})")
                    break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected (session {session_id})")

    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}", exc_info=True)

    finally:
        if session:
            session_manager.end_session(session_id)
            logger.info(f"Session ended: {session_id}")

        try:
            await websocket.close()
        except:
            pass


def create_wav(pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
    """
    Create WAV file bytes from raw PCM data.

    Args:
        pcm_data: Raw PCM16 audio bytes
        sample_rate: Sample rate (Hz)
        channels: Number of channels (1=mono, 2=stereo)
        sample_width: Bytes per sample (2 for PCM16)

    Returns:
        WAV file bytes
    """
    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)

    return wav_buffer.getvalue()


if __name__ == "__main__":
    import uvicorn

    # Get server config
    settings = get_settings()
    host = settings.get('server.host', '0.0.0.0')
    port = settings.get('server.port', 5000)
    debug = settings.get('server.debug', True)

    print(f"Starting Session Manager on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
