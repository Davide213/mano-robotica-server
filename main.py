import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Recupera la chiave API dalle variabili d'ambiente (la imposteremo su Render)
api_key = os.getenv("AQ.Ab8RN6KWHIMjNf8pvyxnYwzKqiFGwBSjE1Rlome5NSVvSC-F4Q")
if not api_key:
    # Se non trova la chiave locale (es. nei test sul PC), puoi metterne una di test qui
    # genai.configure(api_key="TUA_CHIAVE_DI_TEST")
    pass
else:
    genai.configure(api_key=api_key)

# Definiamo il formato dei dati che l'APK del telefono invierà al server
class RichiestaMano(BaseModel):
    domanda: str
    umidita: float

# Una pagina di prova per verificare se il server è online
@app.get("/")
def home():
    return {"status": "running", "message": "Server Ponte della Mano Robotica attivo!"}

# L'endpoint principale che verrà chiamato dal telefono Huawei
@app.post("/ask")
async def ask_ai(data: RichiestaMano):
    try:
        # Usiamo il modello 'gemini-3.5-flash', è velocissimo ed ottimale per questi scopi
        model = genai.GenerativeModel('gemini-3.5-flash')
        
        # Creiamo le istruzioni di sistema (System Prompt) per dare carattere all'IA
        system_instruction = (
            "Sei l'assistente vocale integrato in una MANO ROBOTICA. Ti chiami MANO. "
            "Rispondi sempre in italiano. Sii estremamente amichevole ma conciso (massimo 1 o 2 frasi), "
            "poiché la tua risposta verrà letta ad alta voce da un sintetizzatore vocale sul telefono. "
            f"L'umidità attuale della stanza rilevata dal mio sensore è del {data.umidita}%. "
            "Se l'utente ti fa domande sul clima domestico, sull'ambiente o su come stai, "
            "usa questo dato per rispondergli in modo simpatico."
        )
        
        # Costruiamo il prompt finale unendo il contesto e la domanda dell'utente
        prompt_completo = f"{system_instruction}\n\nUtente: {data.domanda}\nMANO:"
        
        # Generiamo la risposta
        response = model.generate_content(prompt_completo)
        
        return {"risposta": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore del server: {str(e)}")
