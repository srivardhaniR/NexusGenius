from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
#we are using hugging face transformers which is a library of pretrained language models
#we use the shortcut tools like
#Autotokenizer : converts raw text in to tokens that modal can understand
#AutoModelForSeq2SeqLM : this helps us load pretrained model (flan T5) that works for sequence to sequence tasks

import streamlit as st

# Loading the flan-t5-small only once
@st.cache_resource(show_spinner="Loading Smart Chatbot..")
#this is a streamlit decorator, caches the result of the below function , so it doesnot reload the model every time
#very important when we are uisng huggingface models as they take lot of tiem to load

def load_flan_model():
    
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    #this line load the tokenizer for the flan-t5-small model
    #this tokenizer converts the question or a text to numbers that model understands
    
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    #we are loading FLAN T5 model from google, its a  sequence2sequence language model
    
    generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
    #tect2text-generation meaning take text as inpiut and generate a responze texxt
    #creating a pipeline to combine the model (FLAN T5), the tokenizer into single easy to use tool
    
    return generator


#Generate the answer using top retrieved chunks + user query
def generate_answer(chunks, query, generator):
    #here the fucntion takes 3 inputs :a small text chunk from (uploaded file -uploaded by trainer), 
    # the quesry is the questions we asked or entered, 
    # generator  the FLAN T5 model pipeline created above
    
    context = "\n".join(chunks)
    #we combine all the chunks in to one long block of text and store in "context" string
    
    prompt = f"Answer the question based on this context:\n\n{context}\n\nQuestion: {query}\n\nAnswer:"
    #it is our custom prompt where it looks like, answer the query based on "context" ,question: and answer:
    
    result = generator(prompt, max_length=300, temperature=0.7)
    #we send the prompt to the model using pipeline
    #max_length is limit of answer the generated (300 is the number of max tokens in the generated answer)
    #temperature is the strictness of the answer , higher the value more strict and ore creative answer will be, less the valeu less strict and less relevent the answer will be
    
    return result[0]['generated_text']
#we will extract generated answer and return it to the user

# Main answer function for chatbot tab
def answer_question(query, notes_folder="uploaded_notes/", generator=None):
    from utils import load_notes_from_folder, split_text, embed_chunks, create_faiss_index, get_top_chunks

    all_texts = load_notes_from_folder(notes_folder)
    all_chunks = []
    for text in all_texts:
        all_chunks.extend(split_text(text))

    embeddings, embed_model = embed_chunks(all_chunks)
    index = create_faiss_index(embeddings)
    top_chunks = get_top_chunks(query, embed_model, index, all_chunks)

    if generator is None:
        generator = load_flan_model()

    answer = generate_answer(top_chunks, query, generator)
    return answer
