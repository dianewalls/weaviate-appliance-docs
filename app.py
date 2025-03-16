import streamlit as st
import weaviate
import pypdf
import os
from dotenv import load_dotenv
from weaviate.classes.init import Auth

# Load environment variables
load_dotenv()
WEAVIATE_API_URL = os.getenv("WEAVIATE_API_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")


# Schema 
def get_schema():
    schema = {
        "class": "ApplianceDocuments",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {"text2vec-openai": {"model": "text-embedding-ada-002"}},
        "properties": [
            {"name": "content", "dataType": ["text"]},
            {"name": "productType", "dataType": ["text"]},
            {"name": "model", "dataType": ["text"]},
            {"name": "brand", "dataType": ["text"]},
            {"name": "documentType", "dataType": ["text"]}
        ]
    }
    

# Cache Weaviate connection
@st.cache_resource
def get_weaviate_client():
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_API_URL,
        auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
    )
   # if not client.schema.contains(get_schema()):
   #     client.schema.create_class(get_schema())
    return client

client = get_weaviate_client()


# Cache PDF text extraction
@st.cache_data
def extract_text_from_pdf(file):
    reader = pypdf.PdfReader(file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

# Function for document upload
def upload_document():
    st.header("📂 Upload PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        with st.spinner("Extracting text..."):
            extracted_text = extract_text_from_pdf(uploaded_file)

        # User Inputs
        product_type = st.text_input("Product Type", placeholder="Washing Machine, Refrigerator, Monitor, etc.")
        model = st.text_input("Model", placeholder="Enter Model Number")
        brand = st.text_input("Brand", placeholder="Enter Brand Name")
        document_type = st.selectbox("Document Type", ["Manual", "Review", "FAQ"])

        if st.button("Store in Weaviate"):
            with st.spinner("Storing document..."):
                obj = {
                    "content": extracted_text,
                    "productType": product_type,
                    "model": model,
                    "brand": brand,
                    "documentType": document_type
                }
                client.data_object.create(obj, class_name="ApplianceDocuments")
                st.success("✅ Document stored successfully!")

# Function for document search
def search_documents():
    st.header("🔍 Search Documents")
    query = st.text_input("Enter search query", placeholder="Type keywords...")

    if st.button("Search") and query:
        with st.spinner("Searching..."):
            response = (
                client.query.get("ApplianceDocuments", ["content", "productType", "model", "brand", "documentType"])
                .with_near_text({"concepts": [query]})
                .with_limit(5)
                .do()
            )

        results = response.get("data", {}).get("Get", {}).get("ApplianceDocuments", [])
        
        if results:
            for doc in results:
                st.subheader(f"📌 {doc['brand']} {doc['model']} ({doc['documentType']})")
                st.write(doc["content"][:500] + "...")
        else:
            st.warning("No matching documents found.")

# Main function
def main():
    st.title("📄 Appliance Document Manager")
    st.write("Upload and search appliance-related documents.")

    # Sidebar for navigation
    menu = ["Upload Document", "Search Documents"]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "Upload Document":
        upload_document()
    elif choice == "Search Documents":
        search_documents()

if __name__ == "__main__":
    main()