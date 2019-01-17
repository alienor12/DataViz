import http.cookiejar
import urllib.request
import requests
import bs4
import json
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('email',
                    help='your email associated to Facebook account')
parser.add_argument('passwd',
                    help='password of your Facebook account')
parser.add_argument('friends',
                    help='path to your json file with your list of friends')

args = parser.parse_args()

# Store the cookies and create an opener that will hold them
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Add our headers
opener.addheaders = [('User-agent', 'dfdf')]

# Install our opener (note that this changes the global opener to the one
# we just made, but you can also just call opener.open() if you want)
urllib.request.install_opener(opener)

# The action/ target from the form
authentication_url = 'https://m.facebook.com/login.php'

# Input parameters we are going to send
payload = {
  'email': args.email,
  'pass': args.passwd
  }

# Use urllib to encode the payload
data = urllib.parse.urlencode(payload).encode("utf-8")

# Build our Request object (supplying 'data' makes it a POST)
req = urllib.request.Request(authentication_url, data)

# Make the request and read the response
resp = urllib.request.urlopen(req)
contents = resp.read()
# print(contents)

def get_user_info(url):
  url = 'https://m.facebook.com' + url[:-12] + '/about'
  data = requests.get(url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  info = {}

  # Education info
  scol = []
  for element in soup.find_all('div', {'id':'education'}):
    for link in element.find_all('a'):
      if len(link.text) > 1:
        scol += [link.text]

  # Birthday info
  for element in soup.find_all('div', {'title':'Date de naissance'}):
    for subelement in element.find_all('div'):
      birthday = subelement.text

  try:
    if len(birthday.split(' ')) == 3:
      year = birthday.split(' ')[-1]

    info['birthday year'] = year
  except NameError:
    info['birthday year'] = ''

  try:
    info['birthday month'] = birthday.split(' ')[1]
  except NameError:
    info['birthday month'] = ''

  try:
    info['birthday day'] = birthday.split(' ')[0]
  except NameError:
    info['birthday day'] = ''


  # Work info
  work = []
  for element in soup.find_all('div', {'id':'work'}):
    for link in element.find_all('a'):
      if len(link.text) > 1:
        work += [link.text]

    info['work'] = work

  # Current city
  for element in soup.find_all('div', {'title': 'Ville actuelle'}):
    for subelement in element.find_all('div'):
      current_city = subelement.text

  try:
    info['current city'] = current_city
  except NameError:
    info['current city'] = ''

  # Home city
  for element in soup.find_all('div', {'title': 'Ville d’origine'}):
    for subelement in element.find_all('div'):
      home_city = subelement.text

  try:
    info['home city'] = home_city
  except NameError:
    info['home city'] = ''

  # Sex
  for element in soup.find_all('div', {'title': 'Sexe'}):
    for subelement in element.find_all('div'):
      sex = subelement.text

  try:
    info['sex'] = sex
  except NameError:
    info['sex'] = ''

  # Relationship
  try:
    relationship = soup.find('div', {'id':'relationship'}).text

    for i in range(len(relationship)-1):
      if relationship[i].islower() and relationship[i+1].isupper():
        relationship = relationship[i+1:]
        break
    info['relationship'] = relationship


  except AttributeError:
    info['relationship'] = ''

  for element in soup.find_all('div', {'id':'relationship'}):
    for link in element.find_all('a'):
      spouse = link.get('href')

  try:
    info['spouse'] = spouse
  except NameError:
    info['spouse'] = ''

  # Friends in common
  for link in soup.find_all('a'):
    if 'en commun' in link.text:
      common_friends = link.text.split('(')[1].split(')')[0]

  try:
    info['common friends'] = common_friends
  except NameError:
    info['common friends'] =''

  return info

def get_user_likes(url):
  new_url = 'https://m.facebook.com' + url[:-12] +'?v=likes'
  data = requests.get(new_url, cookies=cj)
  soup = bs4.BeautifulSoup(data.text, 'html.parser')

  likes = []
  # Activities
  for element in soup.find_all('a'):
    if element.span:
      if element.span.text != 'En voir plus' and element.span.text != 'Voir plus':
        likes += [element.span.text]

  return likes

with open(args.friends, 'r') as fp:
    data = json.load(fp)
    new_data = {}
    for user in data:
      print(user, data[user])
      user_url = data[user]
      user_info = get_user_info(user_url)
      user_likes = get_user_likes(user_url)
      user_info['likes'] = user_likes
      user_info['url'] = user_url
      new_data[user] = user_info

with open('friend_list_info.json', 'w') as fp:
  json.dump(new_data, fp, sort_keys=True, indent=4)

