import requests

api_key = "edcda13a1ac5874b89255e512fdc6750"

film_adi = "Inception"

url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={film_adi}"

cevap = requests.get(url)

veri = cevap.json()

film = veri["results"][0]

print("Film Adı:", film["title"])
print("Puan:", film["vote_average"])
print("Açıklama:", film["overview"])
print("Poster Linki:")
print("https://image.tmdb.org/t/p/w500" + film["poster_path"])