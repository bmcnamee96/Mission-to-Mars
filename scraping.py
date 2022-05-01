# import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        'hemi_info': hemisphere(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def hemisphere(browser):
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []
    hemisphere_titles = []

    # code to retrieve the image urls
    mars_html = browser.html
    mars_soup = soup(mars_html, 'html.parser') 
    mars_pic = mars_soup.find_all('div', class_='item')
    for pic in mars_pic:
        mars_img_url_rel = pic.find('img', class_='thumb').get('src')
        mars_img_url = f'{url}{mars_img_url_rel}'
        hemisphere_image_urls.append(mars_img_url)

    # code to retrieve the titles
    mars_desc = mars_soup.find_all('div', class_='description')
    for desc in mars_desc:
        mars_title = desc.a.get_text(strip=True)
        hemisphere_titles.append(mars_title)

    # create a dictionary to hold the scraped info
    hemi_info = {}
    keys = hemisphere_titles
    values = hemisphere_image_urls

    # iterate through the keys to line up all the values
    for i in keys:
        for x in values:
            hemi_info[i] = x

    return hemi_info

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())