# -*- coding: utf-8 -*-
"""Render klip demo uji suara dari server lokal Piper (localhost:3000)."""
import json
import os
import subprocess
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(BASE, "clips")
API = "http://localhost:3000/api/bunyi"

NAMA_ID = {"a": "a", "b": "be", "c": "ce", "d": "de", "e": "e", "f": "ef",
           "g": "ge", "h": "ha", "i": "i", "j": "je", "k": "ka", "l": "el",
           "m": "em", "n": "en", "o": "o", "p": "pe", "q": "qi", "r": "er",
           "s": "es", "t": "te", "u": "u", "v": "ve", "w": "we", "x": "eks",
           "y": "ye", "z": "zet"}
NAMA_EN = {"a": "ay", "b": "bee", "c": "cee", "d": "dee", "e": "ee",
           "f": "ef", "g": "gee", "h": "aitch", "i": "eye", "j": "jay",
           "k": "kay", "l": "el", "m": "em", "n": "en", "o": "oh",
           "p": "pee", "q": "cue", "r": "ar", "s": "ess", "t": "tee",
           "u": "you", "v": "vee", "w": "double-u", "x": "ex", "y": "wy",
           "z": "zee"}

# lang, kata tampil, pecahan, nama huruf (untuk Arab: dibaca suara id)
KATA = [
    ("ar", "كِتَابٌ", ["كِ", "تَا", "بٌ"], ["kaf", "ta", "alif", "ba"]),
    ("ar", "بَيْتٌ", ["بَيْ", "تٌ"], ["ba", "ya", "ta"]),
    ("ar", "مَدْرَسَةٌ", ["مَدْ", "رَ", "سَ", "ةٌ"],
     ["mim", "dal", "ra", "sin", "ta marbuthah"]),
    ("ar", "قَلَمٌ", ["قَ", "لَ", "مٌ"], ["qaf", "lam", "mim"]),
    ("id", "perpustakaan", ["per", "pus", "ta", "ka", "an"], None),
    ("id", "membaca", ["mem", "ba", "ca"], None),
    ("id", "sekolah", ["se", "ko", "lah"], None),
    ("en", "beautiful", ["beau", "ti", "ful"], None),
    ("en", "library", ["li", "bra", "ry"], None),
    ("en", "elephant", ["e", "le", "phant"], None),
]


def ambil(teks, lang):
    data = json.dumps({"teks": teks, "lang": lang, "lambat": 1.0}).encode("utf-8")
    req = urllib.request.Request(API, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def simpan(wav, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".wav"
    with open(tmp, "wb") as f:
        f.write(wav)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp,
                    "-codec:a", "libmp3lame", "-q:a", "4", path],
                   check=True, timeout=60)
    os.remove(tmp)


def segmen_untuk(lang, kata, pecahan, nama):
    hasil = {"kata": [(kata, lang)],
             "suku": [(kata, lang)] + [(p, lang) for p in pecahan] + [(kata, lang)]}
    if lang == "ar":
        hasil["eja"] = [(kata, "ar")] + [(n, "id") for n in nama]
    else:
        tab = NAMA_ID if lang == "id" else NAMA_EN
        hasil["eja"] = [(kata, lang)] + [(tab[c], lang)
                                         for c in kata.lower() if c in tab]
    return hasil


def main():
    manifest = {}
    for i, (lang, kata, pecahan, nama) in enumerate(KATA):
        wid = "w%d" % (i + 1)
        entri = {"id": wid, "kata": kata, "pecahan": pecahan, "modes": {}}
        for mode, segs in segmen_untuk(lang, kata, pecahan, nama).items():
            files = []
            for j, (teks, lg) in enumerate(segs):
                rel = "clips/%s/%s/%s-%d.mp3" % (lang, wid, mode, j)
                tujuan = os.path.join(BASE, rel)
                if not (os.path.exists(tujuan) and os.path.getsize(tujuan) > 0):
                    simpan(ambil(teks, lg), tujuan)
                files.append(rel)
            entri["modes"][mode] = files
            print(lang, kata, mode, len(files), "klip")
        manifest.setdefault(lang, []).append(entri)
    with open(os.path.join(BASE, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("manifest selesai")


if __name__ == "__main__":
    main()
