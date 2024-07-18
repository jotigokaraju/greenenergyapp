import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline

model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Caching the model
@st.cache_resource
def gpt2_pipeline():
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

# Load the model
text_generator = gpt2_pipeline()

# Streamlit app
st.title("EcoEstimator")
st.header("Helping You Transition to Green Energy")
st.divider()
st.header("Questionnaire")
st.write("Please answer the following questions:")
with st.form("my_form"):
    st.write("Rapid Form")
    budget = st.slider("What is your budget?", 0, 500000, 50000)
    home = st.text_area("What type of house do you live in?", "Condo")
    location = st.text_area("Where do you live?", "Vancouver")
    electricity_bill = st.number_input("What is your monthly electricity bill?", value=0.0, format="%.2f")
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        prompt = (
            f"I have a budget of ${budget}. I live in a {home} in {location}. My monthly electricity bill is ${electricity_bill}. "
            "Based on this information, what type of green energy source would you recommend for me (e.g., solar panels, changing to LED lights, etc.)?"
        )

        input_ids = tokenizer.encode(prompt, return_tensors="pt", truncation=True)
        input_ids = input_ids[:, :100]  # Truncate input to avoid excessive length
        output = model.generate(input_ids, max_length=100, pad_token_id=tokenizer.eos_token_id)
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        
        st.header("Recommended Green Energy Source")
        st.write(generated_text)
