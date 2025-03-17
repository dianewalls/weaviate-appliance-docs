# Appliance Document Manager

A **Streamlit application** that allows users to **store and search PDF documents** (manuals, reviews, FAQs) for home appliances (washing machines, refrigerators, monitors) using **Weaviate** as a vector database.

## 🚀 Features
- Upload appliance PDFs and extract text automatically.
- Store metadata (product type, model, brand, document type) in Weaviate.
- Perform **semantic search** on stored documents using vectorization.
- Authentication support with **API key**.

---

## 🛠️ Prerequisites

### 1️⃣ Install Python
Ensure you have **Python 3.8+** installed. You can check your version with:
```sh
python --version
```
If not installed, download it from [Python's official website](https://www.python.org/downloads/).

### 2️⃣ Create a Virtual Environment
Run the following commands to set up a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # MacOS/Linux
venv\Scripts\activate    # Windows
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

---

## 🏗️ Setup Weaviate

### 4️⃣ Create a Weaviate Cloud Instance (WCD)
1. Go to [Weaviate Cloud Console](https://console.weaviate.cloud/).
2. **Sign up** and create a **free sandbox instance**.
3. Copy the **Weaviate URL** and **API Key** from the instance details.

More details: [Weaviate Documentation](https://weaviate.io/developers/wcs)

Alternatively, you can run Weaviate locally using Docker:
```sh
docker run -d --name weaviate -p 8080:8080 semitechnologies/weaviate:latest \
  --env OPENAI_APIKEY=your_openai_key
```
More on Weaviate Docker setup: [Weaviate Quickstart](https://weaviate.io/developers/weaviate/quickstart)

### 5️⃣ Configure Environment Variables
Copy the provided `.env.sample` file and rename it to `.env`:
```sh
cp .env.sample .env
```
Then, update the `.env` file with your Weaviate URL and API key.

---

## 🔧 Running the Application

### 6️⃣ Start the Streamlit App
Once everything is set up, run:
```sh
source venv/bin/activate 
streamlit run app.py
```
This will launch the application in your browser.

---

## 🔍 Searching Documents
- Enter a search query to find relevant documents based on **semantic similarity**.
- Results include document type, product details, and a preview of the text.

---

## 🛑 Stopping the Application
To stop the app, press `CTRL + C` in the terminal.
To deactivate the virtual environment, run:
```sh
deactivate
```

---

## 📌 Future Enhancements
- 🔥 Improve document classification using AI.
- 📂 Support for more file types.
- 📊 Visualization of stored documents.

---

## 📜 License
This project is licensed under the MIT License.

---

## 🙌 Contributions
Pull requests are welcome! Open an issue for feature requests or bugs.

### 🔗 Useful Links
- **Weaviate Website:** [https://weaviate.io/](https://weaviate.io/)
- **Weaviate Cloud Console:** [https://console.weaviate.io/](https://console.weaviate.io/)
- **Weaviate Documentation:** [https://weaviate.io/developers/wcs](https://weaviate.io/developers/wcs)
- **Weaviate Quickstart Guide:** [https://weaviate.io/developers/weaviate/quickstart](https://weaviate.io/developers/weaviate/quickstart)
- **Python Downloads:** [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Streamlit Documentation:** [https://docs.streamlit.io/](https://docs.streamlit.io/)

Happy Coding! 🚀

