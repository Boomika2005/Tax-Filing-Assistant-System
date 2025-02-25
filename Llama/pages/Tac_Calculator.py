import streamlit as st
import pandas as pd
from datetime import datetime
import io

def calculate_tax(income, deductions, regime, age):
    taxable_income = max(0, income - deductions)
    tax = 0
    slabs = []
    
    if regime == "Old":
        slabs = [
            (250000, 0.05),  # 5% on income from 2.5L to 5L
            (500000, 0.2),   # 20% on income from 5L to 10L
            (1000000, 0.3)   # 30% on income above 10L
        ]
        if age >= 60:
            slabs[0] = (300000, 0.05)  # Higher exemption for senior citizens
        if age >= 80:
            slabs[0] = (500000, 0.05)
        std_deduction = 50000  # Standard Deduction
        taxable_income = max(0, taxable_income - std_deduction)
    else:
        slabs = [
            (250000, 0.05),
            (500000, 0.1),
            (750000, 0.15),
            (1000000, 0.2),
            (1250000, 0.25),
            (1500000, 0.3)
        ]
    
    prev_limit = 0
    for limit, rate in slabs:
        if taxable_income > prev_limit:
            tax += (min(limit, taxable_income) - prev_limit) * rate
        prev_limit = limit
    
    return tax, taxable_income

def calculate_salary(base_pay, da_percent, hra_percent, cca, epf_percent, income_tax, prof_tax):
    months = ["March - 2020", "April - 2020", "May - 2020", "June - 2020", "July - 2020", "August - 2020", "September - 2020", "October - 2020", "November - 2020", "December - 2020", "January - 2021", "February - 2021"]
    
    data = []
    for month in months:
        da = (da_percent / 100) * base_pay
        hra = (hra_percent / 100) * base_pay
        epf = (epf_percent / 100) * base_pay
        gross = base_pay + da + hra + cca
        deductions = epf + income_tax/12 + prof_tax
        net_pay = gross - deductions
        
        data.append([month, base_pay, da, hra, cca, gross, epf, income_tax/12, prof_tax, net_pay])
    
    df = pd.DataFrame(data, columns=[
        "Month", "Pay + GP/AGP + Personal Pay + Special Pay", "Dearness Allowance", "House Rent Allowance",
        "City Compensatory Allowance", "Total Gross", "EPF Subscription", "Income Tax Deducted", "Professional Tax", "Net Pay"
    ])
    
    df.loc['Total'] = df.iloc[:, 1:].sum(numeric_only=True)
    df.loc['Total', 'Month'] = 'Total'
    
    return df

def create_excel_with_format(salary_df, tax_amount, deduction_month):
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write the dataframe
        salary_df.to_excel(writer, sheet_name='Salary Details', index=False, startrow=2)
        
        workbook = writer.book
        worksheet = writer.sheets['Salary Details']
        
        # Add title
        title_format = workbook.add_format({
            'bold': True, 
            'font_size': 14, 
            'align': 'center',
            'valign': 'vcenter'
        })
        worksheet.merge_range('A1:J2', 'Salary details for the Financial Year 2020 - 21 (Assessment Year 2021 - 22)', title_format)
        
        # Format headers
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9D9D9',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        # Apply header format
        for col_num, value in enumerate(salary_df.columns.values):
            worksheet.write(2, col_num, value, header_format)
        
        # Format for numbers
        number_format = workbook.add_format({
            'num_format': '₹#,##0.00',
            'border': 1
        })
        
        # Format for text cells
        text_format = workbook.add_format({
            'border': 1,
            'align': 'left'
        })
        
        # Apply formats to data cells
        for row_num in range(3, len(salary_df) + 3):
            worksheet.write(row_num, 0, salary_df.iloc[row_num-3, 0], text_format)  # Month column
            
            # Apply number format to numeric columns
            for col_num in range(1, len(salary_df.columns)):
                value = salary_df.iloc[row_num-3, col_num]
                worksheet.write(row_num, col_num, value, number_format)
        
        # Auto-adjust columns' width
        for i, col in enumerate(salary_df.columns):
            column_width = max(salary_df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_width)
        
        # Add the declaration text at the bottom
        end_row = len(salary_df) + 5
        tax_in_words = "zero" if tax_amount == 0 else "amount in words"  # Replace with actual conversion if needed
        
        declaration = f"Please deduct Rs. {tax_amount} /-        (Rupees {tax_in_words} only)    from  my  salary  from  the  month  of {deduction_month} onwards towards my Income Tax payment."
        signature_line = "Date:                    Place: Kavaraipettai                Signature of the Staff: _______________"
        
        worksheet.write(end_row, 0, declaration)
        worksheet.write(end_row + 2, 0, signature_line)
        
        # Merge cells for declaration and signature
        worksheet.merge_range(end_row, 0, end_row, len(salary_df.columns) - 1, declaration)
        worksheet.merge_range(end_row + 2, 0, end_row + 2, len(salary_df.columns) - 1, signature_line)
    
    buffer.seek(0)
    return buffer

# Main application
st.title("🇮🇳 Indian Income Tax Calculator")
st.write("Calculate your income tax under both Old and New Regimes.")

# Create tabs for different sections
tab1, tab2 = st.tabs(["Tax Calculator", "Salary Calculator"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Enter your Age", min_value=18, max_value=100, value=25, key="tax_age")
        regime = st.radio("Select Tax Regime", ["Old", "New"])

    with col2:
        income = st.number_input("Enter Your Annual Income (₹)", min_value=0, value=500000, key="tax_income")
        deductions = st.number_input("Total Deductions (₹, Only for Old Regime)", min_value=0, value=0, key="tax_deductions")

    if st.button("Calculate Tax"):
        tax, taxable_income = calculate_tax(income, deductions if regime == "Old" else 0, regime, age)
        st.success(f"Taxable Income: ₹{taxable_income:,.2f}")
        st.error(f"Total Tax Payable: ₹{tax:,.2f}")
        
        st.subheader("Tax Slabs Used")
        slab_df = pd.DataFrame({
            "Regime": ["Old", "New"],
            "0 - 2.5L": ["No Tax", "No Tax"],
            "2.5L - 5L": ["5%", "5%"],
            "5L - 7.5L": ["20%", "10%"],
            "7.5L - 10L": ["20%", "15%"],
            "10L - 12.5L": ["30%", "20%"],
            "12.5L - 15L": ["30%", "25%"],
            "Above 15L": ["30%", "30%"]
        })
        st.table(slab_df)

with tab2:
    st.subheader("Annual Salary Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        base_pay = st.number_input("Basic Pay (₹)", min_value=0, value=30000)
        da_percent = st.number_input("Dearness Allowance (%)", min_value=0.0, value=5.0)
        hra_percent = st.number_input("House Rent Allowance (%)", min_value=0.0, value=10.0)
    
    with col2:
        cca = st.number_input("City Compensatory Allowance (₹)", min_value=0, value=1000)
        epf_percent = st.number_input("EPF Contribution (%)", min_value=0.0, value=12.0)
        income_tax = st.number_input("Annual Income Tax (₹)", min_value=0, value=12000)
        prof_tax = st.number_input("Monthly Professional Tax (₹)", min_value=0, value=200)
    
    # Add options for tax declaration
    st.subheader("Tax Declaration")
    tax_amount = st.number_input("Tax Amount to Deduct (₹)", min_value=0, value=0)
    deduction_month = st.selectbox(
        "Starting Month for Deduction",
        ["March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February"]
    )

    salary_df = None
    if st.button("Generate Salary Details"):
        salary_df = calculate_salary(base_pay, da_percent, hra_percent, cca, epf_percent, income_tax, prof_tax)
        st.write("Salary Details:")
        st.dataframe(salary_df)
        
        # Store the dataframe in session state to access it later for download
        st.session_state.salary_df = salary_df
        st.session_state.tax_amount = tax_amount
        st.session_state.deduction_month = deduction_month
    
    # Add download button
    if 'salary_df' in st.session_state:
        buffer = create_excel_with_format(
            st.session_state.salary_df, 
            st.session_state.tax_amount,
            st.session_state.deduction_month
        )
        
        file_name = f"Salary_Details_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        
        st.download_button(
            label="Download Salary Excel",
            data=buffer,
            file_name=file_name,
            mime="application/vnd.ms-excel"
        )

# Add footer
st.markdown("---")
st.markdown("© 2025 Indian Income Tax Calculator | For informational purposes only")