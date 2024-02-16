import io

from faster_whisper import WhisperModel

class Speech2TextModel:
    def __init__(self, model_size="large-v2", device="cuda", precision="float16") -> None:
        self._model = WhisperModel(model_size, device=device, compute_type=precision)

    def transcribe(self, wav_data: io.BytesIO):
        segments, _ = self._model.transcribe(wav_data, beam_size=5)

        text = ""

        for s in segments:
            text += s.text

        return text