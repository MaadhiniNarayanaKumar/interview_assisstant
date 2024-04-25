# from openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
import langchain_openai 
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from audio import audio
from chat.prompts import Prompts_all

aud=audio.transcribe_the_speech()
prompt=Prompts_all()
class communicate:
    llm=''
    def __init__(self) -> None:
        self.llm=langchain_openai.OpenAI(api_key)
    def self_intro(self,query):
        # res="Hello World"
        stt=aud.speech_to_text("C:Users/maanu/Downloads/self_intro2.mp3")
        template=prompt.get_template('self_intro')
        chain= template | self.llm | StrOutputParser()
        res=chain.invoke({'context':stt})
        return res
    
    def chat(self,query):
        # res="Hello World"
        # stt=aud.speech_to_text("D:/mj/content/harvard.wav")
        template=prompt.get_template('chat')
        chain= template | self.llm | StrOutputParser()
        res=chain.invoke({'context':query})
        print(res)
        return res
    def classify(self,query):
        template=prompt.get_template('classification')
        chain= template | self.llm | StrOutputParser()
        res=chain.invoke({'context':query})
        print(res)
        return res
    def converse(self,query):
        # res="Hello World"
        # stt=aud.speech_to_text("D:/mj/content/harvard.wav")
        template=prompt.get_template('converse')
        chain= template | self.llm | StrOutputParser()
        res=chain.invoke({'context':query})
        print(res)
        return res