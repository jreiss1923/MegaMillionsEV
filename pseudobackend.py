import requests
from bs4 import BeautifulSoup
import math

state_tax_dict = {"AZ": 0.025, "AR": 0.047, "CA": 0, "CO": 0.044, "CT": 0.0699, "DE": 0.066, "FL": 0, "GA": 0.0575, "ID": 0.058, "IL": 0.0495, "IN": 0.0315, "IA": 0.06, "KS": 0.057, "KY": 0.045, "LA": 0.0475, "ME": 0.0715, "MD": 0.0895, "MA": 0.09, "MI": 0.0425, "MN": 0.0985, "MS": 0.05, "MO": 0.0495, "MT": 0.0675, "NE": 0.0664, "NH": 0, "NJ": 0.1075, "NM": 0.059, "NY": 0.109, "NC": 0.0475, "ND": 0.029, "OH": 0.0399, "OK": 0.0475, "OR": 0.099, "PA": 0.0307, "RI": 0.0599, "SC": 0.065, "SD": 0, "TN": 0, "TX": 0, "VT": 0.0875, "VI": 0, "VA": 0.0575, "WA": 0, "DC": 0.1075, "WV": 0.065, "WI": 0.0765, "WY": 0}

def calculate_post_tax(winnings, state):
    return winnings * (1.0 - 0.37 - state_tax_dict[state])

def text_to_int(jackpot_text):
    num = jackpot_text.split(" ")[0]
    zeroes = jackpot_text.split(" ")[1]

    if (zeroes == "Million"):
        return float(num) * 1000000
    else:
        return float(num) * 1000000000
    
def get_todays_winnings(state):
    response = requests.get("https://powerball-megamillions.com/megamillions/current-jackpot")

    soup = BeautifulSoup(response.content, 'html.parser')

    jackpot_tag = soup.find('div', class_="currentJackpotAmount")
    cash_tag = soup.find('div', class_="currentJackpotCashValue")

    jackpot_text = jackpot_tag.text.split("$")[1]
    cash_text = cash_tag.text.split("$")[1]

    jackpot_int = text_to_int(jackpot_text)
    cash_int = text_to_int(cash_text)

    return calculate_post_tax(jackpot_int, state), calculate_post_tax(cash_int, state)

def poisson(lambda_lottery, i):
    return (math.pow(lambda_lottery, i) * math.exp((-1) * lambda_lottery))/math.factorial(i)

def calculate_poisson(lambda_lottery):
    poisson_arr = []
    for i in range(1, 11):
        poisson_arr.append((1/(1-poisson(lambda_lottery, 0))) * poisson(lambda_lottery, i))

    return poisson_arr

def expected_winners_of_jackpot():
    # todo: estimate ratio between prize pool increase and ticket sales
    # todo: scrape powerball-megamillions for ticket sales data and use estimated ratio to multiply based on prize pool increase

    response = requests.get("https://www.lottoreport.com/mmsales.htm")

    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table')
    rows = table.find_all('tr')
    columns = rows[2].find_all('td')
    
    mm_sales = float(columns[6].text.split("\r\n")[1].replace("$", "").replace(",", ""))
    jj_sales = float(columns[7].text.split("\r\n")[1].replace("$", "").replace(",", ""))
    jackpot_chances = mm_sales/2 + jj_sales*2/3

    return calculate_poisson(jackpot_chances/302575350)

def calculate_ev_jackpot(jackpot):

    ev_jackpot = 0

    poisson = expected_winners_of_jackpot()

    for i in range(0, len(poisson)):
        ev_jackpot += poisson[i] * float(jackpot) / 302575350 / float(i + 1)

    return ev_jackpot

def calculate_ev(jackpot, state):
    return (calculate_ev_jackpot(jackpot[0]) + calculate_post_tax(1000000, state) / 12607306 + 10000/931001 + 500/38792 + 200/14547 + 10/606 + 10/693 + 4/89 + 2/37,
            calculate_ev_jackpot(jackpot[1]) + calculate_post_tax(1000000, state) / 12607306 + 10000/931001 + 500/38792 + 200/14547 + 10/606 + 10/693 + 4/89 + 2/37)


print(calculate_ev(get_todays_winnings("MA"), "MA"))



