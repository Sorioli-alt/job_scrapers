from playwright.async_api import Browser
from playwright.async_api import async_playwright
import csv
class MonsterWebsite():
    DATA_ANALYST_JOBS = 'https://www.monster.com/jobs/search?q=Data+Analyst&where=&page=1&so=m.s.sh'
    DATA_SCIENTIST_JOBS = 'https://www.monster.com/jobs/search?q=data+scientist&where=&page=1&so=m.s.sh'
    BUSINESS_ANALYST_JOBS = 'https://www.monster.com/jobs/search?q=business+analyst&where=&page=1&so=m.s.sh'
    DATA_ENGINEER_JOBS = 'https://www.monster.com/jobs/search?q=data+engineer&where=&page=1&so=m.s.sh'

    _BASE_URL = 'https://www.monster.com'

    def __init__(self, url):
        self._url = url

    def get_url(self):
        return self._url
    
    async def scrape(self, browser: Browser):
        jobs_list = []
        page = await browser.new_page()
        url = self.get_url()
        print(f"Scraping URL: {url}")
        await page.goto(url, timeout=90000)
        await page.wait_for_load_state('load', timeout=10000)

        async def scroll_page(page):
            await page.evaluate('''() => {
                const internalScrollElement = document.querySelector('#card-scroll-container');
                if (internalScrollElement) {
                internalScrollElement.scrollTop += 200;
                }
            }''')


        while not await page.locator("button:has-text('No More Results')").is_visible():
            await scroll_page(page)

        # while not await page.locator("button:has-text('No More Results')").is_visible():
        #     await page.evaluate('''() => {
        #         const internalScrollElement = document.querySelector('#card-scroll-container');
        #         internalScrollElement.scrollTop += 200;
        #     }''')
        job_title_selector = 'xpath=/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[1]/div/div/div/div/div/ul/li/div/article/div[2]/div[1]/h3/a'
        
        await page.locator('div#JobCardGrid').click()
        while await page.locator("button",has_text="No More Results").is_visible() is False:
            await page.mouse.wheel(0,200)

        await page.wait_for_selector(job_title_selector)
        joblist = page.locator(job_title_selector)
        
        count = await joblist.count()
        print(count)

        for job_index in range(count):
            try:
                job_features = {}

                job_box = '[data-test-id=\'svx-job-card-component-'
                job_box_selector = job_box + str(job_index) + "']"
                await page.locator(job_box_selector).click()

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
                    #xpath=/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[2]/div/div[2]/div[2]/div/div
                    #/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[2]/div/div[2]/div[2]/div
                    job_description = await page.locator(job_description_selector).inner_text()
                else:
                    job_description_selector = 'xpath=/html/body/div[1]/div[2]/main/div[3]/nav/section[1]/div[2]/div[2]/div/div[2]/div[1]/div/div[1]'
                    job_description = await page.locator(job_description_selector).inner_text()

                
                job_features['job_description'] = job_description
                jobs_list.append(job_features)
            except Exception as ex:
                print(ex)
        
        field_names = ['title','company','location','job_description']
        with open('jobs_list.csv','w') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=field_names)
            writer.writeheader()
            writer.writerows(jobs_list)
        await page.close()