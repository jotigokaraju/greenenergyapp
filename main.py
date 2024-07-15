import streamlit as st
from transformers import pipeline

# Caching the model
@st.cache_resource
def gpt2():
    
    return pipeline("text-generation", model="openai-community/gpt2")

# Load the model


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
        model = gpt2()
        # Prepare the input for the model
        user_input = (
            f"I have a budget of ${budget}. I live in a {home} in {location}. My monthly electricity bill is ${electricity_bill}. "
            "Based on this information, what type of green energy source would you recommend for me (e.g., solar panels, changing to LED lights, etc.)?"
        )

        # Get the response from the GPT-2 model
        response = model(user_input, max_length=50, num_return_sequences=1)

        # Display the response
        st.header("Recommended Green Energy Source")
        st.write(response[0]['generated_text'])
