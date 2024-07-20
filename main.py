import streamlit as st


def survey():

    

    import streamlit as st
    import pandas as pd
    
    
    def style(budget, current_bill, solar_panel_cost):
        # Constants
        BASIC_CHARGE = 6.759  # Monthly basic charge in dollars
        STEP1_RATE = 0.1097   # Step 1 energy charge in dollars per kWh
        STEP2_RATE = 0.1408   # Step 2 energy charge in dollars per kWh
        STEP1_LIMIT = 1376    # Step 1 limit in kWh
        SOLAR_COST_PER_WATT = 2.30
        HOURS_PER_DAY = 4
        DAYS_PER_MONTH = 30
    
        # Calculate net charge excluding the basic charge
        net_charge = current_bill - BASIC_CHARGE
    
        # Determine total kWh consumption (Q)
        if net_charge <= STEP1_LIMIT * STEP1_RATE:
            total_kwh_consumption = net_charge / STEP1_RATE
        else:
            q1_cost = STEP1_LIMIT * STEP1_RATE
            q2_cost = (net_charge - q1_cost) / STEP2_RATE
            total_kwh_consumption = STEP1_LIMIT + q2_cost
    
        # Calculate the total kWh production from the installed solar panels
        system_size_watts = solar_panel_cost / SOLAR_COST_PER_WATT
        monthly_solar_kwh = (system_size_watts / 1000) * HOURS_PER_DAY * DAYS_PER_MONTH
    
        # Compute monthly savings
        if monthly_solar_kwh <= STEP1_LIMIT:
            savings = monthly_solar_kwh * STEP1_RATE
        else:
            savings = (STEP1_LIMIT * STEP1_RATE) + ((monthly_solar_kwh - STEP1_LIMIT) * STEP2_RATE)
    
        data_df = pd.DataFrame(
            {
        "sales": [
                    [current_bill, (current_bill - savings)],
                ],
            }
        )

        st.data_editor(
            data_df,
            column_config={
                "sales": st.column_config.BarChartColumn(
                    "Sales (last 6 months)",
                    help="The sales volume in the last 6 months",
                    y_min=0,
                    y_max=100,
                ),
            },
            hide_index=True,
        )

    # Streamlit app
    st.title("EcoShift")
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
            st.write(f"Budget: {budget}")
            st.write(f"Home: {home}")
            st.write(f"Location: {location}")
            st.write(f"Electricity Bill: {electricity_bill}")
            
            
            st.header("Recommended Green Energy Source")
            budget = int(budget)
            electricity_bill = int(electricity_bill)
            budget_purchase = budget * 0.4
            budget_install = budget * 0.2
            budget_batteries = budget * 0.15
            budget_inverter = budget *0.05
            budget_additional = 0.1
            
            
            
            st.success(f"Based on your specified information, EcoEstimator AI reccommends that you install ${budget_purchase} worth of solar panels, spend ${budget_install} on installation, spends ${budget_batteries} on supplementary battery costs, ${budget_inverter} on an inverter, and ${budget_additional} on other hardware") 
            st.write("For more information, purchase the premium version")

            style(budget, electricity_bill, budget_purchase)


page_names_to_funcs = {
    "English": survey,
    "Français": survey
}

demo_name = st.sidebar.selectbox("Select Option", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
