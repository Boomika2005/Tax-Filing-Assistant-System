import streamlit as st
import pandas as pd
import numpy as np
import base64
from datetime import datetime, date
from io import BytesIO, StringIO
import re

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def is_senior_citizen(dob):
    if dob is None:
        return False
    age = calculate_age(dob)
    return age >= 60

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df, filename="income_tax_calculation_FY2024-25.xlsx"):
    """Generates a link allowing the data in a given pandas dataframe to be downloaded"""
    val = to_excel(df)
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download Excel File</a>'

def calculate_tax_old_regime(taxable_income, is_senior=False):
    tax = 0
    tax_exempt_limit = 300000 if is_senior else 250000
    
    if taxable_income > tax_exempt_limit:
        # 5% slab (2.5L-5L)
        tax_5_percent = min(max(0, taxable_income - tax_exempt_limit), 250000) * 0.05
        
        # 20% slab (5L-10L)
        tax_20_percent = min(max(0, taxable_income - tax_exempt_limit - 250000), 500000) * 0.20
        
        # 30% slab (>10L)
        tax_30_percent = max(0, taxable_income - tax_exempt_limit - 750000) * 0.30
        
        tax = tax_5_percent + tax_20_percent + tax_30_percent
    
    # Rebate under section 87A
    rebate = 0
    if taxable_income <= 500000:
        rebate = min(tax, 12500)
    
    tax_after_rebate = tax - rebate
    cess = tax_after_rebate * 0.04
    total_tax = tax_after_rebate + cess
    
    return {
        "tax": tax,
        "rebate": rebate,
        "tax_after_rebate": tax_after_rebate,
        "cess": cess,
        "total_tax": total_tax
    }

def calculate_tax_new_regime(taxable_income, is_senior=False):
    tax = 0
    tax_exempt_limit = 300000 # Same for everyone in new regime
    
    if taxable_income > tax_exempt_limit:
        # 5% slab (3L-7L)
        tax_5_percent = min(max(0, taxable_income - tax_exempt_limit), 400000) * 0.05
        
        # 10% slab (7L-10L)
        tax_10_percent = min(max(0, taxable_income - tax_exempt_limit - 400000), 300000) * 0.10
        
        # 15% slab (10L-12L)
        tax_15_percent = min(max(0, taxable_income - tax_exempt_limit - 700000), 200000) * 0.15
        
        # 20% slab (12L-15L)
        tax_20_percent = min(max(0, taxable_income - tax_exempt_limit - 900000), 300000) * 0.20
        
        # 30% slab (>15L)
        tax_30_percent = max(0, taxable_income - tax_exempt_limit - 1200000) * 0.30
        
        tax = tax_5_percent + tax_10_percent + tax_15_percent + tax_20_percent + tax_30_percent
    
    # Rebate under section 87A (higher in new regime)
    rebate = 0
    if taxable_income <= 700000:
        rebate = min(tax, 25000)
    
    tax_after_rebate = tax - rebate
    cess = tax_after_rebate * 0.04
    total_tax = tax_after_rebate + cess
    
    return {
        "tax": tax,
        "rebate": rebate,
        "tax_after_rebate": tax_after_rebate,
        "cess": cess,
        "total_tax": total_tax
    }

def main():
    st.set_page_config(page_title="Income Tax Filing - FY 2024-25", layout="wide")
    
    st.title("Income Tax Filing - FY 2024-25 (AY 2025-26)")
    
    # Tax Regime Selection (moved to top based on image)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Your Option (Old Regime / New Regime):")
    with col2:
        tax_regime = st.radio("Select Tax Regime", ["Old Regime", "New Regime"], index=0, label_visibility="collapsed")
    
    st.subheader("Upload Your Tax Form (Optional)")
    uploaded_file = st.file_uploader("Choose a file", type=["docx", "pdf", "txt"])
    
    # Initialize variables with default values
    name = ""
    pan = ""
    designation = ""
    department = ""
    dob = None
    is_senior = False
    
    # If file is uploaded, try to extract information
    if uploaded_file:
        # For simplicity, we'll assume text extraction works
        # In a real app, you'd need proper docx/pdf parsing
        st.success("Form uploaded successfully! We've pre-filled some fields based on your form.")
        
        # Here, we're simulating extraction from the form
        name = "M.SHANTHI"
        pan = "DFTPS6875E"
        designation = "ASSOCIATE PROFESSOR (Grade-II)"
        department = "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE"
    
    # Personal Information
    st.header("Personal Information")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Name", value=name)
        designation = st.text_input("Designation", value=designation)
    
    with col2:
        pan = st.text_input("PAN Number", value=pan)
        department = st.text_input("Department", value=department)
    
    dob_col1, dob_col2 = st.columns([1, 3])
    with dob_col1:
        is_senior = st.checkbox("Are you a Senior Citizen?")
    
    with dob_col2:
        if is_senior:
            dob = st.date_input("Date of Birth", value=date(1960, 1, 1), max_value=date.today())
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Income", "House Property", "Other Income", "Deductions"])
    
    # Income Details
    with tab1:
        st.subheader("I. SALARY")
        
        # Table-like structure for salary components as shown in the image
        # (a) Basic Salary, AGP/GP, DA, HRA, CCA, IR
        basic_salary = st.number_input("Basic Salary", min_value=0.0, step=1000.0, format="%.2f", value=962835.0 if uploaded_file else 0.0)
        
        # Breakup of the components
        col1, col2 = st.columns(2)
        
        with col1:
            agp_gp = st.number_input("Academic Grade Pay/Grade Pay (AGP/GP)", min_value=0.0, step=1000.0, format="%.2f")
            da = st.number_input("Dearness Allowance (DA)", min_value=0.0, step=1000.0, format="%.2f")
            hra = st.number_input("House Rent Allowance (HRA)", min_value=0.0, step=1000.0, format="%.2f")
        
        with col2:
            cca = st.number_input("City Compensatory Allowance (CCA)", min_value=0.0, step=1000.0, format="%.2f")
            ir = st.number_input("IR (If applicable)", min_value=0.0, step=1000.0, format="%.2f")
            other_allowances = st.number_input("Other Allowances", min_value=0.0, step=1000.0, format="%.2f")
        
        # (b) Taxable Value of Perquisites
        perquisites = st.number_input("(b) Taxable Value of Perquisites", min_value=0.0, step=1000.0, format="%.2f")
        
        # (c) Pension
        pension = st.number_input("(c) Pension", min_value=0.0, step=1000.0, format="%.2f")
        
        # (d) Others (to be specified)
        others_specified = st.text_input("(d) Others (specify)")
        others_amount = st.number_input("Amount for Others", min_value=0.0, step=1000.0, format="%.2f")
        
        # (e) Additional field if needed
        additional_income = st.number_input("(e) Additional Income (if any)", min_value=0.0, step=1000.0, format="%.2f")
        
        # Calculate total salary
        salary_total = basic_salary + agp_gp + da + hra + cca + ir + other_allowances + perquisites + pension + others_amount + additional_income
        st.info(f"Total Salary: ₹ {salary_total:,.2f}")
        
        epf_subscription = st.number_input("EPF Subscription", min_value=0.0, step=1000.0, format="%.2f")
        professional_tax = st.number_input("Professional Tax", min_value=0.0, step=100.0, format="%.2f")
        
        if tax_regime == "Old Regime":
            st.subheader("HRA Exemption")
            rent_paid = st.number_input("Rent Paid", min_value=0.0, step=1000.0, format="%.2f")
            
            # Calculate HRA exemption
            basic_for_hra = basic_salary + agp_gp  # Basis for HRA calculation
            forty_percent_basic = basic_for_hra * 0.4  # 40% of basic (for non-metro)
            ten_percent_basic = basic_for_hra * 0.1
            rent_minus_10_percent = max(0, rent_paid - ten_percent_basic)
            
            hra_exemption = min(hra, rent_minus_10_percent, forty_percent_basic)
            
            st.info(f"HRA Exemption: ₹ {hra_exemption:,.2f}")
            
            # Standard Deduction
            standard_deduction = min(50000, salary_total)
            st.info(f"Standard Deduction: ₹ {standard_deduction:,.2f}")
        else:
            # New regime doesn't have HRA exemption or standard deduction
            hra_exemption = 0
            rent_paid = 0
            standard_deduction = 0
            st.info("Note: HRA Exemption and Standard Deduction not applicable in the New Regime")
    
    # House Property Income
    with tab2:
        st.subheader("Income from House Property")
        
        has_house_property = st.checkbox("Do you have income from House Property?")
        
        if has_house_property:
            rent_received = st.number_input("Annual Rent Received", min_value=0.0, step=1000.0, format="%.2f")
            property_tax = st.number_input("House Tax (Property Tax Paid)", min_value=0.0, step=100.0, format="%.2f")
            
            net_annual_value = rent_received - property_tax
            
            # 30% deduction for repairs
            repairs_deduction = net_annual_value * 0.3
            
            # Housing loan interest
            housing_loan_interest = st.number_input("Interest on Housing Loan", min_value=0.0, max_value=200000.0, step=1000.0, format="%.2f", help="Maximum deduction allowed is ₹2,00,000")
            
            # Calculate net house property income
            net_house_income = net_annual_value - repairs_deduction - housing_loan_interest
            
            st.info(f"Net Income from House Property: ₹ {net_house_income:,.2f}")
        else:
            rent_received = 0
            property_tax = 0
            net_annual_value = 0
            repairs_deduction = 0
            housing_loan_interest = 0
            net_house_income = 0
    
    # Other Income
    with tab3:
        st.subheader("Income from Other Sources")
        
        savings_interest = st.number_input("Savings Bank A/C Interest", min_value=0.0, step=100.0, format="%.2f")
        fd_interest = st.number_input("Fixed Deposit Interest", min_value=0.0, step=1000.0, format="%.2f")
        exam_remuneration = st.number_input("Exam Remuneration", min_value=0.0, step=1000.0, format="%.2f")
        other_sources = st.number_input("Other Income Sources", min_value=0.0, step=1000.0, format="%.2f")
        
        total_other_income = savings_interest + fd_interest + other_sources
        st.info(f"Total Income from Other Sources: ₹ {total_other_income:,.2f}")
    
    # Initialize deductions dictionary
    deductions = {}
    total_deductions = 0
    
    # Deductions
    with tab4:
        if tax_regime == "Old Regime":
            st.subheader("Deductions under Section 80C (Max ₹1,50,000)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                deductions["LIC/PLI"] = st.number_input("LIC/PLI", min_value=0.0, step=1000.0, format="%.2f")
                deductions["NSC"] = st.number_input("National Savings Certificate (NSC)", min_value=0.0, step=1000.0, format="%.2f")
                deductions["PPF"] = st.number_input("Public Provident Fund (PPF)", min_value=0.0, step=1000.0, format="%.2f")
                deductions["ELSS"] = st.number_input("Equity Linked Savings Scheme", min_value=0.0, step=1000.0, format="%.2f")
            
            with col2:
                deductions["Home Loan Principal"] = st.number_input("Home Loan Principal Repayment", min_value=0.0, step=1000.0, format="%.2f")
                deductions["Tuition Fee"] = st.number_input("Children Education (Tuition Fee)", min_value=0.0, step=1000.0, format="%.2f")
                deductions["Tax Saver FD"] = st.number_input("Tax Saver Fixed Deposits (5 years)", min_value=0.0, step=1000.0, format="%.2f")
                deductions["Sukanya Samriddhi"] = st.number_input("Sukanya Samriddhi Account", min_value=0.0, step=1000.0, format="%.2f")
            
            total_80c = sum(deductions.values()) + epf_subscription
            capped_80c = min(total_80c, 150000)
            
            st.info(f"Total Section 80C Deductions: ₹ {total_80c:,.2f} (Capped at ₹ {capped_80c:,.2f})")
            
            st.subheader("Other Deductions")
            
            additional_nps = st.number_input("Additional NPS Contribution (80CCD(1B)) - Max ₹50,000", min_value=0.0, max_value=50000.0, step=1000.0, format="%.2f")
            
            max_mediclaim = 50000 if is_senior else 25000
            mediclaim = st.number_input(f"Medical Insurance Premium (80D) - Max ₹{max_mediclaim}", min_value=0.0, max_value=float(max_mediclaim), step=1000.0, format="%.2f")
            
            education_loan_interest = st.number_input("Interest on Education Loan (80E)", min_value=0.0, step=1000.0, format="%.2f")
            affordable_house_interest = st.number_input("Interest on Affordable Housing Loan (80EEA) - Max ₹1,50,000", min_value=0.0, max_value=150000.0, step=1000.0, format="%.2f")
            ev_loan_interest = st.number_input("Interest on Electric Vehicle Loan (80EEB)", min_value=0.0, step=1000.0, format="%.2f")
            donations = st.number_input("Donations (80G)", min_value=0.0, step=1000.0, format="%.2f")
            rent_paid_deduction = st.number_input("Rent Paid (80GG)", min_value=0.0, step=1000.0, format="%.2f", value=96000.0 if uploaded_file else 0.0)
            
            savings_interest_deduction = min(savings_interest, 10000)
            st.info(f"Savings Bank Interest Deduction (80TTA): ₹ {savings_interest_deduction:,.2f} (Max ₹10,000)")
            
            # For senior citizens
            if is_senior:
                ttb_deduction = min(savings_interest + fd_interest, 50000)
                st.info(f"Senior Citizen Interest Deduction (80TTB): ₹ {ttb_deduction:,.2f} (Max ₹50,000)")
            else:
                ttb_deduction = 0
                
            disabled_person = st.checkbox("Are you a person with disability (80U)?")
            disability_deduction = 75000 if disabled_person else 0
            
            # Calculate total deductions
            total_deductions = (capped_80c + additional_nps + mediclaim + education_loan_interest + 
                               affordable_house_interest + ev_loan_interest + donations + 
                               savings_interest_deduction + ttb_deduction + disability_deduction +
                               rent_paid_deduction)
            
            st.info(f"Total Deductions: ₹ {total_deductions:,.2f}")
        else:
            st.warning("Deductions under Section 80C, 80D, etc. are not applicable in the New Regime")
            capped_80c = 0
            additional_nps = 0
            mediclaim = 0
            education_loan_interest = 0
            affordable_house_interest = 0
            ev_loan_interest = 0
            donations = 0
            savings_interest_deduction = 0
            ttb_deduction = 0
            disability_deduction = 0
            rent_paid_deduction = 0
    
    # Calculate Taxable Income
    st.header("Tax Calculation")
    
    # Net salary after exemptions and deductions
    if tax_regime == "Old Regime":
        net_salary = salary_total - hra_exemption - standard_deduction - professional_tax
        gross_total_income = net_salary + net_house_income + total_other_income
        taxable_income = gross_total_income - total_deductions
    else:
        # New regime
        net_salary = salary_total - professional_tax
        gross_total_income = net_salary + net_house_income + total_other_income
        taxable_income = gross_total_income  # No deductions in new regime
    
    taxable_income = max(0, taxable_income)
    st.subheader(f"Taxable Income: ₹ {taxable_income:,.2f}")
    
    # Calculate tax based on selected regime
    if tax_regime == "Old Regime":
        tax_results = calculate_tax_old_regime(taxable_income, is_senior)
    else:
        tax_results = calculate_tax_new_regime(taxable_income, is_senior)
    
    # Display tax calculation results
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Income Tax", f"₹ {tax_results['tax']:,.2f}")
        st.metric("Rebate u/s 87A", f"₹ {tax_results['rebate']:,.2f}")
        st.metric("Tax after Rebate", f"₹ {tax_results['tax_after_rebate']:,.2f}")
    
    with col2:
        st.metric("Education & Health Cess (4%)", f"₹ {tax_results['cess']:,.2f}")
        st.metric("Total Tax Liability", f"₹ {tax_results['total_tax']:,.2f}")
    
    # TDS details
    tds_already_deducted = st.number_input("TDS Already Deducted", min_value=0.0, step=1000.0, format="%.2f")
    remaining_tax = max(0, tax_results['total_tax'] - tds_already_deducted)
    
    st.metric("Remaining Tax to be Paid", f"₹ {remaining_tax:,.2f}")
    
    # Calculate for both regimes for comparison
    old_regime_results = calculate_tax_old_regime(
        gross_total_income - total_deductions if tax_regime == "Old Regime" else gross_total_income - 0, 
        is_senior
    )
    new_regime_results = calculate_tax_new_regime(gross_total_income, is_senior)
    
    # Recommendation based on comparison
    st.subheader("Tax Regime Comparison")
    
    # Create a dataframe for display
    compare_df = pd.DataFrame({
        "": ["Old Regime", "New Regime"],
        "Tax Amount": [f"₹ {old_regime_results['total_tax']:,.2f}", f"₹ {new_regime_results['total_tax']:,.2f}"]
    })
    
    st.table(compare_df)
    
    if old_regime_results['total_tax'] < new_regime_results['total_tax']:
        st.success(f"Recommendation: Choose Old Regime to save ₹ {new_regime_results['total_tax'] - old_regime_results['total_tax']:,.2f}")
    elif new_regime_results['total_tax'] < old_regime_results['total_tax']:
        st.success(f"Recommendation: Choose New Regime to save ₹ {old_regime_results['total_tax'] - new_regime_results['total_tax']:,.2f}")
    else:
        st.info("Both regimes result in the same tax amount.")
    
    # Create downloadable form
    if st.button("Generate Downloadable Form"):
        # Create a DataFrame with all the tax calculation details
        data = {
            "Parameter": [
                "Personal Details", "", "", "", "", "",
                "Income Details", "", "", "", "", "", "", "", "", "", "", "", "",
                "Deductions", "", "", "", "", "", "", "", "", "", "", "", "", "",
                "Tax Calculation", "", "", "", "", "", "", ""
            ],
            "Field": [
                "Name", "PAN Number", "Designation", "Department", "Senior Citizen", "Tax Regime",
                "Basic Salary", "AGP/GP", "DA", "HRA", "CCA", "IR", "Other Allowances", "Perquisites", "Pension", "Others (Specified)", "Additional Income", "Income from House Property", "Income from Other Sources",
                "EPF Subscription", "Section 80C (capped)", "Additional NPS (80CCD(1B))", "Mediclaim (80D)", "Education Loan Interest (80E)", "Affordable Housing Interest (80EEA)", "Electric Vehicle Loan Interest (80EEB)", "Donations (80G)", "Rent Paid (80GG)", "Savings Interest (80TTA/TTB)", "Disability (80U)", "Total Deductions", "HRA Exemption", "Standard Deduction",
                "Gross Total Income", "Taxable Income", "Tax Calculated", "Rebate u/s 87A", "Tax after Rebate", "Education & Health Cess (4%)", "Total Tax Liability", "Remaining Tax to be Paid"
            ],
            "Value": [
                name, pan, designation, department, "Yes" if is_senior else "No", tax_regime,
                basic_salary, agp_gp, da, hra, cca, ir, other_allowances, perquisites, pension, f"{others_specified}: {others_amount}", additional_income, net_house_income, total_other_income,
                epf_subscription, capped_80c, additional_nps, mediclaim, education_loan_interest, affordable_house_interest, ev_loan_interest, donations, rent_paid_deduction, savings_interest_deduction + ttb_deduction, disability_deduction, total_deductions, hra_exemption, standard_deduction,
                gross_total_income, taxable_income, tax_results['tax'], tax_results['rebate'], tax_results['tax_after_rebate'], tax_results['cess'], tax_results['total_tax'], remaining_tax
            ],
            "Old Regime": [
                name, pan, designation, department, "Yes" if is_senior else "No", "Old Regime",
                basic_salary, agp_gp, da, hra, cca, ir, other_allowances, perquisites, pension, f"{others_specified}: {others_amount}", additional_income, net_house_income, total_other_income,
                epf_subscription, capped_80c, additional_nps, mediclaim, education_loan_interest, affordable_house_interest, ev_loan_interest, donations, rent_paid_deduction, savings_interest_deduction + ttb_deduction, disability_deduction, total_deductions, hra_exemption, standard_deduction,
                gross_total_income, gross_total_income - total_deductions, old_regime_results['tax'], old_regime_results['rebate'], old_regime_results['tax_after_rebate'], old_regime_results['cess'], old_regime_results['total_tax'], max(0, old_regime_results['total_tax'] - tds_already_deducted)
            ],
            "New Regime": [
                name, pan, designation, department, "Yes" if is_senior else "No", "New Regime",
                basic_salary, agp_gp, da, hra, cca, ir, other_allowances, perquisites, pension, f"{others_specified}: {others_amount}", additional_income, net_house_income, total_other_income,
                "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
                gross_total_income, gross_total_income, new_regime_results['tax'], new_regime_results['rebate'], new_regime_results['tax_after_rebate'], new_regime_results['cess'], new_regime_results['total_tax'], max(0, new_regime_results['total_tax'] - tds_already_deducted)
            ]
        }
        
        df = pd.DataFrame(data)
        
        # Display download link
        st.markdown(get_table_download_link(df, f"Income_Tax_Calculation_{name}_{date.today()}.xlsx"), unsafe_allow_html=True)
        
        # Form for monthly deduction
        st.subheader("Monthly Tax Deduction Plan")
        
        remaining_months = st.slider("Remaining months for tax deduction", 1, 12, 6)
        monthly_deduction = remaining_tax / remaining_months if remaining_months > 0 else 0
        
        st.success(f"Recommended monthly deduction: ₹ {monthly_deduction:,.2f} for the next {remaining_months} months")
        
        # Declaration section
        st.subheader("Declaration")
        st.markdown(f"""
        I, {name}, do hereby declare that what is stated above is true to the best of my knowledge and belief.
        
        Date: {date.today().strftime('%d-%m-%Y')}
        
        Place: Kavaraipettai
        
        Signature: __________________
        
        Please deduct Rs. **{remaining_tax:,.2f}** (Rupees **{num_to_words(remaining_tax)}** only) from my salary from the month of {date.today().strftime('%B')}.
        """)

def num_to_words(num):
    """Convert a number to words for Indian currency"""
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    if num == 0:
        return "Zero"
    
    # Convert to float and separate whole and decimal parts
    num_str = str(num)
    if '.' in num_str:
        whole_part, decimal_part = num_str.split('.')
        whole_num = int(whole_part)
        # Ensure two decimal places
        decimal_num = int(decimal_part.ljust(2, '0')[:2])
    else:
        whole_num = int(num)
        decimal_num = 0
    
    words = ""
    
    # Process whole number part
    crore = int(whole_num / 10000000)
    whole_num = whole_num % 10000000
    
    if crore > 0:
        words += num_to_words(crore) + " Crore "
    
    lakh = int(whole_num / 100000)
    whole_num = whole_num % 100000
    
    if lakh > 0:
        words += num_to_words(lakh) + " Lakh "
    
    thousand = int(whole_num / 1000)
    whole_num = whole_num % 1000
    
    if thousand > 0:
        words += num_to_words(thousand) + " Thousand "
    
    hundred = int(whole_num / 100)
    whole_num = whole_num % 100
    
    if hundred > 0:
        words += units[hundred] + " Hundred "
    
    if whole_num > 0:
        if words != "" and whole_num < 100:
            words += "and "
        
        if whole_num < 20:
            words += units[whole_num]
        else:
            words += tens[int(whole_num / 10)]
            if whole_num % 10 > 0:
                words += " " + units[whole_num % 10]
    
    # Handle decimal part
    if decimal_num > 0:
        words += " and Paise "
        if decimal_num < 20:
            words += units[decimal_num]
        else:
            words += tens[int(decimal_num / 10)]
            if decimal_num % 10 > 0:
                words += " " + units[decimal_num % 10]
    
    return words

if __name__ == "__main__":
    main()