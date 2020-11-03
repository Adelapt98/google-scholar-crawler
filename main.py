from selenium import webdriver
from time import sleep
import pandas as pd
import math

inputCsv = pd.read_csv('input-csv.csv')

driver = webdriver.Firefox()

df = pd.DataFrame(columns=['id', 'name', 'title', 'profileUrl', 'image', 'homePage', 'researchAreas', 'email',
                           'citationsAll', 'citationsSince2015', 'hIndexAll', 'hIndexSince2015', 'i10IndexAll', 'i10IndexSince2015',
                            'firstArticleDate', 'lastArticleDate', 'articlesCount', 'coAuthorsCount', 'coAuthors'])


# get method
url = 'https://scholar.google.com/citations?view_op=search_authors'

driver.get(url)

def search(title):
    while (True):
        try:
            searchInput = driver.find_element_by_class_name('gs_in_txt')
            a = "arguments[0].setAttribute('value', \'" + title + "\')"
            driver.execute_script(a, searchInput)
            searchInput.submit()
            break
        except:
            if isinstance(title, str) or not math.isnan(float(title)):
                sleep(0.1)
            else:
                searchInput = driver.find_element_by_class_name('gs_in_txt')
                a = "arguments[0].setAttribute('value', \'" + ' ' + "\')"
                driver.execute_script(a, searchInput)
                searchInput.submit()
                break


def getProfileInfo(profileUrl, id):
    i = 0
    sleep(1)
    while True:
        try:
            if i != 0:
                driver.get(profileUrl)
                sleep(3)

            
            #publications
            year = driver.find_element_by_xpath("//span[@id='gsc_a_ha']/a")
            year.click()

            lastArticleDate = driver.find_element_by_xpath("//span[contains(@class, 'gsc_a_h') and contains(@class, 'gsc_a_hc')]").text

            while (True):
                try:
                    artNums = driver.find_element_by_id('gsc_a_nn').text
                except:
                    artNums = len(driver.find_elements_by_class_name('gsc_a_at'))
                showMore = driver.find_element_by_id('gsc_bpf_more')
                if showMore.is_enabled():
                    showMore.click()
                else:
                    try:
                        artNums = driver.find_element_by_id('gsc_a_nn').text
                        artNums = artNums.split('–')[1]
                    except:
                        artNums = len(driver.find_elements_by_class_name('gsc_a_at'))
                    
                    artDates = driver.find_elements_by_class_name('gsc_a_hc')
                    firstArticleDate = ''
                    for date in reversed(artDates):
                        if date.text != '':
                            firstArticleDate = date.text
                            break

                    break

            try:
                viewAll = driver.find_element_by_id('gsc_coauth_opn')
            except:
                viewAll = None

            if viewAll != None:
                viewAll.click()
                sleep(2)
                links = driver.find_elements_by_xpath(
                    "//h3[contains(@class, 'gs_ai_name')]/a")
            else:
                links = driver.find_elements_by_xpath(
                    "//span[contains(@class, 'gsc_rsb_a_desc')]/a")

            coAuthors = []
            for element in links:
                try:
                    linkId = element.get_attribute('href')
                    linkId = linkId.replace('/citations?user=', '')
                    linkId = linkId.replace('=en', '')
                    linkId = linkId.replace('https://scholar.google.com', '')
                    element = {'name': element.text, 'id': linkId}
                except: 
                    pass
                coAuthors.append(element)

            if viewAll != None:
                x = driver.find_element_by_id('gsc_md_cod-x')
                x.click()
                    
            name = driver.find_element_by_id('gsc_prf_in').text  # name
            image = driver.find_element_by_id(
                'gsc_prf_pup-img').get_attribute('src')  # image
            information = driver.find_elements_by_class_name('gsc_prf_il')
            title = information[0].text  # page title
            fields = []  # research fields
            homePageAddress = ''  # university homepage
            email = ''  # verified or not

            for info in information[1:]:

                # get job research fields
                fieldList = info.find_elements_by_class_name('gsc_prf_inta')
                if len(fieldList) > 0:
                    for field in fieldList:
                        fields.append(field.text)

                # get homepage address and email
                else:
                    if 'Homepage' in info.text:
                        homePageAddress = info.find_element_by_class_name(
                            'gsc_prf_ila').get_attribute('href')
                    if 'Verified' in info.text:
                        email = info.text.split('-')[0].strip()

            citations = {'all': 0, 'since2015': 0}
            h_index = {'all': 0, 'since2015': 0}
            i10_index = {'all': 0, 'since2015': 0}

            try:
                citeInfo = driver.find_elements_by_class_name('gsc_rsb_std')
                if len(citeInfo) > 0:
                    citations['all'] = citeInfo[0].text
                    citations['since2015'] = citeInfo[1].text
                    h_index['all'] = citeInfo[2].text
                    h_index['since2015'] = citeInfo[3].text
                    i10_index['all'] = citeInfo[4].text
                    i10_index['since2015'] = citeInfo[5].text

            finally:
                pass


            dic = {'id': id, 'name': name, 'title': title, 'profileUrl': profileUrl, 'image': image, 'homePage': homePageAddress, 'researchAreas': fields, 'email': email,
                'citationsAll': citations['all'], 'citationsSince2015': citations['since2015'], 'hIndexAll': h_index['all'], 'hIndexSince2015': h_index['since2015'], 'i10IndexAll': i10_index['all'], 'i10IndexSince2015': i10_index['since2015']
                , 'firstArticleDate': firstArticleDate,'lastArticleDate': lastArticleDate, 'articlesCount': artNums, 'coAuthorsCount': len(coAuthors), 'coAuthors': coAuthors}

            df.loc[0] = dic
            break

        except Exception as e: 
            print(e)
            i += 1
            continue


df.to_csv('result-dataset.csv', encoding='utf-8', index=False)
fullNames = (inputCsv['name'])
for i in range(0, len(fullNames)):
    nam = fullNames[i]
    search(nam)
    print(i)
    print(nam)
    sleep(3)
    pageCount = 0
    pageLeft = True

    while(pageLeft):
        pageCount = pageCount + 1
        if pageCount == 2:
            break
        links = driver.find_elements_by_xpath(
            "//h3[contains(@class, 'gs_ai_name')]/a")

        for link in links:
            try:
                sleep(1)
                linkUrl = link.get_attribute('href')
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(linkUrl)
                getProfileInfo(linkUrl, i)

                df.to_csv('result-dataset.csv', mode='a',
                        header=False, index=False)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:    
                pass

        try:
            nextPage = driver.find_element_by_class_name('gs_btn_srt')
            disabled = nextPage.get_attribute('disabled')

            if disabled == None:
                pageLeft = True
                nextPage.click()
            else:
                pageLeft = False
        except:
            pageLeft = False


print('\n\n\n')
print(pageCount)

driver.close()
