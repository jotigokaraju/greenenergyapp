import streamlit as st
from transformers import pipeline
from transformers import GPT2LMHeadModel, GPT2Tokenizer

model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Caching the model
@st.cache_resource
def gpt2():

    return pipeline("text-generation", model="openai-community/gpt2")

# Load the model
model = gpt2()


# Streamlit app
st.title("EcoEstimator")
st.header("Helping You Transition to Green Energy")
st.divider()
st.header("Questionnaire")
st.write("Please answer the following questions:")
with st.form("my_form"):
    st.write("Rapid Form")
    budget = st.slider("What is your budget?", 0, 500000, 50000)
    home = st.text_input("What type of house do you live in?", "Condo")
    location = st.text_input("Where do you live?", "Vancouver")
    electricity_bill = st.number_input("What is your monthly electricity bill?")
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        if st.button("Generate"):
            prompt = (
                f"I have a budget of ${budget}. I live in a {home} in {location}. My monthly electricity bill is ${electricity_bill}. "
                "Based on this information, what type of green energy source would you recommend for me (e.g., solar panels, changing to LED lights, etc.)?"
            )
            
            input_ids = tokenizer.encode(prompt, return_tensors="pt")
            output = model.generate(input_ids, max_length=100)
            generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
            
            # Prepare the input for the model
            
            st.header("Recommended Green Energy Source")
            st.write(generated_text)
