import assemblyai as aai

class transcribe_the_speech:
    def speech_to_text(self,audio_url:any):
        aai.settings.api_key = api
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_url)
        return transcript.text