from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
import json
import wordlists
import audiolists

def search_and_replace():

# Obrir Firefox i maestra
    driver = webdriver.Firefox()
    driver.get("https://app.maestrasuite.com/login")
    assert "Maestra" in driver.title

#Posar usuari i contrassenya
    creds = json.load(open('credentials.json'))
    user_box = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/div[2]/div/div[1]/input")
    user_box.clear()
    username = creds["username"]
    user_box.send_keys(username)

    password_box = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[3]/div/div[3]/div/div[1]/input")
    password = creds["password"]
    password_box.send_keys(password)
    password_box.send_keys(Keys.RETURN)

    time.sleep(3)

    if driver.current_url != "https://app.maestrasuite.com/voiceovers":
        raise Exception("Usuari o contrassenya incorrectes. Torneu a iniciar el programa.")

    n_entrega = int(input("Número d'entrega: "))

    if n_entrega > 200:
        raise Exception("El número d'entrega ha de ser entre el 1 i el 200.")
    
# Entrar a la pestanya de captions
    caption_button = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div[2]/div/div[1]/a[2]")))
    caption_button.click()

#Entrar a entrega
    folder_button = WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH,f"//*[text()='Entrega {n_entrega}']")))
    folder_button.click()

    llista_entregues = {}
    total_entregues = range(1, 200)
    keys = total_entregues
    values = [f"audiolists.entrega_{i}" for i in total_entregues]
    for k, v in zip(keys, values):
        llista_entregues[k] = [v]
    
    audiolist = eval(f"audiolists.entrega_{n_entrega}")

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

search_and_replace()
