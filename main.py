import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

def main():
    keywords = "Help+Desk"
    location = "United+States"

    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&start=0"

    req = requests.get(url)

    if req.status_code == 200:

        html = req.text

        df = pd.DataFrame({
            "Job_Title": [],
            "Company_Name": [],
            "Location": [],
            "Time_Passed": [],
            "Link": [],
            "Company_Profile_Link": []
        })

        # job scraping
        df, msg = scrap_linkedin_jobs_page(html, df)
        print(msg)

        # Write scrap jobs to a CSV file
        df.to_csv("data/linkedin_jobs.csv", index=False)


def scrap_linkedin_jobs_page(html: str, df: pd.DataFrame):
    """LinkedIn Job Scraping"""

    soup = BeautifulSoup(html, "lxml")

    li_tags = soup.find_all("li")

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename="logs/scrap_jobs.log",
        filemode="w",
        encoding="utf-8",
        level=logging.DEBUG
    )

    job_count = 0
    for li_tag in li_tags:
        a_tag = li_tag.find("a", {"class", "base-card__full-link"})
        
        link = "N/A"
        if a_tag != None:
            link = a_tag.get("href")

        h3_tag = li_tag.find("h3", {"class", "base-search-card__title"})
        
        job_title = "N/A"
        if h3_tag != None:
            job_title = h3_tag.get_text()
            job_title = job_title.strip()
        
        company_name = "N/A"
        company_profile_link = "N/A"
        h4_tag = li_tag.find("h4", {"class", "base-search-card__subtitle"})
        if h4_tag != None:
            company_name = h4_tag.get_text()
            company_name = company_name.strip()

            a_tag = h4_tag.find("a", {"class", "hidden-nested-link"})
            company_profile_link = a_tag.get("href")

        div_metadata_tag = li_tag.find("div", {"class", "base-search-card__metadata"})

        location = "N/A"
        time_passed = "N/A"
        if div_metadata_tag != None:
            span_location_tag = div_metadata_tag.find("span", {"class", "job-search-card__location"})
        
            if span_location_tag != None:
                location = span_location_tag.get_text()
                location = location.strip()
        
            time_tag = div_metadata_tag.find("time", {"class", "job-search-card__listdate"})
        
            if time_tag != None:
                time_passed = time_tag.get_text()
                time_passed = time_passed.strip()
        
        logger.debug(f"Job Title: {job_title}")
        logger.debug(f"Company Name: {company_name}")
        logger.debug(f"Location: {location}")
        logger.debug(f"Time Passed: {time_passed}")
        logger.debug(f"Link {link}")
        logger.debug(f"Company Profile Link: {company_profile_link}\n")

        job_box_data = pd.DataFrame({
            "Job_Title": [job_title],
            "Company_Name": [company_name],
            "Location": [location],
            "Time_Passed": [time_passed],
            "Link": [link],
            "Company_Profile_Link": [company_profile_link]
        })


        df = pd.concat([df, job_box_data], ignore_index=True)
        job_count += 1

    print(f"Scraped {job_count} jobs")

    return df, "Success"

if __name__ == "__main__":
    main()