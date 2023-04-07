import os
import pandas as pd
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from app_auto import utils
from app_auto.config import CODE_HOME, PASSWORD, HEADLESS, get_logger, DRIVER_PATH

logger = get_logger(__name__)


# Any password with one upper letter and length>8.
password = PASSWORD
# File name to save the memories and addresses.
# xxx.csv.
file_name = f"{CODE_HOME}/account.sui2.csv"

EXTENSION_ID = 'opcgpfmipidbgpenhmajoajpbobppdil'
EXT_URL = f"chrome-extension://{EXTENSION_ID}/home.html"
EXTENSION_FILE_NAME = "sui_23.3.31.2.crx"
CUSTOM_RPC = "https://explorer-rpc.testnet.sui.io"




def conWallet(driver):
    # switch to new window
    switch_to_window(driver, -1)

    # click to Connect button
    click(driver, '//div[text()="Connect"]', 5)

    # switch to first window
    switch_to_window(driver, 0)


def approve(driver):
    # switch to new window
    time.sleep(5)  # wait for page load
    switch_to_window(driver, -1)

    # click to Connect button
    click(driver, '//div[text()="Approve"]', 10)  # wait for page load

    # switch to first window
    switch_to_window(driver, 0)


def reject(driver):
    # switch to new window
    time.sleep(5)  # wait for page load
    switch_to_window(driver, -1)

    # click to Connect button
    click(driver, '//div[text()="Reject"]', 10)

    # switch to first window
    switch_to_window(driver, 0)


def click(driver, xpath, time_to_sleep = None) -> None:
    if time_to_sleep is None:
        time_to_sleep = 1
    # Click once.
    # If click more times, try another method.
    button = driver.find_element(By.XPATH, xpath)
    # logger.info('click on "' + button.text + '"')
    clicking = ActionChains(driver).click(button)
    clicking.perform()
    time.sleep(time_to_sleep)


def new_window(driver, url):
    # Create a new window by the url.
    # Remember to switch to the new window!
    driver.execute_script('window.open("'+url+'")')


def switch_to_window(driver, window_number):
    # Switch to another window, start from 0.
    driver.switch_to.window(driver.window_handles[window_number])
    logger.info(f'switched to window numer: {str(window_number)}')


def input_text(driver, xpath, text):
    key = driver.find_element(By.XPATH, xpath)
    key.send_keys(text)


def create_driver():
    # New a driver with extension sui_wallet.
    option = webdriver.ChromeOptions()
    pf = os.path.abspath(os.path.dirname(__file__))
    option.add_extension(f"{pf}/{EXTENSION_FILE_NAME}")

    # add headless option
    if utils.force2bool(HEADLESS):
        logger.info('headless mode')
        option.add_argument('--headless')

    driver = webdriver.Chrome(options=option, executable_path=DRIVER_PATH)
    # driver.maximize_window()
    time.sleep(3)  # wait for extension load
    return driver


def create_new_wallet_window(driver : webdriver.Chrome, url : str = EXT_URL):
    # Create a new window and switch to it.
    new_window(driver, url)
    switch_to_window(driver, 1)
    driver.close()
    time.sleep(5)
    switch_to_window(driver, 1)
    try:
        log_out(driver)
    finally:
        return


def set_wallet_sleep_time(driver : webdriver.Chrome):
    # The wallet will lock after 5 minutes, change it to 30 minutes(max).
    click(driver, "/html/body/div/div/div[1]/header/div[3]/a")
    click(driver, '//div[text()="Auto-lock"]')

    # Delete default "5" and set the number to 30.
    inputs = driver.find_elements(By.XPATH, '//input')
    inputs[0].click()
    inputs[0].send_keys(Keys.DELETE)
    inputs[0].send_keys("30")
    click(driver, '//div[text()="Save"]')
    click(driver, "/html/body/div/div/div/div[1]/a[2]", 0)


def get_private_key(driver : webdriver.Chrome, account : dict) -> str:
    private_key = ''
    # Get the private key of the wallet.

    # Click the "Settings" button.
    click(driver, "/html/body/div/div/div[1]/header/div[3]/a")

    # Click the "Accounts" button.
    click(driver, '//div[text()="Accounts"]', 4)

    # Click the "Export" button.
    # The address is too long, so we use the short address.
    # The short address is like "0x2cc0…33a4".
    # format short address is first 6 and last 4.
    short_add = account['address'][:6] + "…" + account['address'][-4:]
    click(driver, f'//div[text()="{short_add}"]', 4)

    click(driver, '//div[text()="Export Private Key"]', 2)

    # Insert password to show private key.
    inputs = driver.find_elements(By.XPATH, '//input')
    inputs[0].send_keys(password)
    click(driver, '//div[text()="Continue"]', 8)  # MUST wait for the private key to show.

    # Show the private key.
    button_list = driver.find_elements(By.XPATH, '//button')
    # skip the first button and all the buttons after the first button.
    for button in button_list[1:]:
        button.click()
    time.sleep(2)

    # Get the private key.
    try:
        private_key = driver.find_element(
            By.XPATH, "/html/body/div/div/div[1]/div/div/div[2]/div/div[2]/div[1]/div[1]/div").text
    except:
        logger.info(f"Can't get private key {account['address']}.")

    # Close the window.
    click(driver, "/html/body/div/div/div[1]/header/div[3]/a")
    return private_key


def log_in(driver, mnemonic):
    # Log in an account with mnemonic.
    click(driver, '/html/body/div/div/div[1]/div/div/div[2]/a', 2)
    click(driver, "/html/body/div/div/div[1]/div[2]/a", 1)

    inputs = driver.find_elements(By.XPATH, '//input')
    list_of_recovery_phrase = mnemonic.split(" ")
    for i, x in enumerate(list_of_recovery_phrase):
        phrase = list_of_recovery_phrase[i]
        inputs[i].send_keys(phrase)

    click(driver, "/html/body/div/div/div[1]/div[3]/form/div/button", 0)

    # input password
    input_text(driver,
               "/html/body/div/div/div[1]/div[3]/form/label[1]/div[2]/input", password)
    input_text(driver,
               "/html/body/div/div/div[1]/div[3]/form/label[2]/div[2]/input", password)
    click(driver, "/html/body/div/div/div/div[3]/form/div[2]/button[2]", 1)
    click(driver, "/html/body/div/div/div/div[3]/a", 5)
    # After logging in, it can take a while for the page to reload.


def log_out(driver: webdriver.Chrome) -> None:
    # Log out an account.
    click(driver, "/html/body/div/div/div/div[1]/a[2]", 0)
    click(
        driver, "/html/body/div/div/div/div[2]/div/div[2]/div/a[1]/div[2]", 0)
    # After logging out, it can take a while for the page to reload.
    click(driver, "/html/body/div/div/div/div[2]/div/div[2]/div/button", 5)


def log_out_after_create(driver: webdriver.Chrome) -> None:
    # Log out an account.
    click(driver, "/html/body/div/div/div[1]/header/div[3]/a")
    click(driver, '//div[text()="Logout"]')
    click(driver, "/html/body/div[2]/div/div/div/div[2]/div/div[3]/div/div[2]/button/div", 5)


def create_wew_wallet(driver):
    # Create a new wallet.
    click(driver, '/html/body/div/div/div/div/div/div[2]/a', 0)
    click(driver, "/html/body/div/div/div/div[1]/a", 0)
    # Input any password.
    input_text(
        driver, "/html/body/div/div/div/form/div/fieldset/label[1]/div[2]/input", password)
    input_text(
        driver, "/html/body/div/div/div/form/div/fieldset/label[2]/div[2]/input", password)
    click(
        driver, "/html/body/div/div/div/form/div/fieldset/label[3]/span[1]", 0)
    click(driver, "/html/body/div/div/div/form/button", 1)
    # Get mnemonic.
    button_list = driver.find_elements(By.XPATH, '//button')
    button_list[0].click()
    mnemonic = driver.find_element(
        By.XPATH, "/html/body/div/div/div/div[3]/div[1]/div[3]/div[1]/div[1]/div").text
    mnemonic = str.replace(mnemonic, "COPY", "")
    mnemonic = str.replace(mnemonic, "\n", "")
    click(driver, "//div[text()='I saved my recovery phrase']")
    click(driver, '//div[text()="Open Sui Wallet"]')

    # Get the address.
    # The address shown in the wallet is not complete. Use blockscan link to read the address.
    # driver.find_element(By.XPATH, '//a[text()="Apps"]').click()
    click(driver, "/html/body/div/div/div[1]/div/nav/div[2]/a[3]")
    full_addr = driver.find_element(
        By.XPATH, "/html/body/div/div/div[1]/div/main/div/div/section/div/div[1]/a").get_attribute("href")
    # Do not understand why, link length is not constant.
    full_addr = str.replace(full_addr, "https://explorer.sui.io/address/", "")
    # first 66 characters are the address.

    addr = full_addr[:66]

    # get private key.
    private_key = get_private_key(driver, account={'address': addr})

    return mnemonic, addr, private_key


def send_SUI(driver, sendAmount, receiver):
    # If sent successfully, return True, else return False.
    try:
        click(driver, "/html/body/div/div/div/div[2]/nav/div[2]/a[1]/i", 0)
        click(
            driver, "/html/body/div/div/div/div[2]/main/div/div[2]/a[2]/div/i", 0)
        input_text(
            driver, "/html/body/div/div/div/div[2]/main/div/div[2]/form/div[1]/div[1]/input", sendAmount)
        # Continue. If insufficient, button will be grey.
        click(
            driver, "/html/body/div/div/div/div[2]/main/div/div[2]/form/div[2]/div/button", 0)
        # Fill in address.
        input_text(
            driver, "/html/body/div/div/div/div[2]/main/div/div[2]/form/div[1]/div[2]/div[1]/div[1]/textarea", receiver)
        # Send, may take a while. WAIT.
        click(
            driver, "/html/body/div/div/div/div[2]/main/div/div[2]/form/div[2]/div/button", 20)
        try:
            # There are two types of tx result. Sent successful window may not pop up.
            click(driver, "/html/body/div/div/div/div[2]/main/div/button/i", 0)
            return True
        except:
            return True
    except:
        return False


def SwitchToTestNet(driver):
    # Switch to test net.
    click(driver, "/html/body/div/div/div/div[1]/a[2]/span[3]", 0)
    click(
        driver, "/html/body/div/div/div/div[2]/div/div[2]/div/a[2]/div[2]", 0)
    click(
        driver, "/html/body/div/div/div/div[2]/div/div[2]/div/div[2]/ul/li[4]/button", 0)
    click(driver, "/html/body/div/div/div/div[1]/a[2]/span[1]", 0)
    # May take a while to switch to test net. WAIT.
    click(driver, "/html/body/div/div/div/div[2]/nav/div[2]/a[1]/i", 10)


def request_faucet(driver : webdriver.Chrome):
    click(driver, "/html/body/div/div/div[1]/header/div[3]/a", 5)
    # click the request button in settings.
    click(driver, '//div[text()="Request Testnet SUI Tokens"]', 5)
    # Close the window.
    click(driver, "/html/body/div/div/div[1]/header/div[3]/a", 5)
    try:
        # click the request button in main page if has.
        click(driver, '//div[text()="Request Testnet SUI Tokens"]', 5)
    except:
        pass


def change_rpc(driver : webdriver.Chrome):
    click(driver, "/html/body/div/div/div[1]/header/div[3]/a", 2)
    # click the request button in settings.
    click(driver, '//div[text()="Network"]', 2)
    # Close the window.
    click(driver, "/html/body/div/div/div[1]/div/div/div[2]/div/ul/li[4]/button", 4)
    try:
        inputs = driver.find_elements(By.XPATH, '//input')
        inputs[0].click()
        inputs[0].send_keys(CUSTOM_RPC)
        inputs[0].submit()
        time.sleep(2)
    except:
        pass

    click(driver, "/html/body/div/div/div[1]/header/div[3]/a", 3)


def get_balance(driver : webdriver.Chrome) -> str:
    # Get balance.
    balance = ""
    try:
        balance = driver.find_element(
            By.XPATH, "/html/body/div/div/div[1]/div/main/div/div[1]/div/div/span[1]").text
    except:
        pass
    balance = str.replace(balance, "SUI", "")
    balance = str.replace(balance, " ", "")
    balance = utils.force_float(balance)
    logger.info(f"Balance: {balance}")
    return balance


def try_find(driver : webdriver.Chrome, xpath="", by=By.XPATH):
    try:
        return driver.find_element(by, xpath)
    except:
        return None


def try_finds(driver : webdriver.Chrome, xpath="", by=By.XPATH):
    try:
        return driver.find_elements(by, xpath)
    except:
        return []


def stack_sui(driver : webdriver.Chrome, validator = '', amount=1) -> str:
    time.sleep(5)
    button_current = try_find(driver, '//div[text()="Currently Staked"]')
    button_new_stack = try_find(driver, '//div[text()="Stake & Earn SUI"]')

    if button_current:
        try:
            button_current.click()
            time.sleep(3)

            click(driver, f'//div[text()="{validator}"]', 3)

            click(driver, '//div[text()="Stake SUI"]', 3)
        except:
            pass
    elif button_new_stack:
        try:
            button_new_stack.click()
            time.sleep(3)

            click(driver, f'//div[text()="{validator}"]', 3)
            click(driver, f'//div[text()="Select Amount"]', 3)
        except:
            pass

    try:
        # input stake amount
        inputs = try_finds(driver, '//input')
        inputs[0].send_keys(f"{amount}")

        click(driver, f'//div[text()="Stake Now"]', 3)

        # confirm
        button = try_finds(driver, '//button')
        button[0].click()

        time.sleep(10)  # wait for tx to be mined
    except:
        pass



def MintTestToken(driver : webdriver.Chrome):
    click(driver, "/html/body/div/div/div/div[2]/nav/div[2]/a[1]", 1)
    SwitchToTestNet(driver)

    click(driver, "/html/body/div/div/div/div[2]/main/div/div[4]/button", 0)
    # Try for at most 5 minutes.
    # You can add the time to up to 30 minutes, or the wallet will fall asleep.
    for i in range(0, 30):
        time.sleep(10)
        balance = driver.find_element(
            By.XPATH, "/html/body/div/div/div/div[2]/main/div/div[1]/div/div/span[1]").text
        if balance != "0":
            break
        logger.info("balance still 0")
    # Now you should have got the test token. Return whether minted successfully.
    # True for success, False for fail.
    return balance != "0"


def mint_threeNFTs(driver):
    click(driver, "/html/body/div/div/div/div[2]/nav/div[2]/a[3]", 1)
    # Mint nfts. WAIT.
    click(
        driver, "/html/body/div/div/div/div[2]/main/div/div/section/div/div[1]/button", 5)
    click(
        driver, "/html/body/div/div/div/div[2]/main/div/div/section/div/div[1]/button", 5)
    click(
        driver, "/html/body/div/div/div/div[2]/main/div/div/section/div/div[1]/button", 5)


def create_pack(driver : webdriver.Chrome) -> None:
    create_new_wallet_window(driver)
    # mns = pd.DataFrame(columns=["mnemonic", "addr"])
    mns = pd.DataFrame(columns=["Name", "Address", "Private Key", "Seed Phrase",
                                "Password", "Status", "Description"])
    # Max 10.
    # After 10 wallets, the balance will be 0.00001, not enough for minting nfts.
    walletLength = 1

    # Create wallets first and save in dataframe.
    for i in range(0, walletLength):
        mn, addr, private_key = create_wew_wallet(driver)
        mns.loc[len(mns)] = [f"air {i}", addr, private_key, mn, password, 'active', '']
        logger.info(f"NO. {str(i)} wallet created.")
        log_out_after_create(driver)

    # Log in the first wallet and get test SUI.
    log_in(driver, mns["Seed Phrase"][0])
    request_faucet(driver)
    # set_wallet_sleep_time(driver)
    # success = MintTestToken(driver)
    # if not success:
    #     log_out(driver)
    #     return

    # Mint nfts.
    mint_threeNFTs(driver)
    utils.add_to_csv(file_name, mns.loc[0])
    # Send balance to next wallet.
    # If you want to leave more balance in your wallets, reduce the amount to send.
    success = send_SUI(driver, "0.000055", mns["Address"][1])
    if not success:
        log_out(driver)
        return
    log_out(driver)

    # Later wallets.
    for i in range(1, walletLength):
        log_in(driver, mns["Seed Phrase"][i])
        SwitchToTestNet(driver)
        mint_threeNFTs(driver)
        utils.add_to_csv(file_name, mns.loc[i])
        # Send SUI to next wallet.
        # If you want to leave more balance in your wallets, reduce the amount to send.
        # Use 0.000055-0.000005*i will let the string to be 5e-5.
        success = send_SUI(driver, "0.0000"+str(55-i*5), mns["Address"][i+1])
        if not success:
            log_out(driver)
            return
        log_out(driver)


def create_account(driver):
    create_new_wallet_window(driver)
    mns = pd.DataFrame(columns=["Name", "Address", "Private Key", "Seed Phrase",
                                "Password", "Status", "Description"])
    # Max 10.
    # After 10 wallets, the balance will be 0.00001, not enough for minting nfts.
    walletLength = 10

    # Create wallets first and save in dataframe.
    for i in range(0, walletLength):
        mn, addr, private_key = create_wew_wallet(driver)
        mns.loc[len(mns)] = [f"air {i}", addr, private_key, mn, password, 'active', '']
        logger.info(f"NO. {str(i)} wallet created.")
        log_out_after_create(driver)
        utils.add_to_csv(file_name, mns.loc[i])

    # Log in the first wallet and get test SUI.


def convert_time(start: float):
    end = time.time()
    time_used = end - start
    # convert into hours, minutes and seconds
    hours = time_used // 3600
    time_used = time_used % 3600
    minutes = time_used // 60
    time_used %= 60
    seconds = time_used
    logger.info(f"Time Lapsed = {int(hours)}:{int(minutes)}:{int(seconds)}")


if __name__ == "__main__":
    start = time.time()
    driver = create_driver()
    for i in range(0, 300):
        try:
            create_account(driver)
            # create_pack(driver)
        except Exception as e:
            logger.info(e)
            driver.quit()
            driver = create_driver()
            continue

    convert_time(start)
