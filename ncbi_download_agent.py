import os
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select


specias_list = ["Photobacterium jeanii"]#full the list with the specias' name as the sample structure
URL = "https://www.ncbi.nlm.nih.gov/assembly/?term="
USER_AGENT = 'user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"' 
PREF = {"download.default_directory": os.getcwd(), "profile.default_content_setting_values.automatic_downloads":1}

def decrator(*kwg):
    def countor(func):
        num = 1
        lenth = len(kwg)
        for ite in kwg:
            func(ite)
            print( "{:05.3%}".format( float(num/lenth) ), flush=True)
            num += 1
    return countor

def check_download_state(path):
    while True:
        for root, dirs, files in os.walk(path):
            files = [f for f in files if not f[0] == '.']
            for file in files:
                if '.crdownload' in file:
                    time.sleep(0.5)
                    continue
        return True

@decrator(*specias_list)
def Chrome_operator(ite):
    options = webdriver.ChromeOptions()
    options.add_argument(USER_AGENT)
    options.add_experimental_option('prefs', PREF)
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(URL+ite)
    time.sleep(1)
    if '?term=' in driver.current_url:
        elems = driver.find_elements_by_xpath("//div[@class='rprt']")
        elems_lenth = len(elems)
        elem_num = 0
        for elem in elems:
            detail = elem.find_element_by_xpath(".//dl[@class='details'][5]").text
            if detail == 'Assembly level: Complete Genome':
                driver.execute_script('arguments[0].scrollIntoView();', elem)
                nextpage = elem.find_element_by_xpath(".//p[@class='title']/a")
                nextpage.click()
                time.sleep(1)
                break
            else:
                elem_num += 1
            if elem_num == elems_lenth:
                driver.execute_script('arguments[0].scrollIntoView();', elems[0])
                nextpage = elems[0].find_element_by_xpath(".//p[@class='title']/a")
                nextpage.click()
                time.sleep(1)
                break
    try_time = 1
    while True:
        try:
            download_button_1 = driver.find_element_by_xpath("//h4[@id='download-asm']")
            download_button_1.click()
            time.sleep(try_time)
            selection = Select(driver.find_element_by_xpath("//select[@id='dl_assembly_gbrs']"))
            selection.select_by_value("GenBank")
            selection = Select(driver.find_element_by_xpath("//select[@id='dl_assembly_file_types']"))
            selection.select_by_value("GENOME_FASTA")
        except Exception as e:
            try_time += 1
            print("Exception %s"%e)
            print("try %d times"%try_time-1)
        else:
            break
    download_button_2 = driver.find_element_by_xpath("//button[@id='dl_assembly_download']")
    download_button_2.click()
    time.sleep(5)
    if check_download_state(os.getcwd()):
        try_time = 0
        while True:
            try:
                os.rename(os.path.join(os.getcwd(),'genome_assemblies_genome_fasta.tar'),os.path.join(os.getcwd(),ite.replace(' ','_')+'.tar'))
            except Exception as e:
                print("download fall "+ ite)
                break
            else:
                break
    driver.quit()

Chrome_operator

