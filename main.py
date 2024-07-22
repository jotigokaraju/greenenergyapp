import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

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

    return savings, total_kwh_consumption



def display_recommendations(budget, current_bill, savings, kwh):
    # Bar chart for Estimated Energy Bills
    data = {
        "Category": ["Current Bill", "New Bill"],
        "Amount": [current_bill, current_bill - savings]
    }
    data_df = pd.DataFrame(data)

    st.header("Analytics")
    st.divider()
    st.subheader("Estimated Energy Bills")

    fig, ax = plt.subplots()
    data_df.set_index('Category').plot(kind='bar', ax=ax, color=['#4CAF50', '#FFC107'], legend=False)
    
    # Set axis labels and title
    ax.set_xlabel('Category', fontsize=12)
    ax.set_ylabel('Amount (CAD)', fontsize=12)
    ax.set_title('Estimated Energy Bills', fontsize=14)
    
    # Add value labels on top of bars
    for p in ax.patches:
        ax.annotate(f'${p.get_height():,.2f}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 5), textcoords='offset points')
    
    # Customize gridlines and spines
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(0.5)
    
    st.pyplot(fig)
    
    if (current_bill - savings) > 0:
        st.success(f"You will save ${savings:.2f} a month!")
    else:
        st.success("You are producing more energy than you need!")
        st.success(f"You can profit ${round(savings, 2)} a month by selling the extra energy back to the grid.")
    
    st.divider()

    # ROI Over Time Line Chart
    initial_investment = budget
    monthly_savings = savings
    months_to_break_even = (initial_investment - REBATE_AMOUNT) / monthly_savings
    years_to_break_even = months_to_break_even / 12

    number = int(months_to_break_even * 1.5)  # Extend the timeline to 1.5 times the break-even point

    months = range(1, number + 1)
    cumulative_savings = [REBATE_AMOUNT + monthly_savings * month for month in months]
    initial_investment_line = [initial_investment] * len(months)

    roi_data = pd.DataFrame({
        "Month": months,
        "Cumulative Savings": cumulative_savings,
        "Initial Investment": initial_investment_line
    })

    st.subheader("Return on Investment")
    st.success(f"You will receive ${REBATE_AMOUNT} in federal and provincial rebates")
    
    fig, ax = plt.subplots()
    roi_data.set_index("Month").plot(ax=ax)
    
    # Set axis labels and title
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Amount (CAD)', fontsize=12)
    ax.set_title('Return on Investment Over Time', fontsize=14)
    
    # Customize gridlines and spines
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(0.5)
    
    st.pyplot(fig)

    st.success(f"You will break even after approximately {years_to_break_even:.2f} years.")

    st.divider()

    # Carbon Emission Reduction Bar Chart
    st.subheader("Carbon Emission Reduction")

    emissions1 = kwh * 7.6
    emissions2 = savings / 0.1076 * 7.6
    em = emissions1 - emissions2
    data = {
        "Emissions Per Month": ["Before", "After"],
        "Grams of CO2": [emissions1, em]
    }
    data_eco = pd.DataFrame(data)

    fig, ax = plt.subplots()
    data_eco.set_index('Emissions Per Month').plot(kind='bar', ax=ax, color=['#0047AB', '#03A9F4'], legend=False)
    
    # Set axis labels and title
    ax.set_xlabel('Emissions Per Month', fontsize=12)
    ax.set_ylabel('Grams of CO2', fontsize=12)
    ax.set_title('Monthly Carbon Emissions Reduction', fontsize=14)
    
    # Add value labels on top of bars
    for p in ax.patches:
        ax.annotate(f'{p.get_height():,.0f}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 5), textcoords='offset points')
    
    # Customize gridlines and spines
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')
        spine.set_linewidth(0.5)
    
    st.pyplot(fig)

    emer = emissions1 - em
    emer = round(emer)
    st.success(f"You will save {emer} grams of CO2 per month")

    st.divider()
    st.subheader("Recommended Solar Product:")
    st.components.v1.iframe("https://ca.renogy.com/200-watt-12-volt-monocrystalline-solar-panel/?Rng_ads=85ea6920805ad1cd&kw=&ad=&gr=&ca=20221950916&pl=ga&gclid=CjwKCAjw4_K0BhBsEiwAfVVZ_zLbfdDqE1-74o4DDqSZnEUVj5lYYGzTiATz_bpF8kYwf5P0Zlvb7xoCg38QAvD_BwE&r_u_id=9222541894&gad_source=1", height=400, scrolling=True)

    st.divider()
    st.subheader("Recommended Battery Product:")
    st.components.v1.iframe("https://www.canbat.com/product/12v-100ah-cold-weather-lithium-battery/", height=400, scrolling=True)

    st.divider()
    st.subheader("Recommended Installation Service Provider:")
    st.components.v1.iframe("https://www.vancouversolarpv.ca/", height=400, scrolling=True)

    st.divider()
    st.subheader("Book an In-Person Consultation and Installation Now! We will come with everything you need")

    with st.form("my_form"):
        name = st.text_input("Your Name", "Jack Daniels")
        email = title = st.text_input("Your Email", "name@example.com")
        
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
           st.success(f"You will here from us soon {name}")


def show_survey_page():
    st.title(":green[EcoShift Survey]")
    st.divider()
    st.header("Helping You Transition to Green Energy")
    st.write("Please fill out the following form to get personalized recommendations:")

    with st.form("survey_form"):
        st.write("Rapid Form")
        budget = st.slider("What is your budget?", 0, 100000, 20000)
        home = st.text_area("What type of house do you live in?", "Condo")
        location = st.text_area("Where do you live?", "Vancouver")
        electricity_bill = st.number_input("What is your monthly electricity bill?", value=250.0, format="%.2f")

        # Additional questions
        heating_type = st.selectbox("What type of heating does your home use?", ["Electric", "Gas", "Oil", "Other"], index=0)
        cooling_type = st.selectbox("What type of cooling does your home use?", ["Central Air", "Window Units", "None"], index=2)
        water_heater_type = st.selectbox("What type of water heater do you have?", ["Electric", "Gas", "Solar", "Other"], index=0)
        solar_exposure = st.selectbox("How much sunlight does your home receive?", ["Full Sun", "Partial Shade", "Full Shade"], index=1)
        roof_type = st.selectbox("What type of roof do you have?", ["Asphalt Shingles", "Metal", "Tile", "Flat", "Other"], index=0)
        roof_age = st.slider("How old is your roof?", 0, 50, 10)
        insulation_quality = st.selectbox("How would you rate your home's insulation?", ["Poor", "Average", "Good", "Excellent"], index=1)
        windows_type = st.selectbox("What type of windows do you have?", ["Single Pane", "Double Pane", "Triple Pane"], index=1)
        appliance_efficiency = st.selectbox("How energy-efficient are your appliances?", ["Not Efficient", "Somewhat Efficient", "Very Efficient"], index=1)
        vehicle_type = st.selectbox("What type of vehicle do you drive?", ["Gasoline", "Hybrid", "Electric", "None"], index=0)
        commute_distance = st.slider("What is your daily commute distance (in km)?", 0, 100, 10)
        smart_home_devices = st.multiselect("Which smart home devices do you use?", ["Smart Thermostat", "Smart Lights", "Smart Plugs", "Smart Security", "None"], placeholder="Smart Thermostat")
        energy_saving_measures = st.multiselect("What energy-saving measures have you implemented?", ["LED Lighting", "Energy Star Appliances", "Solar Panels", "Home Automation", "None"], placeholder="LED Lighting")
        interest_in_batteries = st.selectbox("Are you interested in battery storage solutions?", ["Yes", "No"], index=1)
        interest_in_financing = st.selectbox("Are you interested in financing options?", ["Yes", "No"], index=1)

        submitted = st.form_submit_button("Submit")
        
        if submitted:
            st.session_state.budget = budget
            st.session_state.electricity_bill = electricity_bill
            st.session_state.submitted = True
            st.session_state.show_chart = False

            st.write(f"**Budget:** ${budget:,.2f}")
            st.write(f"**Home:** {home}")
            st.write(f"**Location:** {location}")
            st.write(f"**Electricity Bill:** ${electricity_bill:,.2f}")
            st.write(f"**Heating Type:** {heating_type}")
            st.write(f"**Cooling Type:** {cooling_type}")
            st.write(f"**Water Heater Type:** {water_heater_type}")
            st.write(f"**Solar Exposure:** {solar_exposure}")
            st.write(f"**Roof Type:** {roof_type}")
            st.write(f"**Roof Age:** {roof_age} years")
            st.write(f"**Insulation Quality:** {insulation_quality}")
            st.write(f"**Windows Type:** {windows_type}")
            st.write(f"**Appliance Efficiency:** {appliance_efficiency}")
            st.write(f"**Vehicle Type:** {vehicle_type}")
            st.write(f"**Commute Distance:** {commute_distance} km")
            st.write(f"**Smart Home Devices:** {', '.join(smart_home_devices) if smart_home_devices else 'None'}")
            st.write(f"**Energy-Saving Measures:** {', '.join(energy_saving_measures) if energy_saving_measures else 'None'}")
            st.write(f"**Interest in Batteries:** {interest_in_batteries}")
            st.write(f"**Interest in Financing:** {interest_in_financing}")

            budget_purchase = int(budget * 0.4)
            budget_install = int(budget * 0.2)
            budget_batteries = int(budget * 0.15)
            budget_inverter = int(budget * 0.05)
            budget_additional = int(budget * 0.1)

            st.divider()

            st.subheader("For your specifications, we recommend:")
            st.image('solar.jpg')
            st.subheader("Solar Panels")
            st.divider()
            st.success(
                f"Based on your specified information, EcoShifter AI recommends that you install "
                f"{budget_purchase:,.2f} CAD in solar panels, spend {budget_install:,.2f} CAD on installation costs, "
                f"spend {budget_batteries:,.2f} CAD on supplementary battery costs, {budget_inverter:,.2f} CAD on an inverter, "
                f"and {budget_additional:,.2f} CAD on other hardware."
            )
            st.write("For more information, purchase the premium version")
            st.divider()

    if st.session_state.get('submitted', False):
        if st.button("Premium Version", type="primary"):
            budget_purchase = st.session_state.budget * 0.4
            savings, kwh = calculate_energy_savings(st.session_state.electricity_bill, budget_purchase)
            display_recommendations(st.session_state.budget, st.session_state.electricity_bill, savings, kwh)
            st.session_state.show_chart = True




def search_bing(query):
    headers = {"User-Agent": "Mozilla/5.0"}
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
        st.divider()
        st.button("See General Product Recommendations", type="primary")
    elif page == "Survey":
        show_survey_page()
    elif page == "Search":
        show_search_page()

if __name__ == "__main__":
    main()
