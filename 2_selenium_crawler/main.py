from seleniumwire import webdriver
import selenium.common
import json
import logging
import gzip

PROXY = "socks5://ss.maghsk.site:3535"

def main():
    url_list = [
        'https://www.oppo.com/cn/smartphones/series-find-n/find-n/3d/',
        'https://webglsamples.org/aquarium/aquarium.html',
    ]
    inject_js_str = open('inject.js', 'rt').read()

    options = webdriver.ChromeOptions()
    options.add_argument(f'--proxy-server={PROXY}')
    browser = webdriver.Chrome(options=options)
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': inject_js_str})
    browser.implicitly_wait(30.0)
    browser.set_page_load_timeout(30.0)

    for url in url_list:
        url_id = url.split('/')[2]
        output = get_captured_webgl_functions(browser, url)

        with gzip.open(f'../output/{url_id}-capturedWebGLFunctions.json.gz', 'wt') as fp:
            fp.write(output)

    browser.close()

    # captured = json.loads(output)
    # browser.execute_script('window.stop();')
    # with gzip.open(f'../output/{url_id}-capturedWebGLFunctions.pkl.gz', 'wb') as fp:
    #     pickle.dump(captured, fp)

def get_captured_webgl_functions(browser, url) -> str:
    try:
        browser.get(url)
    except selenium.common.exceptions.TimeoutException as e:
        logging.info('TimeoutException when loading url: %s', url)
    return browser.execute_script('return getJSONCapturedWebGLFunctions();')


if __name__ == '__main__':
    main()