from selenium import webdriver

inject_js_str = open('/home/maghsk/storage/Projects/WebGL Empirical Study/Crawler/2_selenium_crawler/inject.js', 'rt').read()

browser = webdriver.Chrome()
browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': inject_js_str})

browser.get('https://www.oppo.com/cn/smartphones/series-find-n/find-n/3d/')

output = browser.execute_script('return capturedWebGLFunctions;')
print(output)