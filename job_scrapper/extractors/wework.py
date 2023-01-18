from bs4 import BeautifulSoup
import requests

def extract_weworkremotely_jobs(term):
    url = f"https://weworkremotely.com/remote-jobs/search?term={term}"
    request = requests.get(url, headers={"User-Agent": "Kimchi"})
    results = []
    if request.status_code == 200:
        soup = BeautifulSoup(request.text, "html.parser")
        head_positions = soup.find_all("section", class_="jobs")
        for head_position in head_positions:
            jobs = head_position.find_all("li")[:-1]
            for job in jobs:
                link = job.find_all("a")[1]
                company = job.find("span", class_="company")
                location = job.find("span", class_="region company")
                position = job.find("span", class_="title")
                
                if company:
                    company = company.string.strip()
                if position:
                    position = position.string.strip()
                if location:
                    location = location.string.strip()
                if link:
                    link = f"https://weworkremotely.com{link['href']}"
                    
                if company and position and location:
                    job = {
                        'company': company,
                        'position': position,
                        'location': location,
                        'link': link
                    }
                    results.append(job)
        
    else:
        print("Can't get jobs.")
    return results

if __name__ == "__main__": 
    extract_weworkremotely_jobs("rust")