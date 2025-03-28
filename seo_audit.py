import requests
from bs4 import BeautifulSoup
import streamlit as st
import pdfkit
from io import BytesIO

def fetch_seo_data(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return {"error": f"Failed to fetch the page (Status Code: {response.status_code})"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract Title
        title = soup.title.string if soup.title else "No title found"
        title_score = 10 if title else 0
        
        # Extract Meta Description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"] if meta_desc else "No description found"
        desc_score = 10 if meta_desc else 0
        
        # Extract Headings
        headings = {f"h{i}": [tag.text.strip() for tag in soup.find_all(f"h{i}")] for i in range(1, 7)}
        headings_score = 10 if any(headings.values()) else 0
        
        # Check for Alt Text in Images
        images = soup.find_all("img")
        images_with_alt = [img for img in images if img.get("alt")]
        image_alt_score = 10 if len(images_with_alt) / len(images) > 0.7 else 0
        
        # Check for Internal & External Links
        links = soup.find_all("a", href=True)
        internal_links = [link for link in links if url in link["href"]]
        external_links = [link for link in links if url not in link["href"]]
        link_score = 10 if internal_links else 0
        
        # Fetch Page Speed Score from Google PageSpeed API
        pagespeed_api = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key=YOUR_API_KEY"
        speed_score = 0
        try:
            speed_response = requests.get(pagespeed_api).json()
            speed_score = speed_response.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", 0) * 100
        except:
            pass
        
        # Calculate Total SEO Score
        seo_score = title_score + desc_score + headings_score + image_alt_score + link_score + (speed_score / 10)
        
        priority_issues = []
        if not title:
            priority_issues.append("Missing title tag - High priority")
        if not meta_desc:
            priority_issues.append("Missing meta description - High priority")
        if not any(headings.values()):
            priority_issues.append("No headings found - Medium priority")
        if not images_with_alt:
            priority_issues.append("Images missing alt text - Low priority")
        if not internal_links:
            priority_issues.append("No internal links found - Medium priority")
        
        return {
            "title": title,
            "description": description,
            "headings": headings,
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "images_with_alt": len(images_with_alt),
            "total_images": len(images),
            "seo_score": seo_score,
            "page_speed_score": speed_score,
            "priority_issues": priority_issues
        }
    except Exception as e:
        return {"error": str(e)}

def generate_pdf(report_html):
    pdf = pdfkit.from_string(report_html, False)
    return BytesIO(pdf)

# Streamlit UI
st.title("Advanced SEO Audit Tool")
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
            
            st.write(f"**Internal Links:** {result['internal_links']}")
            st.write(f"**External Links:** {result['external_links']}")
            st.write(f"**Images with Alt Text:** {result['images_with_alt']} / {result['total_images']}")
            st.write(f"**Page Speed Score:** {result['page_speed_score']}")
            
            st.subheader(f"Overall SEO Score: {result['seo_score']} / 60")
            
            if result['priority_issues']:
                st.subheader("Priority Issues to Fix:")
                for issue in result['priority_issues']:
                    st.write(f"- {issue}")
            
            report_html = f"""
            <h1>SEO Audit Report</h1>
            <p><strong>Title:</strong> {result['title']}</p>
            <p><strong>Meta Description:</strong> {result['description']}</p>
            <p><strong>Internal Links:</strong> {result['internal_links']}</p>
            <p><strong>External Links:</strong> {result['external_links']}</p>
            <p><strong>Page Speed Score:</strong> {result['page_speed_score']}</p>
            <h2>Priority Issues:</h2>
            <ul>
            {''.join(f'<li>{issue}</li>' for issue in result['priority_issues'])}
            </ul>
            """
            pdf = generate_pdf(report_html)
            st.download_button("Download Report as PDF", pdf, "SEO_Audit_Report.pdf", "application/pdf")
    else:
        st.warning("Please enter a valid URL.")
