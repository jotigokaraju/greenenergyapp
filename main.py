import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.logo('EcoShifting.png')

# Constants for energy calculations
BASIC_CHARGE = 6.759  # Monthly basic charge in dollars
STEP1_RATE = 0.1097   # Step 1 energy charge in dollars per kWh
STEP2_RATE = 0.1408   # Step 2 energy charge in dollars per kWh
STEP1_LIMIT = 1376    # Step 1 limit in kWh
SOLAR_COST_PER_WATT = 2.30
HOURS_PER_DAY = 4
DAYS_PER_MONTH = 30
REBATE_AMOUNT = 8000  # One-time rebate amount

def calculate_energy_savings(current_bill, solar_panel_cost):
    net_charge = current_bill - BASIC_CHARGE
    if net_charge <= STEP1_LIMIT * STEP1_RATE:
        total_kwh_consumption = net_charge / STEP1_RATE
    else:
        q1_cost = STEP1_LIMIT * STEP1_RATE
        q2_cost = (net_charge - q1_cost) / STEP2_RATE
        total_kwh_consumption = STEP1_LIMIT + q2_cost

    system_size_watts = solar_panel_cost / SOLAR_COST_PER_WATT
    monthly_solar_kwh = (system_size_watts / 1000) * HOURS_PER_DAY * DAYS_PER_MONTH

    if monthly_solar_kwh <= STEP1_LIMIT:
        savings = monthly_solar_kwh * STEP1_RATE
    else:
        savings = (STEP1_LIMIT * STEP1_RATE) + ((monthly_solar_kwh - STEP1_LIMIT) * STEP2_RATE)

    return savings

def display_recommendations(budget, current_bill, savings):
    data = {
        "Category": ["Current Bill", "New Bill"],
        "Amount": [current_bill, current_bill - savings]
    }
    data_df = pd.DataFrame(data)
    st.header("Analytics")
    st.divider()
    st.subheader("Estimated Energy Bills")
    st.bar_chart(data_df.set_index('Category'))
    if (current_bill - savings) > 0:
        st.success(f"You will save ${savings:.2f} a month!")
    else:
        st.success("You are producing more energy than you need!")
        st.success(f"You can profit ${round(savings, 2)} a month by selling the extra energy back to the grid.")
    
    st.divider()

    # Calculate ROI over time
    initial_investment = budget
    monthly_savings = savings
    months_to_break_even = (initial_investment - REBATE_AMOUNT) / monthly_savings
    years_to_break_even = months_to_break_even / 12

    number = int(months_to_break_even * 1.5)  # Extend the timeline to 1.5 times the break-even point

    months = range(1, number + 1)
    cumulative_savings = [REBATE_AMOUNT + monthly_savings * month for month in months]
    initial_investment_line = [initial_investment] * len(months)  # Match the length of months

    roi_data = pd.DataFrame({
        "Month": months,
        "Cumulative Savings": cumulative_savings,
        "Initial Investment": initial_investment_line
    })

    st.subheader("ROI Over Time")
    st.success(f"You will receive ${REBATE_AMOUNT} in federal and provincial rebates")
    st.line_chart(roi_data.set_index("Month"))

    st.success(f"You will break even after approximately {years_to_break_even:.2f} years.")

    st.divider()
    st.subheader("Recommended Product:")
    st.components.v1.iframe("https://ca.renogy.com/200-watt-12-volt-monocrystalline-solar-panel/?Rng_ads=85ea6920805ad1cd&kw=&ad=&gr=&ca=20221950916&pl=ga&gclid=CjwKCAjw4_K0BhBsEiwAfVVZ_zLbfdDqE1-74o4DDqSZnEUVj5lYYGzTiATz_bpF8kYwf5P0Zlvb7xoCg38QAvD_BwE&r_u_id=9222541894&gad_source=1", height=400, scrolling=True)


def show_survey_page():
    st.title(":green[EcoShift Survey]")
    st.divider()
    st.header("Helping You Transition to Green Energy")
    st.write("Please fill out the following form to get personalized recommendations:")

    with st.form("survey_form"):
        st.write("Rapid Form")
        budget = st.slider("What is your budget?", 0, 500000, 50000)
        home = st.text_area("What type of house do you live in?", "Condo")
        location = st.text_area("Where do you live?", "Vancouver")
        electricity_bill = st.number_input("What is your monthly electricity bill?", value=0.0, format="%.2f")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            st.session_state.budget = budget
            st.session_state.electricity_bill = electricity_bill
            st.session_state.submitted = True
            st.session_state.show_chart = False

            st.write(f"Budget: {budget}")
            st.write(f"Home: {home}")
            st.write(f"Location: {location}")
            st.write(f"Electricity Bill: {electricity_bill}")

            budget_purchase = budget * 0.4
            budget_install = budget * 0.2
            budget_batteries = budget * 0.15
            budget_inverter = budget * 0.05
            budget_additional = budget * 0.1

            st.success(f"Based on your specified information, EcoEstimator AI recommends that you install ${budget_purchase} worth of solar panels, spend ${budget_install} on installation, spend ${budget_batteries} on supplementary battery costs, ${budget_inverter} on an inverter, and ${budget_additional} on other hardware.") 
            st.write("For more information, purchase the premium version")

    if st.session_state.get('submitted', False):
        if st.button("Premium Version"):
            budget_purchase = st.session_state.budget * 0.4
            savings = calculate_energy_savings(st.session_state.electricity_bill, budget_purchase)
            display_recommendations(st.session_state.budget, st.session_state.electricity_bill, savings)
            st.session_state.show_chart = True

def search_bing(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = f"{query} energy-efficient sustainable"
    url = f"https://www.bing.com/search?q={query}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for item in soup.find_all('li', class_='b_algo'):
        link = item.find('a')['href']
        links.append(link)
    
    return links

def show_search_page():
    st.title(":green[EcoShift Product Search]")
    st.divider()
    st.header("Search for Products")
    st.write("Use the search bar below to find products and solutions.")

    search_query = st.text_input("Search", "")
    
    if search_query:
        results = search_bing(search_query)
        
        if results:
            st.subheader("EcoShift recommends the following:")

            # Sponsored section with customer testimonials
            st.markdown("### ⭐ Sponsored")
            st.markdown(f"**⭐ Sponsored Link 1:** [Click here]({results[0]})", unsafe_allow_html=True)
            st.markdown(f"**⭐ Sponsored Link 2:** [Click here]({results[1]})", unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <h4>What Our Customers Are Saying</h4>
                <blockquote>
                    <p>"EcoShift has completely transformed the way I view energy efficiency. The recommendations were spot-on and helped me save a lot!"</p>
                    <footer>- Jane D.</footer>
                </blockquote>
                <blockquote>
                    <p>"I was impressed with the user-friendly interface and the personalized suggestions. It made the transition to green energy so much easier."</p>
                    <footer>- Mark T.</footer>
                </blockquote>
                <blockquote>
                    <p>"The search results and sponsored links helped me find the perfect products for my needs. Highly recommend EcoShift!"</p>
                    <footer>- Emma R.</footer>
                </blockquote>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # Button to reveal additional links
            if st.button("Show More Results"):
                st.subheader("Additional Results")
                for i in range(2, len(results)):
                    st.markdown(f"**Link {i+1}:** [Click here]({results[i]})", unsafe_allow_html=True)
        else:
            st.write("No results found. Please try a different query.")
            
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Home", "Survey", "Search"])
    
    if page == "Home":
        st.title(":green[EcoShift]")
        st.divider()
        st.header("Welcome to EcoShift")
        st.subheader("Your Partner in Green Energy")
        st.write("""
            EcoShift is designed to help you transition to green energy solutions with ease. 

            **What We Offer:**
            - **Survey:** Get tailored recommendations for your green energy investments.
            - **Search:** Find products and solutions to fit your needs.

            Use the sidebar to navigate between pages.
        """)
    elif page == "Survey":
        show_survey_page()
    elif page == "Search":
        show_search_page()

if __name__ == "__main__":
    main()

