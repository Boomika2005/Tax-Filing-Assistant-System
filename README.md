# Tax Filing and Assistant System #

The Tax Assistant is a comprehensive web tool designed to simplify calculations for users in India and the United States. It offers features such as automated tax filing for Form 16 (India only), tax computation under both old and new regimes, personalized deduction suggestions, and downloadable reports. Built with Streamlit and Python, the application leverages multiple APIs to ensure accurate and efficient processing.

Features:

1. Tax Assistant BOT:

* Calculates tax based on the amount provided.
* Supports both old and new tax regimes.
* Available for users in the USA and India.

2. Tax Filing (Form 16):

* Collects personal details via user input or uploaded documents.
* Gathers user income details and calculates tax liabilities.
* Automatically fills the declaration form.
* Provides the completed Form 16 as a downloadable Excel file.

3. Deduction Suggestions:

* Suggests applicable deductions based on user input.
* Provides downloadable summaries for easy reference.

4. Downloadable Chat History:

* Users can download their interaction and calculation history for record-keeping.


Tax Filing and Assistant System Dashboard:

The dashboard provides an intuitive user interface to access all features, including:

1. Tax Assistant Bot: For both USA & India and suggest deductions as personalized recommendations..
![Image](https://github.com/user-attachments/assets/0939de31-f89c-4e01-95f9-c0d8553901e3)

2. Tax Calculator: Instant tax computation.
![Image](https://github.com/user-attachments/assets/f4531a3f-a7dd-4d60-ac72-d448ffe4dfb1)

3. Tax Filing: Automated Form 16 generation for India.
![Image](https://github.com/user-attachments/assets/bcf7066d-5d0c-476e-a8f3-fbdd7cd5dd6c)


Tech Stack:

* Framework: Streamlit 7
* Programming Language: Python, MySQL
* APIs Used:
    - GROQ_API_KEY
    - LLAMA_CLOUD_API_KEY
    - QDRANT_API_KEY

Installation and Setup
Follow these steps to set up and run the Tax Assistant application:

1. Clone the Repository:
    ``````````
    cd Llama

    ``````````
2. Create Virtual Environment:
    ````````````````````
    python -m venv venv

    ````````````````````
3. Activate Virtual Environment:
    - Windows:
       ``````````````````````
       venv\Scripts\activate

       ``````````````````````
    - Linux/Mac:
       `````````````````````````
       source venv/bin/activate
    
       `````````````````````````
4. Install Dependencies:
    `````````````````````````````````
    pip install -r requirements.txt

    `````````````````````````````````
5. Install API Mentioned below and add the API's by creating a folder named ".streamlit" in root of the directory inside that create a file name
 ".toml".

   ```````````````````````````````````````````````````
    - GROQ_API_KEY=your_groq_api_key
    - LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
    - QDRANT_API_KEY=your_qdrant_api_key

 ```````````````````````````````````````````````````````

6. Run the Application:

   ````````````````````````
    streamlit run app.py

   ````````````````````````
7.  Open your web browser and go to `http://localhost:8501` to use Tax Assistant.

