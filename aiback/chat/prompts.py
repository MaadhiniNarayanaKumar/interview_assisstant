from langchain.prompts import PromptTemplate

class Prompts_all:
    self_intro_prompt=''
    chat_prompt=''
    classification_prompt=''
    general_chat_prompt=''
    def __init__(self):
        self.self_intro_prompt="""
        You are a native english speaker\
        You are given paragraph or sentence or essay or sppech\
        Analyze the content given to you and provide me your insights about it\
        Only provide me insights in the below given json array format\        
        Format for insights:
        "
        {{
        "content_clarity":how was the content presented,
        "feedback":give me your feedback regarding all the things the user should improve with respect to the context in a detailed way,
        "user_character":[classify user's character and his habits in one word only],
        "user_skills":[classify user's skills which he mentioned in one word only],
        "Sentiment Analysis":analyse his sentiment or how emotional he is from the content
        }}
        "     
        Context is given below
        ===========
        {context}
        """
        self.chat_prompt='''
        You will be assissting the user with his interview preparation\
        he will ask you give some tips or suggestions for interview or practise questions also\
        Only if he says he is interested or ready to try speaking classify it as 'ready'\
        on other scenarios like tips or suggestions for interview or practise question classify it as 'not ready'\
        Analyze the content slowly and decide, do not make wron classifications\
        Only provide me insights in the below given json array format\        
        Format for insights:
        """
        {{"classification":classify as "ready" or "not ready" only in one word}}
        """
        Context is given below
        ===========
        {context}
        '''
        self.classification_prompt='''
        You will be given video or audio or message text form the user in the context, you are an excellent classifier assistant\
        if it is a video or audio classify as "self_intro" else if it is a message classify it as  "chat" \
        Only provide me insights in the below given json array format \       
        Begin example:

        Format for insights:
        """
        {{"classification":classify as "self_intro" or "chat" only in one word}}
        """
        Context is given below
        ===========
        {context}
        '''
        self.general_chat_prompt='''
        you are a chatbot\
        user is eager to learn how to crack interviews\
        have conversation with the user help him in learning to crack interviews from the context\
        do not disclose that you are a chatbot\
        Context is given below
        ===========
        {context}
        '''

    def get_template(self,text):
        if text=='self_intro':
            return PromptTemplate.from_template(self.self_intro_prompt);
        if text=='chat':
            return PromptTemplate.from_template(self.chat_prompt);
        if text=='classification':
                return PromptTemplate.from_template(self.classification_prompt);
        if text=='converse':
                    return PromptTemplate.from_template(self.general_chat_prompt);
             
        return ''
