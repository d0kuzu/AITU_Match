from dataclasses import dataclass


@dataclass(frozen=True)
class WelcomeTexts:
    welcome_text: str = """
*Привет, студент!*   

*Aitu MATCH* - это бот для знакомств среди айтушников — находи друзей, единомышленников или даже вторую половинку!  

✨ *Что тут можно делать?*  
• Смотреть анкеты других ребят 🕵🏿‍♂️
• Найти интересных людей 🎓
• Общаться с виртуальным собеседником 🥶 

_Нажми *"Начать"*, чтобы создать свою анкету или посмотреть другие!_ 
"""



@dataclass(frozen=True)
class Texts:
    welcome_texts: WelcomeTexts = WelcomeTexts()


TEXTS = Texts()