import requests
url = "https://movie.douban.com/top250"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
proxies = {
    "http": None,
    "https": None
}
response = requests.get(url=url, headers=headers, proxies=proxies)
print(response.text)
with open("douban.html", "w", encoding="utf-8") as f:
    f.write(response.text)