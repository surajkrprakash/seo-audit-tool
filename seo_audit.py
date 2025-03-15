import requests
from bs4 import BeautifulSoup
import streamlit as st

def fetch_seo_data(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return {"error": f"Failed to fetch the page (Status Code: {response.status_code})"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract Title
        title = soup.title.string if soup.title else "No title found"
        
        # Extract Meta Description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"] if meta_desc else "No description found"
        
        # Extract Headings
        headings = {f"h{i}": [tag.text.strip() for tag in soup.find_all(f"h{i}")] for i in range(1, 7)}
        
        return {
            "title": title,
            "description": description,
            "headings": headings
        }
    except Exception as e:
        return {"error": str(e)}

# Streamlit UI
st.title("Free SEO Audit Tool")
url = st.text_input("Enter Website URL")
if st.button("Analyze"):
    if url:
        result = fetch_seo_data(url)
        if "error" in result:
            st.error(result["error"])
        else:
            st.subheader("SEO Audit Report")
            st.write(f"**Title:** {result['title']}")
            st.write(f"**Meta Description:** {result['description']}")
            st.write("**Headings:**")
            for tag, texts in result["headings"].items():
                st.write(f"{tag.upper()}: {', '.join(texts) if texts else 'None'}")
    else:
        st.warning("Please enter a valid URL.")
