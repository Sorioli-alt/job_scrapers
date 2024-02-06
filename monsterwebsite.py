from playwright.async_api import Browser
import csv
import time
from datetime import datetime

class MonsterWebsite():
    # URLs for different job roles on Monster.
    DATA_ANALYST_JOBS = 'https://www.monster.com/jobs/q-data-analyst-jobs?page=1&so=p.h.p'
    DATA_SCIENTIST_JOBS = 'https://www.monster.com/jobs/search?q=data+scientist&where=&page=1&so=m.s.sh'
    BUSINESS_ANALYST_JOBS = 'https://www.monster.com/jobs/search?q=business+analyst&where=&page=1&so=m.s.sh'
    DATA_ENGINEER_JOBS = 'https://www.monster.com/jobs/search?q=data+engineer&where=&page=1&so=m.s.sh'
    ML_ENGINEER_JOBS = 'https://www.monster.com/jobs/search?q=Machine+Learning+Engineer&where=&page=1&so=p.s.sh'

    def __init__(self, url):
        self._url = url

    def get_url(self):
        return self._url

    async def scroll_page(self, page):
        while not await page.locator("button:has-text('No More Results')").is_visible():
            await page.wait_for_timeout(2000)
            await page.evaluate('''() => {
                const internalScrollElement = document.querySelector('#card-scroll-container');
                internalScrollElement.scrollTop += 200;
            }''')

    async def scrape(self, browser: Browser):
        # 'jobs_list' is a list containing dictionaries, each representing a job with its respective features
        jobs_list = []

        time.sleep(20)
        # Opening a new page in the browser
        page = await browser.new_page()
        url = self.get_url()
        print(f"Scraping URL: {url}")

        # Navigate to the specified URL
        await page.goto(url, timeout=90000)
        await page.wait_for_load_state('load', timeout=10000)

        job_title_selector = 'xpath=/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[1]/div/div/div/div/div/ul/li/div/article/div[2]/div[1]/h3/a'
        await page.wait_for_selector(job_title_selector)

        await self.scroll_page(page)

        jobs_indices_used = []

        job_card_selector = '[data-test-id^="svx-job-card-component-"]'
        job_cards = await page.locator(job_card_selector).element_handles()
        job_count = len(job_cards)

        variable_name = next(key for key, value in vars(MonsterWebsite).items() if value == self.get_url())
        today_date = datetime.today().strftime('%Y-%m-%d')

        for job_index in range(job_count):
            job_features = {}

            if job_index not in jobs_indices_used:
                job_box = '[data-test-id=\'svx-job-card-component-'
                job_box_selector = job_box + str(job_index) + "']"
                await page.locator(job_box_selector).click()
                await page.wait_for_timeout(3000)

                h3_element = page.locator(job_title_selector).nth(job_index)
                title_text = await h3_element.text_content()
            
                job_features['title'] = title_text

                company_selector = 'xpath=/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[1]/div/div/div/div/div/ul/li/div/article/div[2]/div[1]/h3/span'
                company_element = page.locator(company_selector).nth(job_index)
                company_text = await company_element.text_content()
                
                job_features['company'] = company_text

                location_selector = 'xpath=/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[1]/div/div/div/div/div/ul/li/div/article/div[2]/div[1]/div/span[1]'
                location_element = page.locator(location_selector).nth(job_index)
                location_text = await location_element.text_content()

                job_features['location'] = location_text

                image_xpath = 'xpath=/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[2]/div/div[2]/div[1]/img'
                image_exists = await page.locator(image_xpath).count() > 0

                if image_exists:
                    job_description_selector = 'xpath=/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[2]/div/div[2]/div[2]/div'
                    job_description = await page.locator(job_description_selector).inner_text()
                else:
                    job_description_selector = 'xpath=/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[2]/div/div[2]/div[1]/div/div[1]'
                    job_description = await page.locator(job_description_selector).inner_text()

            job_features['job_description'] = job_description
            search_term = variable_name[:-5]
            job_features['search_term'] = search_term
            job_features['date'] = today_date

            jobs_list.append(job_features)
            jobs_indices_used.append(job_index)
            
        file_name = f'jobs_list.csv'
        field_names = ['title','company','location','job_description','search_term','date']
        with open(file_name,'a',newline='',encoding='utf-8') as csvfile:
            # Check if the file is empty, write the header only if it is
            is_file_empty = csvfile.tell() == 0
            writer = csv.DictWriter(csvfile,fieldnames=field_names)
            
            if is_file_empty:
                writer.writeheader()

            writer.writerows(jobs_list)
        await page.close()
