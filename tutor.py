"""Sarvam Language Tutor — voice-based Indian language learning."""
import os, io, tempfile
import numpy as np, sounddevice as sd, soundfile as sf
from dotenv import load_dotenv
from sarvamai import SarvamAI
from rich.console import Console

load_dotenv()
console=Console()
client=SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])
SR=16000

LESSONS={
    "ta-IN":[{"en":"Good morning","native":"காலை வணக்கம்"},{"en":"Thank you","native":"நன்றி"},{"en":"How are you?","native":"நீங்கள் எப்படி இருக்கிறீர்கள்?"},{"en":"My name is","native":"என் பெயர்"},{"en":"Where is the bus stop?","native":"பஸ் நிறுத்தம் எங்கே?"}],
    "hi-IN":[{"en":"Good morning","native":"सुप्रभात"},{"en":"Thank you","native":"धन्यवाद"},{"en":"How are you?","native":"आप कैसे हैं?"},{"en":"My name is","native":"मेरा नाम है"},{"en":"Where is the bus stop?","native":"बस स्टॉप कहाँ है?"}],
}

def transliterate(text, lang):
    return client.text.transliterate(input=text, source_language_code=lang, target_language_code="en-IN").transliterated_text

def speak(text, lang):
    r=client.text_to_speech.convert(text=text,target_language_code=lang,speaker="anushka")
    with tempfile.NamedTemporaryFile(suffix=".wav",delete=False) as f: f.write(r.audios[0]); tmp=f.name
    d,sr=sf.read(tmp); sd.play(d,sr); sd.wait()

def record(sec=4):
    console.print("[red]● Repeat...[/red]"); a=sd.rec(int(sec*SR),samplerate=SR,channels=1,dtype="float32"); sd.wait(); return a.flatten()

def score_attempt(audio, expected, lang):
    buf=io.BytesIO(); sf.write(buf,audio,SR,format="WAV"); buf.seek(0)
    attempt=client.speech_to_text.transcribe(file=buf,model="saaras:v3",language_code=lang).transcript
    s=len(set(expected.split())&set(attempt.split()))/max(len(set(expected.split())),1)*100
    return attempt, s

def run(lang="ta-IN"):
    lessons=LESSONS.get(lang,LESSONS["hi-IN"]); lang_name={"ta-IN":"Tamil","hi-IN":"Hindi"}.get(lang,lang)
    console.print(f"\n[bold]🎓 Learning {lang_name}[/bold]\n"); total=0
    for i,l in enumerate(lessons):
        console.print(f"\n[cyan]Lesson {i+1}:[/cyan] {l['en']} → [green]{l['native']}[/green]")
        console.print(f"  Roman: [yellow]{transliterate(l['native'],lang)}[/yellow]")
        input("  Enter to hear..."); speak(l['native'],lang)
        input("  Enter to record..."); audio=record()
        attempt,s=score_attempt(audio,l['native'],lang)
        console.print(f"  You: {attempt} | Score: [{'green' if s>60 else 'red'}]{s:.0f}%[/]"); total+=s
    console.print(f"\n[bold]Final: {total/len(lessons):.0f}%[/bold]")

if __name__=="__main__":
    import sys; run(sys.argv[1] if len(sys.argv)>1 else "ta-IN")
