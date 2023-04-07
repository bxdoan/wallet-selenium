import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import os
import urllib.request
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from app_auto import utils
from app_auto.config import get_logger, DRIVER_PATH, PASSWORD, CODE_HOME

logger = get_logger(__name__)

EXTENSION_PATH = os.path.abspath(r"..") + '/metamask_auto/metamask-chrome-10.28.1.crx'
EXTENSION_ID = 'nemfimihgejednjoaiegllipidnpkefe'
EXT_URL = f"chrome-extension://{EXTENSION_ID}/home.html"
POPUP_URL = f"chrome-extension://{EXTENSION_ID}/popup.html"
file_name = f"{CODE_HOME}/account.csv"


def downloadMetamaskExtension():
    print('Setting up metamask extension please wait...')

    url = 'https://xord-testing.s3.amazonaws.com/selenium/10.0.2_0.crx'
    urllib.request.urlretrieve(url, os.getcwd() + '/extension_metamask.crx')


def launchSeleniumWebdriver() -> webdriver:
    print('path', EXTENSION_PATH)
    chrome_options = Options()
    chrome_options.add_extension(EXTENSION_PATH)
    global driver
    driver = webdriver.Chrome(options=chrome_options, executable_path=DRIVER_PATH)
    print("Extension has been loaded")
    return driver


def checkHandles() -> None:
    handles_value = driver.window_handles
    if len(handles_value) > 1:
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        checkHandles()


def metamaskSetup(recoveryPhrase : 'str', password : str) -> None:
    handles_value = driver.window_handles
    if len(handles_value) > 1:
        driver.switch_to.window(driver.window_handles[1])

    driver.switch_to.window(driver.window_handles[1])
    driver.get(f"{EXT_URL}#onboarding/welcome")

    time.sleep(0.1)
    driver.find_element(By.XPATH, '//button[text()="Import an existing wallet"]').click()
    time.sleep(0.1)
    driver.find_element(By.XPATH, '//button[text()="No thanks"]').click()

    time.sleep(0.1)
    inputs = driver.find_elements(By.XPATH, '//input')
    list_of_recovery_phrase = recoveryPhrase.split(" ")
    for i, x in enumerate(list_of_recovery_phrase):
        if i == 0:
            locate_input = i
        else:
            locate_input = i * 2
        phrase = list_of_recovery_phrase[i]
        inputs[locate_input].send_keys(phrase)

    driver.find_element(By.XPATH, '//button[text()="Confirm Secret Recovery Phrase"]').click()
    time.sleep(0.1)

    inputs = driver.find_elements(By.XPATH, '//input')
    inputs[0].send_keys(password)
    inputs[1].send_keys(password)
    driver.find_element(By.CSS_SELECTOR, '.create-password__form__terms-label').click()
    driver.find_element(By.XPATH, '//button[text()="Import my wallet"]').click()

    time.sleep(1)
    driver.find_element(By.XPATH, '//button[text()="Got it!"]').click()
    time.sleep(0.1)
    driver.find_element(By.XPATH, '//button[text()="Next"]').click()
    time.sleep(0.1)
    driver.find_element(By.XPATH, '//button[text()="Done"]').click()
    time.sleep(1)

    print("Wallet has been imported successfully")
    driver.switch_to.window(driver.window_handles[0])


def click(value, time_to_sleep = None, by : By = By.XPATH) -> None:
    if time_to_sleep is None:
        time_to_sleep = 1
    # Click once.
    # If click more times, try another method.
    button = driver.find_element(by, value)
    clicking = ActionChains(driver).click(button)
    clicking.perform()
    time.sleep(time_to_sleep)


def changeMetamaskNetwork(networkName : 'str') -> None:
    # opening network
    print("Changing network")
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(EXT_URL)
    time.sleep(1)

    # Close the popup
    click('//*[@id="popover-content"]/div/div/section/div[2]/div/button')

    # View my account
    click('//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span')

    # Go to settings "Show test networks"
    click('//*[@id="app-content"]/div/div[2]/div/div[1]/div[3]/span/a')

    # click to "Show test networks" in Settings
    click('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/div[7]/div[2]/div/label/div[1]/div[2]/div')

    # click to show "Networks"
    click('//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span')
    print("opening network dropdown")
    time.sleep(1)
    # Ethereum Mainnet
    # Ropsten Test Network
    # Kovan Test Network
    # Rinkeby Test Network
    # Goerli Test Network
    all_li = driver.find_elements(By.TAG_NAME, 'li')

    for li in all_li:
        text = li.text
        if text == networkName:
            li.click()
            print(text, "is selected")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return
    print("Please provide a valid network name")
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)


def addAndChangeNetwork():
    time.sleep(5)
    print("add and change network")
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(EXT_URL)
    # driver.refresh()
    driver.find_element(By.XPATH, "//button[text()='Next']").click()
    driver.find_element(By.XPATH, "//button[text()='Connect']").click()
    time.sleep(1)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def changeNetworkByChainList(network_name : 'str') -> None:
    """
    ref. Chainlist.org

    :Args:
        - network_name: string.

    :Usage:
        auto.changeNetworkByChainList('Binance Smart Chain Mainnet')
    """
    time.sleep(2)
    print("change network by chainlist")
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[1])
    driver.get('https://chainlist.org/')
    time.sleep(4)
    driver.find_element(By.XPATH, "//button[text()='Connect Wallet']").click()
    # connect chainlist
    time.sleep(2)
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[2])
    driver.get(POPUP_URL)
    time.sleep(3)
    driver.find_element(By.XPATH, '//button[text()="Next"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[text()="Connect"]').click()
    time.sleep(3)
    driver.close()
    driver.switch_to.window(driver.window_handles[1])
    # search Network in include testnets
    driver.find_element(By.XPATH, "//span[text()='Include Testnets']").click()
    time.sleep(2)
    inputs = driver.find_elements(By.XPATH, '//input')
    inputs[0].send_keys(network_name)
    time.sleep(4)
    driver.find_element(By.XPATH, "//button[text()='Add to Metamask']").click()
    # change Network
    time.sleep(2)
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[2])
    driver.get(EXT_URL)
    time.sleep(3)
    driver.find_element(By.XPATH, "//button[text()='Approve']").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[text()='Switch network']").click()
    time.sleep(3)
    driver.close()
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(network_name, "is selected")


def connectToWebsite():
    time.sleep(1)

    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get(POPUP_URL)
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    time.sleep(2)
    click('//button[text()="Next"]', 2)
    click('//button[text()="Connect"]', 3)
    logger.info('Site connected to metamask')
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def confirmApprovalFromMetamask():
    time.sleep(5)
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get(POPUP_URL)
    click('//button[text()="Confirm"]', 2)
    logger.info("Approval transaction confirmed")

    driver.close()
    # switch back
    driver.switch_to.window(driver.window_handles[0])


def rejectApprovalFromMetamask():
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get(POPUP_URL)
    time.sleep(1)
    # confirm approval from metamask
    driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[4]/footer/button[1]').click()
    time.sleep(1)
    print("Approval transaction rejected")

    # switch to dafi
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(3)
    print("Reject approval from metamask")


def confirmTransactionFromMetamask():
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get(POPUP_URL)
    time.sleep(1)

    # # confirm transaction from metamask
    driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/div[3]/footer/button[2]').click()
    time.sleep(13)
    print("Transaction confirmed")

    # switch to dafi
    driver.switch_to.window(driver.window_handles[0])

    time.sleep(3)


def rejectTransactionFromMetamask():
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get(POPUP_URL)
    time.sleep(5)
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    time.sleep(5)
    # confirm approval from metamask
    driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/div[3]/footer/button[1]').click()
    time.sleep(2)
    print("Transaction rejected")

    # switch to web window
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(3)


def addToken(tokenAddress):
    # opening network
    print("Adding Token")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(EXT_URL)
    print("closing popup")
    time.sleep(5)
    driver.find_element(By.XPATH, '//*[@id="popover-content"]/div/div/section/header/div/button').click()

    # driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span').click()
    # time.sleep(2)

    print("clicking add token button")
    driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[4]/div/div/div/div[3]/div/div[3]/button').click()
    time.sleep(2)
    # adding address
    driver.find_element("id", "custom-address").send_keys(tokenAddress)
    time.sleep(10)
    # clicking add
    driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[4]/div/div[2]/div[2]/footer/button[2]').click()
    time.sleep(2)
    # add tokens
    driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[4]/div/div[3]/footer/button[2]').click()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(3)


def signConfirm():
    time.sleep(5)
    checkHandles()
    time.sleep(1)

    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get(POPUP_URL)
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    time.sleep(5)
    while True:
        try:
            element = driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[3]/div[1]')
        except NoSuchElementException:
            time.sleep(1)
            print('签名了，但没有完全签名')
            break
        else:
            driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[2]/div/div[3]/div[1]').click()
            driver.find_element(By.XPATH, '//button[text()="签名"]').click()
            time.sleep(1)
            print('签名完成')
            break
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def signReject():
    print("sign")
    time.sleep(3)

    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    driver.get(POPUP_URL)
    time.sleep(5)
    driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
    time.sleep(3)
    driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/button[1]').click()
    time.sleep(1)
    # driver.find_element(By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
    # time.sleep(3)
    print('Sign rejected')
    print(driver.window_handles)
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(3)


def create_wew_wallet():
    mn = addr = private_key = ''

    return mn, addr, private_key


def create_account():
    mns = pd.DataFrame(columns=["Name", "Address", "Private Key", "Seed Phrase",
                                "Password", "Status", "Description"])
    time.sleep(3)
    walletLength = 10

    for i in range(0, walletLength):
        mn, addr, private_key = create_wew_wallet()
        mns.loc[len(mns)] = [f"air {i}", addr, private_key, mn, PASSWORD, 'active', '']
        utils.add_to_csv(file_name, mns.loc[i])


if __name__ == '__main__':
    driver = launchSeleniumWebdriver()
    for i in range(0, 1):
        try:
            create_account()
            # create_pack(driver)
        except Exception as e:
            logger.info(e)
            driver.quit()
            driver = launchSeleniumWebdriver()
            continue
