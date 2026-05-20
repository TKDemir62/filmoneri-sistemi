from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

favoriler = []

onerilen_filmler = []
onerilen_diziler = []

api_key = "edcda13a1ac5874b89255e512fdc6750"

genre_map = {
    28: "Aksiyon",
    12: "Macera",
    16: "Animasyon",
    35: "Komedi",
    80: "Suç",
    99: "Belgesel",
    18: "Drama",
    14: "Fantastik",
    27: "Korku",
    9648: "Gizem",
    10749: "Romantik",
    878: "Bilim Kurgu",
    53: "Gerilim",
    37: "Western"
}


def trend_filmleri_getir():

    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}"

    cevap = requests.get(url)

    veri = cevap.json()

    trend_filmler = []

    for sonuc in veri["results"][:10]:

        if not sonuc.get("poster_path"):
            continue

        film = {
            "ad": sonuc.get("title"),
            "puan": sonuc["vote_average"],
            "aciklama": sonuc["overview"],
            "resim": "https://image.tmdb.org/t/p/w500" + sonuc["poster_path"],
            "tur": sonuc["genre_ids"][0] if sonuc["genre_ids"] else 0,
            "id": sonuc["id"],
            "tip": "movie",
            "dil": sonuc["original_language"],

            "tur_adi": genre_map.get(
                sonuc["genre_ids"][0] if sonuc["genre_ids"] else 0,
                "Bilinmiyor"
            )
        }

        trend_filmler.append(film)

    return trend_filmler


@app.route("/")
def home():

    trend_filmler = trend_filmleri_getir()

    return render_template(
        "index.html",
        film=None,
        favoriler=favoriler,
        trend_filmler=trend_filmler,
        onerilen_filmler=onerilen_filmler,
        onerilen_diziler=onerilen_diziler
    )


@app.route("/oner", methods=["POST"])
def oner():

    trend_filmler = trend_filmleri_getir()

    film_adi = request.form.get("film")
    tip = request.form.get("tip")

    url = f"https://api.themoviedb.org/3/search/{tip}?api_key={api_key}&query={film_adi}"

    cevap = requests.get(url)

    veri = cevap.json()

    if len(veri["results"]) == 0:

        return render_template(
            "index.html",
            film=None,
            favoriler=favoriler,
            trend_filmler=trend_filmler,
            onerilen_filmler=onerilen_filmler,
            onerilen_diziler=onerilen_diziler
        )

    sonuc = veri["results"][0]

    film = {
        "ad": sonuc.get("title", sonuc.get("name")),
        "puan": sonuc["vote_average"],
        "aciklama": sonuc["overview"],
        "resim": "https://image.tmdb.org/t/p/w500" + sonuc["poster_path"],
        "tur": sonuc["genre_ids"][0] if sonuc["genre_ids"] else 0,
        "id": sonuc["id"],
        "tip": tip,
        "dil": sonuc["original_language"],

        "tur_adi": genre_map.get(
            sonuc["genre_ids"][0] if sonuc["genre_ids"] else 0,
            "Bilinmiyor"
        )
    }

    return render_template(
        "index.html",
        film=film,
        favoriler=favoriler,
        trend_filmler=trend_filmler,
        onerilen_filmler=onerilen_filmler,
        onerilen_diziler=onerilen_diziler
    )


@app.route("/favori-ekle", methods=["POST"])
def favori_ekle():

    trend_filmler = trend_filmleri_getir()

    film = {
        "ad": request.form.get("film_adi"),
        "puan": request.form.get("film_puan"),
        "resim": request.form.get("film_resim"),
        "aciklama": request.form.get("film_aciklama"),
        "tur": request.form.get("film_tur"),
        "id": request.form.get("film_id"),
        "tip": request.form.get("film_tip"),
        "dil": request.form.get("film_dil"),

        "tur_adi": request.form.get("film_tur_adi")
    }

    zaten_var = False

    for fav in favoriler:

        if fav["ad"] == film["ad"]:
            zaten_var = True
            break

    mesaj = ""

    if not zaten_var:
        favoriler.append(film)

    else:
        mesaj = "Bu içerik zaten favorilerde!"

    return render_template(
        "index.html",
        film=film,
        favoriler=favoriler,
        trend_filmler=trend_filmler,
        onerilen_filmler=onerilen_filmler,
        onerilen_diziler=onerilen_diziler,
        mesaj=mesaj
    )


@app.route("/favori-sil", methods=["POST"])
def favori_sil():

    trend_filmler = trend_filmleri_getir()

    global onerilen_filmler
    global onerilen_diziler

    film_adi = request.form.get("film_adi")

    for film in favoriler:

        if film["ad"] == film_adi:
            favoriler.remove(film)
            break

    onerilen_filmler = []
    onerilen_diziler = []

    return render_template(
        "index.html",
        film=None,
        favoriler=favoriler,
        trend_filmler=trend_filmler,
        onerilen_filmler=onerilen_filmler,
        onerilen_diziler=onerilen_diziler
    )


@app.route("/oneri-al", methods=["POST"])
def oner_al():

    trend_filmler = trend_filmleri_getir()

    global onerilen_filmler
    global onerilen_diziler

    onerilen_filmler = []
    onerilen_diziler = []

    if len(favoriler) == 0:

        return render_template(
            "index.html",
            film=None,
            favoriler=favoriler,
            trend_filmler=trend_filmler,
            onerilen_filmler=onerilen_filmler,
            onerilen_diziler=onerilen_diziler
        )

    for fav in favoriler:

        if not fav["id"]:
            continue

        film_id = int(fav["id"])
        tip = fav["tip"]

        url = f"https://api.themoviedb.org/3/{tip}/{film_id}/recommendations?api_key={api_key}"

        cevap = requests.get(url)

        veri = cevap.json()

        sonuclar = veri.get("results", [])

        random.shuffle(sonuclar)

        for sonuc in sonuclar[:3]:

            if not sonuc.get("poster_path"):
                continue

            film_var = False

            for fav2 in favoriler:

                if fav2["ad"] == sonuc.get("title", sonuc.get("name")):
                    film_var = True
                    break

            if not film_var and sonuc["vote_average"] >= 6.5:

                onerilen_icerik = {
                    "ad": sonuc.get("title", sonuc.get("name")),
                    "puan": sonuc["vote_average"],
                    "resim": "https://image.tmdb.org/t/p/w500" + sonuc["poster_path"],
                    "tip": tip,
                    "dil": sonuc["original_language"],

                    "tur_adi": genre_map.get(
                        sonuc["genre_ids"][0] if sonuc["genre_ids"] else 0,
                        "Bilinmiyor"
                    )
                }

                if tip == "movie":

                    if onerilen_icerik not in onerilen_filmler:
                        onerilen_filmler.append(onerilen_icerik)

                else:

                    if onerilen_icerik not in onerilen_diziler:
                        onerilen_diziler.append(onerilen_icerik)

    return render_template(
        "index.html",
        film=None,
        favoriler=favoriler,
        trend_filmler=trend_filmler,
        onerilen_filmler=onerilen_filmler,
        onerilen_diziler=onerilen_diziler
    )


if __name__ == "__main__":
    app.run(debug=True)