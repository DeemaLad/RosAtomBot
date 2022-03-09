import json
import requests
from bs4 import BeautifulSoup as bs

"""Получение всех новостей со страницы"""
def get_first_news():
	headers = {
	"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.46 (Edition Yx GX)"
	}

	url = "https://www.rosatom.rts-tender.ru/market/"
	r = requests.get(url = url, headers = headers)

	soup = bs(r.text, "lxml")
	articles_cards = soup.find_all("a", class_ = "search-results-title")

	news_dict = {}
	
	for article in articles_cards:
		article_title = article.contents[0]
		article_desc = article.find("div", class_ ="search-results-title-desc").get_text(strip = False)
		article_url = article.get("href")
		
		article_id = article_url.split("/")[-1]
		article_id = article_id[58:]

		news_dict[article_id] = {
			"article_title" : article_title,
			"article_desc" : article_desc, 
			"article_url" : article_url 
		}

	with open ("news_dict.json", "w", encoding = "utf-8") as file:
		json.dump(news_dict,file, indent = 4, ensure_ascii = False)

"""Проверка на появление новых закупок"""
def check_new_updates():
	with open ("news_dict.json", encoding = "utf-8") as file:
		news_dict = json.load(file) #сохраненные до этого 
	
	headers = {
	"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.46 (Edition Yx GX)"
	}

	url = "https://www.rosatom.rts-tender.ru/market/"
	r = requests.get(url = url, headers = headers)

	soup = bs(r.text, "lxml")
	articles_cards = soup.find_all("a", class_ = "search-results-title")

	fresh_news = {}

	for article in articles_cards:
		article_url = article.get("href")
		article_id = article_url.split("/")[-1]
		article_id = article_id[58:]
		
		if (article_id in news_dict):
			continue
		else:
			article_title = article.contents[0]
			article_desc = article.find("div", class_ ="search-results-title-desc").get_text(strip = False)
			
			news_dict[article_id] = {
			"article_title" : article_title,
			"article_desc" : article_desc, 
			"article_url" : article_url 
		}

			fresh_news[article_id] = {
			"article_title" : article_title,
			"article_desc" : article_desc, 
			"article_url" : article_url 
		}

		with open ("news_dict.json", "w", encoding = "utf-8") as file:
			json.dump(news_dict,file, indent = 4, ensure_ascii = False)
			
	return fresh_news

"""Сохранение последней свежей новости"""
def save_fresh_news():
	
	headers = {
	"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.46 (Edition Yx GX)"
	}

	url = "https://www.rosatom.rts-tender.ru/market/"
	r = requests.get(url = url, headers = headers)

	soup = bs(r.text, "lxml")
	articles_cards = soup.find_all("a", class_ = "search-results-title")

	save_fresh_news = {}
	#for article in articles_cards:
	article = articles_cards[0]
	
	article_url = article.get("href")
	article_id = article_url.split("/")[-1]
	article_id = article_id[58:]
		
	article_title = article.contents[0]
	article_desc = article.find("div", class_ ="search-results-title-desc").get_text(strip = False)

	save_fresh_news[article_id] = {
	"article_title" : article_title,
	"article_desc" : article_desc, 
	"article_url" : article_url 
	}

			
	return save_fresh_news

"""Собственно, запуск парсера"""
def main():
	
	get_first_news()
	print(check_new_updates())
	print(save_fresh_news())

if __name__ == "__main__":
	main()