import streamlit as st
import weaviate
import pypdf
import os
from dotenv import load_dotenv
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.init import AdditionalConfig, Timeout
from weaviate.classes.query import MetadataQuery
import asyncio
from weaviate.exceptions import WeaviateQueryError

# Load environment variables
load_dotenv()
WEAVIATE_API_URL = os.getenv("WEAVIATE_API_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


schema_name = "ApplianceDocuments"
headers = {
    "X-OpenAI-Api-Key": OPENAI_API_KEY,
}

# ✅ Cache Weaviate Connection & Apply Schema if Missing
@st.cache_resource
def get_weaviate_client():
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_API_URL,
        auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
        headers=headers,
        additional_config=AdditionalConfig(
            timeout=Timeout(init=30, query=60, insert=120)  # Values in seconds
        )
    )

    # Apply schema if missing

    collections = client.collections.list_all()

    if schema_name in list(collections.keys()):
        print('Collection already exists')
    else:
        print('Collection not exists, will be created')

        client.collections.create(
            schema_name,
            vectorizer_config=[
                Configure.NamedVectors.text2vec_openai(
                    name="title_vector",
                    source_properties=["title"],
                    model="text-embedding-3-small",
                    dimensions=512
                ),
                Configure.NamedVectors.text2vec_openai(
                    name="content_vector",
                    source_properties=["content"],
                    model="text-embedding-3-small",
                    dimensions=512
                )
            ],
            properties=[  # properties configuration is optional
                Property(name="title", data_type=DataType.TEXT, description="Title of the document"),
                Property(name="content", data_type=DataType.TEXT, description="Document content"),
                Property(name="productType", data_type=DataType.TEXT, description="Type of product"),
                Property(name="model", data_type=DataType.TEXT, description="Product model"),
                Property(name="brand", data_type=DataType.TEXT, description="Brand name"),
                Property(name="documentType", data_type=DataType.TEXT, description="Type of document"),
            ],
        )

    return client

client = get_weaviate_client()


@st.cache_data
def extract_text_from_pdf(file, min_chunk_size=300, max_chunk_size=1000):
    """
    Extracts text from a PDF and chunks it into paragraphs for efficient vector storage.
    
    - min_chunk_size: Minimum characters per chunk before splitting.
    - max_chunk_size: Maximum characters to avoid oversized chunks.
    """
    reader = pypdf.PdfReader(file)
    chunks = []
    current_chunk = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if not page_text:
            continue  # Skip empty pages
        
        paragraphs = page_text.split("\n\n")  # Split into paragraphs

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue  # Skip empty paragraphs

            # If the current chunk is too small, keep appending
            if len(current_chunk) < min_chunk_size:
                current_chunk += " " + paragraph
            else:
                # If adding a new paragraph makes it too big, store and reset
                if len(current_chunk) + len(paragraph) > max_chunk_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    current_chunk += " " + paragraph

    # Add any leftover chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks



# ✅ Optimized Document Upload with OpenAI Vector Storage
def upload_document():
    st.header("📂 Upload PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        with st.spinner("Extracting text..."):
            chunks = extract_text_from_pdf(uploaded_file)  # 🔹 Get structured chunks!

        # User Inputs
        product_type = st.selectbox("Product Type", ["Washing Machine", "Dryer", "Refrigerator", "Monitor", "Oven", "Dishwasher", "Microwave"])
        model = st.text_input("Model", placeholder="Enter Model Number")
        brand = st.selectbox("Brand", ["LG", "Samsung"])
        document_type = st.selectbox("Document Type", ["Manual", "Review", "FAQ"])

        if st.button("Store in Weaviate"):
            with st.spinner("Storing document..."):
                appliance_documents = client.collections.get("ApplianceDocuments")

                with appliance_documents.batch.dynamic() as batch:
                    for index, chunk in enumerate(chunks):
                        obj = {
                            "title": f"{brand} {model} {product_type} {document_type} (Part {index + 1})",
                            "content": chunk,
                            "productType": product_type,
                            "model": model,
                            "brand": brand,
                            "documentType": document_type
                        }
                        batch.add_object(obj)
                        print(f"{brand} {model} {product_type} {document_type} (Part {index + 1}) added")
                        if batch.number_errors > 10:
                            print("Batch import stopped due to excessive errors.")
                            break
                failed_objects = appliance_documents.batch.failed_objects
                if failed_objects:
                    st.error(f"❌ {len(failed_objects)} documents failed to store.")
    
                    # Log detailed error information
                    for i, failed_obj in enumerate(failed_objects[:5]):  # Show up to 5 failed objects
                        st.warning(f"⚠️ Failed Object {i+1}: {failed_obj}")
    
                else: 
                    st.success("✅ Document stored successfully!")

# ✅ Optimized Search Using OpenAI-Powered Vector + Hybrid Search
def search_documents():
    st.header("🔍 Search Documents")
    query = st.text_input("Enter search query", placeholder="Type keywords...")

    if st.button("Search") and query:
        print(f"Received search query: {query}")

        with st.spinner("Searching..."):
            try:
                print("Fetching collection from Weaviate...")
                appliance_documents = client.collections.get(schema_name)
                print("Collection fetched successfully.")

                # Perform Hybrid Search (Corrected to match working GraphQL query)
                print(f"Executing hybrid search with query: {query}")
                results = appliance_documents.query.hybrid(
                    query=query,
                    alpha=0.5,  # Balancing keyword vs semantic search
                    target_vector=["content_vector"],  # Matches GraphQL format
                    limit=5,  # Keeping limit as per GraphQL query
                    return_metadata=MetadataQuery(score=True),  # Fetching certainty and distance
                    query_properties=["title", "content", "brand", "model"],  # Fetch required fields
                )


                # Handle results
                if results.objects:
                    for doc in results.objects:
                        properties = doc.properties  # Extract properties dictionary
                        metadata = doc.metadata  # Extract metadata dictionary
                        uuid = doc.uuid  # Extract UUID

                        # Extract values safely using .get()
                        title = properties.get("title", "No Title")
                        brand = properties.get("brand", "Unknown")
                        model = properties.get("model", "Unknown")
                        product_type = properties.get("productType", "Unknown")
                        document_type = properties.get("documentType", "Unknown")
                        content_snippet = properties.get("content", "")[:500]  # First 500 chars

                        score = metadata.score if metadata and metadata.score else "N/A"

                        # Display in Streamlit
                        st.subheader(f"📌 {brand} {model} ({document_type})")
                        st.write(f"**Title:** {title}")
                        st.write(f"**Product Type:** {product_type}")
                        st.write(content_snippet + "...")
                        st.write(f"🔹 **Relevance Score:** {score:.2f}")
                else:
                    print("No matching documents found.")
                    st.warning("No matching documents found.")

            except Exception as e:
                print(f"Query failed: {str(e)}", exc_info=True)
                st.error(f"Query failed: {str(e)}")

# ✅ Main Function with Navigation
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