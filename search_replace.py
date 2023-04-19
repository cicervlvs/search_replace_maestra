from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
import itertools
import time
import json
import wordlists as wl
import audiolists as al
import xpath_locs as xp_loc
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from simple_term_menu import TerminalMenu


def menu_preview(wl_tuple_list):
    pretty_tuple_list = (
        str(wl.wordlists.get(wl_tuple_list))
        .replace("', '", " -> ")
        .replace("(", "")
        .replace(")", "")
        .replace("[", "")
        .replace("]", "")
        .replace("'", "")
        .replace(", ", "\n")
    )

    return pretty_tuple_list


def search_and_replace():
    # Obrir Firefox i maestra
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.page_load_strategy = "eager"
    driver = webdriver.Firefox(options=options)
    driver.get("https://app.maestrasuite.com/login")
    assert "Maestra" in driver.title

    # Posar usuari i contrassenya
    creds = {}
    with open("credentials.json", "r") as credentials:
        creds = json.load(credentials)

    user_box = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.XPATH, xp_loc.user_box))
    )
    user_box.clear()
    username = creds.get("username")
    user_box.send_keys(username)

    password_box = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.XPATH, xp_loc.password_box))
    )
    password = creds.get("password")
    password_box.send_keys(password)
    password_box.send_keys(Keys.RETURN)

    try:
        WebDriverWait(driver, 10).until(
            ec.url_matches("https://app.maestrasuite.com/voiceovers")
        )
    except TimeoutException:
        if driver.find_element(By.CLASS_NAME, "authScreenMessage"):
            print("Usuari o contrassenya incorrectes.")
        else:
            print("Error desconegut.")
        raise

    n_entrega = int(input("Número d'entrega: "))

    if n_entrega > 200 or n_entrega <= 0:
        raise Exception("El número d'entrega ha de ser entre el 1 i el 200.")

    # Seleccionar llistes de paraules
    terminal_menu = TerminalMenu(
        [i for i in wl.wordlists],
        multi_select=True,
        show_multi_select_hint=True,
        preview_command=menu_preview,
        preview_size=0.75,
        preselected_entries=["diacrítics",
                             "majúscules",
                             "guions",
                             "punts_volats"]
    )
    print("Escull les llistes de paraules que vols substituir:")
    terminal_menu.show()
    selected_tuples = list(
        itertools.chain.from_iterable(
            [wl.wordlists.get(item) for item in terminal_menu.chosen_menu_entries]
        )
    )

    audiolist: list = al.audiolists.get(n_entrega)

    # Entrar a la pestanya de captions
    caption_button = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.XPATH, xp_loc.caption_button))
    )
    caption_button.click()

    # Entrar a entrega
    print("Entrant a la pàgina d'entrega...")
    folder_button = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.XPATH, f"//*[text()='Entrega {n_entrega}']"))
    )
    folder_button.click()

    total_changes = 0

    inner_progress = Progress(
        SpinnerColumn(),
        "{task.description}",
        BarColumn(),
        "{task.completed}/{task.total}",
    )

    outer_progress = Progress(
        SpinnerColumn(),
        "{task.description}",
        BarColumn(),
        "{task.completed}/{task.total}",
        TimeRemainingColumn(),
    )

    task_outer = outer_progress.add_task(
        f"[blue]Progrés en l'entrega {n_entrega}", total=len(audiolist)
    )

    progress_table = Table.grid()
    progress_table.add_row(
        Panel.fit(
            inner_progress, title="[b]Àudios", border_style="blue", padding=(1, 1)
        )
    )

    progress_table.add_row(
        Panel.fit(
            outer_progress,
            title="[b]Progrés total",
            border_style="green",
            padding=(1, 1),
        ),
        Panel.fit(f"Total de canvis: {total_changes}\r")
    )

    with Live(progress_table, refresh_per_second=15, vertical_overflow="visible") as live:
        while not outer_progress.finished:
            for audio in audiolist:
                tasks_inner = inner_progress.add_task(
                    f"[green]{audio}", total=len(selected_tuples)
                )

                search_box = WebDriverWait(driver, 30).until(
                    ec.element_to_be_clickable((By.XPATH, xp_loc.search_box))
                )
                search_box.clear()
                search_box.send_keys(audio)
                audio_button = WebDriverWait(driver, 10).until(
                    ec.element_to_be_clickable((By.CLASS_NAME, "listItemFileName"))
                )
                audio_button.click()
                search_button = WebDriverWait(driver, 60).until(
                    ec.element_to_be_clickable(
                        (
                            By.XPATH,
                            xp_loc.search_button,
                        )
                    )
                )
                search_button.click()

                caps_button = WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable(
                        (
                            By.XPATH,
                            xp_loc.caps_button,
                        )
                    )
                )
                caps_button.click()

                for old_word, new_word in selected_tuples:
                    old_word_box = WebDriverWait(driver, 10).until(
                        ec.element_to_be_clickable(
                            (
                                By.XPATH,
                                xp_loc.old_word_box,
                            )
                        )
                    )
                    old_word_box.send_keys(Keys.CONTROL + "a")
                    old_word_box.send_keys(Keys.DELETE)
                    old_word_box.send_keys(old_word)
                    time.sleep(0.4)
                    word_count = (
                        WebDriverWait(driver, 3)
                        .until(
                            ec.element_to_be_clickable((By.XPATH, xp_loc.word_count))
                        )
                        .text
                    )
                    replace_box = driver.find_element(
                        By.XPATH,
                        xp_loc.replace_box,
                    )
                    replace_all_button = driver.find_element(
                        By.XPATH, xp_loc.replace_all_button
                    )

                    if word_count != "No match":
                        replace_box.send_keys(Keys.CONTROL + "a")
                        replace_box.send_keys(Keys.DELETE)
                        replace_box.send_keys(new_word)
                        replace_all_button.click()
                        confirm_button = WebDriverWait(driver, 3).until(
                            ec.element_to_be_clickable(
                                (By.XPATH, xp_loc.confirm_button)
                            )
                        )
                        confirm_button.click()
                        total_changes += int(word_count)
                        
                    inner_progress.update(tasks_inner, advance=1)
                    live.refresh()
                back_button = driver.find_element(
                    By.XPATH,
                    xp_loc.back_button,
                )
                back_button.click()
                outer_progress.update(task_outer, advance=1)

    print(f"Mitjana de canvis: {total_changes / len(audiolist)}")


def main():
    search_and_replace()


if __name__ == "__main__":
    main()
