from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
import sys
import wordlists
import audiolists

def search_and_replace(n_entrega):

    n_entrega = int(n_entrega)

    if not type(n_entrega) is int:
        raise TypeError("S'ha d'incloure el número d'una entrega com a argument")

# Obrir Firefox i maestra
    driver = webdriver.Firefox()
    driver.get("https://app.maestrasuite.com/login")
    assert "Maestra" in driver.title

#Posar usuari i contrassenya
#TODO: canviar per comandes bitwarden o per input manual
    user_box = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/div[2]/div/div[1]/input")
    user_box.clear()
    username = input("E-mail:")
    user_box.send_keys(username)

    password_box = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/div[3]/div/div[1]/input")
    password = input("Contrassenya:")
    password_box.send_keys(password)
    password_box.send_keys(Keys.RETURN)

    time.sleep(1)

    if driver.current_url != "https://app.maestrasuite.com/voiceovers":
        raise Exception("Usuari o contrassenya incorrectes. Torneu a iniciar el programa.")

# Entrar a la pestanya de captions
    caption_button = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div[2]/div/div[1]/a[2]")))
    caption_button.click()

#Entrar a entrega
    folder_button = WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH,f"//*[text()='Entrega {n_entrega}']")))
    folder_button.click()

    audiolist = audiolists.entrega_23

    for audio in audiolist:
        search_box = WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[5]/div/div[1]/div/div/div[1]/div[4]/div[1]/div/div/input")))
        search_box.clear()
        search_box.send_keys(audio)
        audio_button = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH,"/html/body/div[1]/div/div[5]/div/div[3]/div[1]/div/div/div/div/div[2]")))
        audio_button.click()
        wordlist = wordlists.infok
        search_button = WebDriverWait(driver, 60).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[4]/div/div[1]/div[2]/div/div[1]/div[5]/div")))
        search_button.click()
        
        caps_button = WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[4]/div/div[1]/div[2]/div/div[1]/div[5]/div/div[2]/div[1]/div[2]/button[1]")))
        caps_button.click()

        for old_word, new_word in wordlist:
            old_word_box = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[4]/div/div[1]/div[2]/div/div[1]/div[5]/div/div[2]/div[1]/div[1]/input")))
            old_word_box.send_keys(Keys.CONTROL + "a")
            old_word_box.send_keys(Keys.DELETE)
            old_word_box.send_keys(old_word)
            time.sleep(.4)
            word_count = WebDriverWait(driver, 3).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[4]/div/div[1]/div[2]/div/div[1]/div[5]/div/div[2]/div[1]/div[2]/div"))).text
            replace_box = driver.find_element(By. XPATH, "/html/body/div[1]/div/div[4]/div/div[1]/div[2]/div/div[1]/div[5]/div/div[2]/div[2]/div[1]/input")
            replace_all_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div/div[1]/div[2]/div/div[1]/div[5]/div/div[2]/div[2]/div[2]/button[2]")

            if word_count != "No match":
                replace_box.send_keys(Keys.CONTROL + "a")
                replace_box.send_keys(Keys.DELETE)
                replace_box.send_keys(new_word) 
                replace_all_button.click()
                confirm_button = WebDriverWait(driver, 3).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[4]/div/div[8]/div/div/div[2]/div/button[1]")))
                confirm_button.click()
                time.sleep(1)

        back_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div/div[1]/div[2]/div/div[1]/div[1]")
        back_button.click()

search_and_replace(sys.argv[1])
