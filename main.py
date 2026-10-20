from database import mydb
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)



cursor=mydb.cursor()
cursor.execute("INSERT INTO ayarlar (id, max_teslim_sure, ceza, alim_limit) VALUES (1, 15, 5.00, 3) ON CONFLICT (id) DO NOTHING;")
mydb.commit()
cursor.close()
app = FastAPI()
YONETICISIFRE=os.getenv("YONETICISIFRE")
class uye(BaseModel):
    isim: str
    soyisim: str
    email: str
    sifre: str

class kitap(BaseModel):
    isim: str
    yazar: str
    kategori: Optional[str]=None
    sayfa_sayisi: Optional[int] = None
    calisan_email: str

def gecmis_ekle(mesaj,detay):
    cursor=mydb.cursor()
    cursor.execute("INSERT INTO gecmis (mesaj,aciklama) VALUES (%s,%s)",(mesaj,detay))
    mydb.commit()

@app.post("/yoneticiler")
def yoneticiekle(sifre:int,bilgiler:uye):
    if sifre==YONETICISIFRE:
        cursor=mydb.cursor()
        degerler = (
            bilgiler.isim.lower().title(), 
            bilgiler.soyisim.lower().title(), 
            bilgiler.email, 
            bilgiler.sifre
        )
        cursor.execute("SELECT id FROM yonetici WHERE email = %s", (bilgiler.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bu email adresiyle kayitli bir yonetici zaten mevcut"
            )
        cursor.execute("INSERT INTO yonetici (isim, soyisim, email, sifre) VALUES (%s,%s,%s,%s)",degerler)
        mydb.commit()
        gecmis_ekle("Basarili",f"{bilgiler.isim.title()} {bilgiler.soyisim.title()} adli yonetici eklendi")
        return {"Durum": "Basarili", "Mesaj": f"{bilgiler.isim.title()} {bilgiler.soyisim.title()} adli yonetici eklendi"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gecersiz yonetici sifresi! Yetkilendirme basarisiz."
        )

@app.get("/uyeler")
def uyeler():
    cursor=mydb.cursor()
    cursor.execute("SELECT * FROM kullanicilar")
    result=cursor.fetchall()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kayitli kullanici yoktur"
        )
    kullanicilar=[]
    for kullanici in result:
            kullanicilar.append({
                "Isim": kullanici[1],
                "Soyisim": kullanici[2],
                "Email": kullanici[3]
            })
    return {
        "Toplam kullanici sayisi": len(kullanicilar),
        "Kullanicilar": kullanicilar
    }
@app.post("/uyeler/uyeekle")
def uyeekle(bilgiler:uye):
    cursor=mydb.cursor()
    cursor.execute("SELECT id FROM kullanicilar WHERE email = %s", (bilgiler.email,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu email adresiyle kayitli bir uye zaten mevcut"
        )
    degerler = (
        bilgiler.isim.lower().title(), 
        bilgiler.soyisim.lower().title(), 
        bilgiler.email, 
        bilgiler.sifre
    )
    cursor.execute("INSERT INTO kullanicilar (isim, soyisim, email, sifre) VALUES (%s,%s,%s,%s)",degerler)
    mydb.commit()
    gecmis_ekle("Basarili",f"{bilgiler.isim.lower().title()} {bilgiler.soyisim.lower().title()} adli üye eklendi")
    return {"Durum": "Basarili", "Mesaj": f"{bilgiler.isim.lower().title()} {bilgiler.soyisim.lower().title()} adli üye eklendi"}

@app.delete("/uyeler/uyesil")
def uyesil(mail:str):
    cursor=mydb.cursor()
    cursor.execute("DELETE FROM kullanicilar WHERE email = %s",(mail,))
    mydb.commit()
    if cursor.rowcount==0:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Bu emailde kullanici bulunamadi"
    )
    gecmis_ekle("Silindi", f"{mail} adresli kullanici silindi")
    return {"Durum": "Basarili", "Mesaj": f"{mail} basariyla silindi"}
@app.get("/calisanlar")
def calisanlar():
    cursor=mydb.cursor()
    cursor.execute("SELECT * FROM calisanlar")
    result=cursor.fetchall()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kayitli kullanici yoktur"
        )
    kullanicilar=[]
    for kullanici in result:
            kullanicilar.append({
                "Isim": kullanici[1],
                "Soyisim": kullanici[2],
                "Email": kullanici[3]
            })
    return {
        "Toplam calisan sayisi": len(kullanicilar),
        "Calisanlar": kullanicilar
    }

@app.post("/calisanlar/calisanekle")
def calisanekle(bilgiler:uye):
    cursor=mydb.cursor()
    cursor.execute("SELECT id FROM calisanlar WHERE email = %s", (bilgiler.email,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu email adresiyle kayitli bir calisan zaten mevcut"
        )
    degerler = (
        bilgiler.isim.lower().title(), 
        bilgiler.soyisim.lower().title(), 
        bilgiler.email, 
        bilgiler.sifre
    )
    cursor.execute("INSERT INTO calisanlar (isim, soyisim, email, sifre) VALUES (%s,%s,%s,%s)",degerler)
    mydb.commit()
    gecmis_ekle("Basarili",f"{bilgiler.isim.lower().title()} {bilgiler.soyisim.lower().title()} adli calisan eklendi")
    return {"Durum": "Basarili", "Mesaj": f"{bilgiler.isim.lower().title()} {bilgiler.soyisim.lower().title()} adli calisan eklendi"}

@app.delete("/calisanlar/calisansil")
def calisansil(mail:str):
    cursor=mydb.cursor()
    cursor.execute("DELETE FROM calisanlar WHERE email = %s",(mail,))
    mydb.commit()
    if cursor.rowcount==0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu emailde calisan bulunamadi"
        )
    gecmis_ekle("Silindi", f"{mail} adresli calisan silindi")
    return {"Durum": "Basarili", "Mesaj": f"{mail} basariyla silindi"}
@app.get("/kitaplar")
def kitaplar():
    cursor=mydb.cursor()
    cursor.execute("SELECT * FROM kitaplar")
    result=cursor.fetchall()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kayitli kitap yoktur"
        )
    kitap_listesi = []
    for kitap in result:
        durum = "Evet" if kitap[5] else "Hayır"
        kitap_listesi.append({
            "Kitap ismi": kitap[1],
            "Yazar": kitap[2],
            "Kategori": kitap[6],
            "Odunc_durumu": durum
        })
    return {
        "Toplam kitap sayisi": len(kitap_listesi),
        "Kitaplar": kitap_listesi
    }
@app.post("/kitaplar/kitapekle")
def kitapekle(bilgiler: kitap):
    cursor=mydb.cursor()
    cursor.execute("SELECT id FROM calisanlar WHERE email=(%s)",(bilgiler.calisan_email,))
    result=cursor.fetchone()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calisan emaili sistemde bulunamadi"
        )
    cursor.execute("""
        SELECT id FROM kitaplar 
        WHERE kitap_ismi = %s AND yazar = %s
    """, (bilgiler.isim, bilgiler.yazar))
    
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{bilgiler.isim}' adli, {bilgiler.yazar} yazarina ait bu kitap kutuphanede zaten kayitli"
        )
    degerler=(
        bilgiler.isim,
        bilgiler.yazar,
        bilgiler.sayfa_sayisi,
        result[0],
        bilgiler.kategori
    )
    cursor.execute("INSERT into kitaplar (kitap_ismi,yazar,sayfa_sayisi,ekleyen_id,kategori) VALUES (%s,%s,%s,%s,%s)",degerler)
    mydb.commit()
    gecmis_ekle("Basarili",f"{bilgiler.isim.lower().title()} adli kitap kutuphaneye eklendi")
    return {"Durum": "Basarili", "Mesaj": f"{bilgiler.isim.lower().title()} adli kitap kutuphaneye eklendi"}

@app.delete("/kitaplar/kitapsil")
def kitapsil(kitapid:int):
    cursor=mydb.cursor()
    cursor.execute("SELECT kitap_ismi,odunc_durumu FROM kitaplar WHERE id = %s", (kitapid,))
    kitap = cursor.fetchone()
    if not kitap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kitap bulunamadi"
        )
    if kitap[1] is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{kitap[0]}' isimli kitap su anda bir kullanicida oduncte oldugu icin silinemez"
        )
    cursor.execute("DELETE FROM kitaplar WHERE id=%s",(kitapid,))
    mydb.commit()
    gecmis_ekle("Silindi",f"{kitap[0]} isimli kitap kutuphaneden silindi")
    return {"Durum":"Silindi","Mesaj":f"{kitap[0]} isimli kitap kutuphaneden silindi"}

@app.get("/kitaplar/ara")
def kitapara(kitapismi:Optional[str]=None,yazar:Optional[str]=None,kategori:Optional[str]=None,musait_mi:Optional[bool]=None):
    if kitapismi is None and yazar is None and kategori is None and musait_mi is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lütfen herhangi bir deger giriniz"
        )
    sorgu = "SELECT * FROM kitaplar WHERE 1=1"
    degerler = []
    if kitapismi:
        sorgu += " AND kitap_ismi = %s"
        degerler.append(kitapismi)

    if yazar:
        sorgu += " AND yazar = %s"
        degerler.append(yazar)

    if kategori:
        sorgu += " AND kategori = %s"
        degerler.append(kategori)

    if musait_mi is not None:
        sorgu += " AND odunc_durumu = %s"
        degerler.append(musait_mi)
    
    cursor=mydb.cursor()
    cursor.execute(sorgu,tuple(degerler))
    result=cursor.fetchall()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu ozelliklere sahip kitap bulunamadi"
        )
    kitaplistesi=[]
    for i in result:
        durum="Evet" if i[5]==True else "Hayir"
        sayfa="Unknown" if not i[3] else i[3]
        kitaplistesi.append({
            "Kitap ismi": i[1],
            "Yazar": i[2],
            "Kategori": i[6],
            "Sayfa": sayfa,
            "Odunc Durumu": durum,
        })
    return {"Durum":"Kitap filtreleme","Sonuclar":kitaplistesi}

@app.get("/kitaplar/oduncler")
def oduncler():
    cursor=mydb.cursor()
    cursor.execute("SELECT * FROM odunc_alinanlar WHERE verilme_tarihi is NULL")
    result=cursor.fetchall()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kayitli odunc kaydi yoktur"
        )
    odunclistesi=[]
    for k in result:
        cursor.execute("SELECT kitap_ismi FROM kitaplar WHERE id=%s",(k[1],))
        kitapismi=cursor.fetchone()
        cursor.execute("SELECT isim,soyisim FROM kullanicilar WHERE id=%s",(k[2],))
        kullanici=cursor.fetchone()
        odunclistesi.append({
            "Kitap ismi": kitapismi[0],
            "kullanici": f"{kullanici[0]} {kullanici[1]}",
            "Alinma tarihi": k[3],
            "Son teslim tarihi": k[4]
        })
    return {
        "Odunc sayisi": len(odunclistesi),
        "Odunc listesi": odunclistesi
    }
@app.post("/kitaplar/oduncler/oduncal")
def oduncal(kitapid:int,user_id:int):
    cursor=mydb.cursor()
    cursor.execute("SELECT odunc_durumu, kitap_ismi FROM kitaplar WHERE id=(%s)",(kitapid,))
    resultkitap=cursor.fetchone()
    kitapismi=resultkitap[1]
    if not resultkitap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kutuphanede bu kitap bulunmamaktadir"
        )
    if resultkitap[0] is True:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{kitapismi}' isimli kitap zaten odunc alinmis"
        )
    cursor.execute("SELECT * FROM kullanicilar WHERE id=(%s)",(user_id,))
    result=cursor.fetchone()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu kullanici bulunamadi"
        )
    cursor.execute("SELECT COUNT(*) FROM odunc_alinanlar where kullanici_id=%s AND verilme_tarihi IS NULL",(user_id,))
    adet=cursor.fetchone()
    cursor.execute("SELECT alim_limit, max_teslim_sure from ayarlar")
    limit=cursor.fetchone()
    if adet[0]>=limit[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanicinin odunc alma limiti doludur"
        )
    
    
    cursor.execute("UPDATE kitaplar SET odunc_durumu=TRUE WHERE id=%s",(kitapid,))
    mydb.commit()
    su_an = datetime.now(timezone.utc)
    gun_sayisi = limit[1]
    son_teslim_tarihi = su_an + timedelta(days=gun_sayisi)
    degerler=(
        kitapid,
        user_id,
        son_teslim_tarihi
    )
    cursor.execute("INSERT INTO odunc_alinanlar (kitap_id,kullanici_id,son_teslim_tarihi) VALUES (%s,%s,%s)",degerler)
    mydb.commit()
    gecmis_ekle("Odunc Alindi",f"{kitapismi} isimli kitap odunc alinmistir")
    return {"Durum":"Odunc Alindi","Mesaj":f"{kitapismi} isimli kitap odunc alinmistir"}

@app.post("/kitaplar/oduncler/oduncver")
def oduncver(kitapid:int,userid:int):
    cursor=mydb.cursor()
    cursor.execute("SELECT * from kullanicilar WHERE id=%s",(userid,))
    kullaniciid=cursor.fetchone()
    if not kullaniciid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu kullanici bulunamadi"
        )
    cursor.execute("SELECT * from kitaplar WHERE id=%s",(kitapid,))
    kitap1=cursor.fetchone()
    if not kitap1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kutuphanede bu kitap bulunmamaktadir"
        )
    cursor.execute("SELECT * FROM odunc_alinanlar WHERE kitap_id=%s AND kullanici_id=%s AND verilme_tarihi IS NULL",(kitapid,userid))
    result=cursor.fetchone()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu kullaniciya ait aktif bir odunc kaydi bulunamadi"
        )
    verilme_tarihi = datetime.now(timezone.utc)
    cursor.execute("UPDATE odunc_alinanlar SET verilme_tarihi=%s WHERE kitap_id=%s AND kullanici_id=%s AND verilme_tarihi IS NULL",(verilme_tarihi,kitapid,userid))
    mydb.commit()
    cursor.execute("UPDATE kitaplar SET odunc_durumu=FALSE WHERE id=%s", (kitapid,))
    mydb.commit()
    if verilme_tarihi>result[4]:    
        fark=verilme_tarihi-result[4]
        cursor.execute("SELECT ceza FROM ayarlar")
        ceza=cursor.fetchone()
        cursor.execute("SELECT guncel_ceza from kullanicilar WHERE id=%s",(userid,))
        guncel=cursor.fetchone()
        if guncel[0] is None:
            guncel1=0
        else:
            guncel1=guncel[0]
        ceza_birim = float(ceza[0])
        yeni_ceza = (fark.days * ceza_birim) + float(guncel1)
        cursor.execute("UPDATE kullanicilar SET guncel_ceza=%s WHERE id=%s",(yeni_ceza,userid))
        mydb.commit()
        gecmis_ekle("Odunc verme",f"Bu kullanicinin bu işlem sonucunda {fark.days*ceza_birim} TL cezasi bulunmaktadir")
        return {"Durum":"Odunc verme","Mesaj":f"Bu kullanicinin bu işlem sonucunda {fark.days*ceza_birim} TL cezasi bulunmaktadir"}
    gecmis_ekle("Odunc verme","Islem basariyla tamamlanmistir")
    return {"Durum":"Odunc verme","Mesaj":"Islem basariyla tamamlanmistir"}

@app.get("/kitaplar/oduncler/gecikenler")
def gecikenler():
    cursor=mydb.cursor()
    cursor.execute("SELECT * FROM odunc_alinanlar WHERE verilme_tarihi IS NULL")
    result=cursor.fetchall()
    gecikenkitaplar=[]
    now = datetime.now(timezone.utc)
    for k in result:
        if now>k[4]:
            cursor.execute("SELECT kitap_ismi from kitaplar where id=%s",(k[1],))
            kitapismi=cursor.fetchone()
            cursor.execute("SELECT isim,soyisim from kullanicilar where id=%s",(k[2],))
            kullanici=cursor.fetchone()
            gecikenkitaplar.append({
                "Kitap": kitapismi[0],
                "Kullanici": f"{kullanici[0]} {kullanici[1]}",
                "Son teslim tarihi": k[4],
                "Gecikme suresi": f"{(now-k[4]).days} gun"
            })
    if not gecikenkitaplar:
        return {"Durum": "Temiz", "Mesaj": "Gecikmis kitap bulunmamaktadir"}

    return {
        "Toplam geciken kitap": len(gecikenkitaplar),
        "Gecikenler": gecikenkitaplar
    }

@app.post("/kitaplar/oduncler/sureuzat")
def sureuzat(userid:int,kitapid:int):
    cursor=mydb.cursor()
    cursor.execute("SELECT guncel_ceza,isim,soyisim FROM kullanicilar WHERE id=%s",(userid,))
    kullanici=cursor.fetchone()
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu kullanici bulunamadi"
        )
    if kullanici[0] is not None and float(kullanici[0]) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Odenmemis {kullanici[0]} TL cezaniz bulunmaktadir. Once borcunuzu odeyiniz."
        )
    isim=f"{kullanici[1]} {kullanici[2]}"
    cursor.execute("SELECT * FROM kitaplar WHERE id=%s",(kitapid,))
    kitap1=cursor.fetchone()
    if not kitap1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kutuphanede bu kitap bulunamadi"
        )
    cursor.execute("SELECT * FROM odunc_alinanlar WHERE kitap_id=%s AND kullanici_id=%s AND verilme_tarihi is Null",(kitapid,userid))
    result=cursor.fetchone()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu kullaniciya ait aktif bir odunc kaydi bulunamadi"
        )
    now= datetime.now(timezone.utc)
    if result[4]<now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kitabin son teslim tarihi gectigi icin sure uzatilamaz. Lutfen kitabi iade ediniz ve cezayi odeyiniz."
        )
    cursor.execute("SELECT max_teslim_sure FROM ayarlar")
    sure=cursor.fetchone()
    eklenecek_gun = sure[0] if sure else 15
    yeni_teslim_tarihi = result[4] + timedelta(days=eklenecek_gun)
    cursor.execute(
        "UPDATE odunc_alinanlar SET son_teslim_tarihi = %s WHERE id = %s",
        (yeni_teslim_tarihi, result[0])
    )
    mydb.commit()

    gecmis_ekle("Sure Uzatildi", f"{isim} kullanicisinin '{kitap1[1]}' kitabi icin teslim suresi {eklenecek_gun} gun uzatildi.")

    return {
        "Durum": "Basarili",
        "Mesaj": f"'{kitap1[1]}' kitabi icin teslim suresi {eklenecek_gun} gun uzatilmistir.",
        "Eski Teslim Tarihi": result[4],
        "Yeni Teslim Tarihi": yeni_teslim_tarihi
    }

@app.get("/kitaplar/populer")
def populer():
    cursor=mydb.cursor()
    cursor.execute("""SELECT kitap_id, COUNT(kitap_id) 
        FROM odunc_alinanlar 
        GROUP BY kitap_id 
        ORDER BY COUNT(kitap_id) DESC 
        LIMIT 5;""")
    result=cursor.fetchall()
    siralama=[]
    a=1
    for i in result:
        cursor.execute("SELECT kitap_ismi,yazar,kategori FROM kitaplar WHERE id=%s",(i[0],))
        kitapbilgi=cursor.fetchone()
        kitapismi=kitapbilgi[0]
        yazar=kitapbilgi[1]
        siralama.append({
            "Populerlik sirasi": f"{a}.",
            "Kitap ismi": kitapismi,
            "Yazar": yazar
        })
        a+=1

    return {"Durum":"Populerlik sirasi","Populerlik listesi":siralama}

@app.get("/uyeler/cezalar")
def cezalar():
    cursor=mydb.cursor()
    cursor.execute("SELECT * FROM kullanicilar")
    result=cursor.fetchall()
    cezalarlistesi=[]
    for k in result:
        ceza_tutari = float(k[6]) if k[6] is not None else 0.0
        if ceza_tutari>0:
            cezalarlistesi.append({
                "Isim": k[1],
                "Soyisim": k[2],
                "Email": k[3],
                "Ceza Miktari": k[6]
            })

    return {
        "Cezalar listesi": cezalarlistesi
    }
@app.post("/uyeler/cezalar/cezaode")
def cezaode(userid:int,odeme:float):
    cursor=mydb.cursor()
    cursor.execute("SELECT guncel_ceza FROM kullanicilar WHERE id=%s",(userid,))
    result=cursor.fetchone()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu kullanici bulunamadi"
        )
    if result[0] is None or float(result[0]) <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanicinin odenmesi gereken bir borcu bulunmamaktadir"
        )
    if odeme <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gecersiz odeme tutari! Tutar 0'dan buyuk olmalidir."
        )
    mevcut_borc = float(result[0]) if (result[0] is not None) else 0.0
    if odeme>mevcut_borc:
        para_ustu = round(odeme - mevcut_borc, 2)
        cursor.execute("UPDATE kullanicilar SET guncel_ceza=0.00 WHERE id=%s",(userid,))
        mydb.commit()
        gecmis_ekle("Borc odeme",f"Kullanici borcu odenmekle birlikte para ustu {para_ustu} TL'dir")
        return {"Durum":"Borc odeme","Mesaj":f"Kullanici borcu odenmekle birlikte para ustu {para_ustu} TL'dir"}
    elif odeme<mevcut_borc:
        kalan_borc = round(mevcut_borc - odeme, 2)
        cursor.execute("UPDATE kullanicilar SET guncel_ceza=%s WHERE id=%s",(kalan_borc,userid))
        mydb.commit()
        gecmis_ekle("Borc odeme",f"Kullanici borcu odenmekle birlikte kalan borc {kalan_borc} TL'dir")
        return {"Durum":"Borc odeme","Mesaj":f"Kullanici borcu odenmekle birlikte kalan borc {kalan_borc} TL'dir"}
    else:
        cursor.execute("UPDATE kullanicilar SET guncel_ceza=0.00 WHERE id=%s",(userid,))
        mydb.commit()        
        gecmis_ekle("Borc odeme",f"Kullanici borcu odenmistir")
        return {"Durum":"Borc odeme","Mesaj":f"Kullanici borcu odenmistir"}

@app.get("/uyeler/gecmis")
def gecmis(userid:int):
    cursor=mydb.cursor()
    cursor.execute("SELECT * FROM kullanicilar WHERE id=%s",(userid,))
    result=cursor.fetchone()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu kullanici bulunamadi"
        )
    kullaniciid=result[0]
    cursor.execute("SELECT * FROM odunc_alinanlar WHERE kullanici_id=%s",(kullaniciid,))
    oduncresult=cursor.fetchall()
    if not oduncresult:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu kullanicinin odunc kaydi bulunamadi"
        )
    odunc=[]
    degil=[]
    for i in oduncresult:
        cursor.execute("SELECT * FROM kitaplar WHERE id=%s",(i[1],))
        kitapbilgi=cursor.fetchone()
        if i[5] is None:
            odunc.append({
                "Kitap ismi": kitapbilgi[1],
                "Yazar": kitapbilgi[2],
                "Kategori": kitapbilgi[6]
            })
        else:
            degil.append({
                "Kitap ismi": kitapbilgi[1],
                "Yazar": kitapbilgi[2],
                "Kategori": kitapbilgi[6]
            })
    ret={"Durum":f"{result[1]} {result[2]} isimli kullanicinin odunc kayitlari","Aktif kayitlar":odunc,"Eski kayitlar":degil}
    return ret

@app.get("/gecmis")
def islem_gecmis():
    cursor=mydb.cursor()
    cursor.execute("SELECT * FROM gecmis ORDER BY id DESC LIMIT 50")
    result=cursor.fetchall()
    gecmislist=[]
    for i in result:
        gecmislist.append({
            "mesaj": i[1],
            "aciklama": i[2],
            "olusturulma tarihi": i[3]
        })

    return {"Durum":"Gecmis","Gecmis listesi":gecmislist}

@app.get("/istatistikler")
def istatistik():
    cursor = mydb.cursor()

    cursor.execute("SELECT COUNT(*) FROM kitaplar")
    kitapsayisi = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM kitaplar WHERE odunc_durumu = %s", (True,))
    odunctekikitaplar = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM kitaplar WHERE odunc_durumu = %s", (False,))
    raftakikitaplar = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT kategori) FROM kitaplar")
    kategori_sayisi = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM kullanicilar")
    kullanicisayisi = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE guncel_ceza > 0")
    borclu_uye_sayisi = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(guncel_ceza), 0) FROM kullanicilar")
    toplamceza = float(cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM odunc_alinanlar")
    toplam_odunc_sayisi = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM odunc_alinanlar WHERE verilme_tarihi IS NULL AND son_teslim_tarihi < CURRENT_DATE"
    )
    gecikmis_kitap_sayisi = cursor.fetchone()[0]

    return {
        "Durum": "Kütüphane Genel İstatistikleri",
        "Kitap Ozeti": {
            "Toplam Kitap": kitapsayisi,
            "Rafta Musait": raftakikitaplar,
            "Oduncte Olan": odunctekikitaplar,
            "Farkli Kategori Sayisi": kategori_sayisi
        },
        "Uye ve Finansal Durum": {
            "Toplam Uye": kullanicisayisi,
            "Borclu Uye Sayisi": borclu_uye_sayisi,
            "Odenmemis Toplam Ceza Tutari (TL)": toplamceza
        },
        "Dolasim ve Operasyon": {
            "Toplam Yapilan Odunc Islemi": toplam_odunc_sayisi,
            "Teslimi Gecikmis (Riskli) Kitaplar": gecikmis_kitap_sayisi
        }
    }

@app.post("/kitaplar/degerlendir")
def degerlendir(user_id: int,kitap_id: int,puan: int, yorum: Optional[str]=None):
    if not puan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Puan alanini eksik birakmayiniz"
        )
    if not (1 <= puan <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Puan 1 ile 5 arasinda olmalidir."
        )
    cursor=mydb.cursor()
    if yorum:
        cursor.execute("INSERT INTO degerlendirmeler (kitap_id,kullanici_id,puan,yorum) VALUES (%s,%s,%s,%s)",(kitap_id,user_id,puan,yorum))
        mydb.commit()
    else:
        cursor.execute("INSERT INTO degerlendirmeler (kitap_id,kullanici_id,puan) VALUES (%s,%s,%s)",(kitap_id,user_id,puan))
        mydb.commit()

    return {"Durum": "Basarili", "Mesaj": "Degerlendirmeniz kaydedildi"}

@app.get("/kitaplar/yorumlar")
def yorumlar(kitap_id: int):
    cursor = mydb.cursor()

    cursor.execute("SELECT kitap_ismi, yazar FROM kitaplar WHERE id = %s", (kitap_id,))
    kitap = cursor.fetchone()
    if not kitap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Belirtilen ID'ye sahip kitap bulunamadi."
        )

    cursor.execute(
        "SELECT COALESCE(AVG(puan), 0), COUNT(puan) FROM degerlendirmeler WHERE kitap_id = %s",
        (kitap_id,)
    )
    ortalama_puan, toplam_degerlendirme = cursor.fetchone()

    cursor.execute(
        """
        SELECT puan, yorum 
        FROM degerlendirmeler 
        WHERE kitap_id = %s 
          AND yorum IS NOT NULL 
          AND TRIM(yorum) != '' 
        ORDER BY id DESC
        """,
        (kitap_id,)
    )
    yorum_kayitlari = cursor.fetchall()

    yorum_listesi = [
        {"puan": row[0], "yorum": row[1]} 
        for row in yorum_kayitlari
    ]

    return {
        "kitap_id": kitap_id,
        "kitap_ismi": kitap[0],
        "yazar": kitap[1],
        "ozet": {
            "ortalama_puan": round(float(ortalama_puan), 2),
            "toplam_degerlendirme_sayisi": toplam_degerlendirme,
            "yorum_sayisi": len(yorum_listesi)
        },
        "yorumlar": yorum_listesi
    }

@app.put("/ayarlar")
def ayarlariguncelle(yonetici_sifresi: int,yeni_alim_limit: Optional[int] = None, yeni_ceza: Optional[float] = None, yeni_max_teslim_sure: Optional[int]=None):
    if yonetici_sifresi!=YONETICISIFRE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="YONETİCİ SİFRESİ YANLİS GİRİLMİSTİR"
        )
    degerler=[]
    guncellenecekler=[]
    if yeni_alim_limit:
        guncellenecekler.append("alim_limit= %s")
        degerler.append(yeni_alim_limit)

    if yeni_ceza:
        guncellenecekler.append("ceza=%s")
        degerler.append(yeni_ceza)

    if yeni_max_teslim_sure:
        guncellenecekler.append("max_teslim_sure=%s")
        degerler.append(yeni_max_teslim_sure)

    if not guncellenecekler:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guncellenecek en az bir ayar girmelisiniz."
        )
    sorgu = f"UPDATE ayarlar SET {', '.join(guncellenecekler)} WHERE id = 1"
    cursor=mydb.cursor()
    cursor.execute(sorgu,tuple(degerler))
    mydb.commit()
    gecmis_ekle("Ayarlar guncellendi","Ayarlar basariyla guncellenmistir")
    return {"Durum" : "Ayarlar guncellendi", "Mesaj" : "Ayarlar basariyla guncellenmistir"}

@app.post("/sohbet")
def yapay_zekaya_sor(gonderilecek_metin):
    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=f"""Kullanicinin metnini '{gonderilecek_metin}' incele. Kullanicinin niyetine gore bir SQL sorgusu hazirla. SQL tablolarimi da sana olduğu gibi yollicam bunlara göre mantiğiyla dusun yaz. Dogrudan cursor.execute in icine yapistiricam o yuzden ek herhangi bi se yazma dogrudan cursor.execute(response.text) yazip icine atcam haberin olsun.Kullanıcı birden fazla şey sorarsa, kesinlikle noktalı virgülle birden çok sorgu yazma; hepsini tek bir SELECT sorgusunda alt sorgularla (subquery) birleştirerek getir. Ve aynı zamanda kullanici calisan ve yonetici bilgilerini asla kimseyle paylasma isim soyisim paylasabilirsin ancak email veya sifre paylasmiyosun. Sen kutuphane asistanisin ona gore davran.    
        CREATE TABLE IF NOT EXISTS public.ayarlar
(
    id serial NOT NULL,
    max_teslim_sure integer NOT NULL,
    ceza numeric(10,2) NOT NULL DEFAULT 14,
    alim_limit integer NOT NULL,
    CONSTRAINT ayarlar_pkey PRIMARY KEY (id)
)

public.calisanlar
(
    id serial NOT NULL,
    isim character varying(50) COLLATE pg_catalog."default" NOT NULL,
    soyisim character varying(50) COLLATE pg_catalog."default" NOT NULL,
    email character varying(250) COLLATE pg_catalog."default" NOT NULL,
    sifre character varying(255) COLLATE pg_catalog."default" NOT NULL,
    rol character varying(20) COLLATE pg_catalog."default" DEFAULT 'admin'::character varying,
    CONSTRAINT calisanlar_pkey PRIMARY KEY (id),
    CONSTRAINT calisanlar_email_key UNIQUE (email)
)

public.degerlendirmeler
(
    id serial NOT NULL,
    kitap_id integer,
    kullanici_id integer,
    puan integer,
    yorum text COLLATE pg_catalog."default",
    tarih timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT degerlendirmeler_pkey PRIMARY KEY (id),
    CONSTRAINT degerlendirmeler_kitap_id_fkey FOREIGN KEY (kitap_id)
        REFERENCES public.kitaplar (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT degerlendirmeler_kullanici_id_fkey FOREIGN KEY (kullanici_id)
        REFERENCES public.kullanicilar (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT degerlendirmeler_puan_check CHECK (puan >= 1 AND puan <= 5)
)

public.gecmis
(
    id serial NOT NULL,
    mesaj character varying(500) COLLATE pg_catalog."default" NOT NULL,
    aciklama character varying(500) COLLATE pg_catalog."default" NOT NULL,
    olusturulma_tarihi timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT gecmis_pkey PRIMARY KEY (id)
)



    CREATE TABLE IF NOT EXISTS public.kitaplar
(
    id serial NOT NULL,
    kitap_ismi character varying(150) COLLATE pg_catalog."default" NOT NULL,
    yazar character varying(200) COLLATE pg_catalog."default" NOT NULL,
    sayfa_sayisi integer,
    ekleyen_id integer,
    odunc_durumu boolean DEFAULT false,
    kategori character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT kitaplar_pkey PRIMARY KEY (id),
    CONSTRAINT kitaplar_ekleyen_id_fkey FOREIGN KEY (ekleyen_id)
        REFERENCES public.calisanlar (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL
)

public.kullanicilar
(
    id serial NOT NULL,
    isim character varying(50) COLLATE pg_catalog."default" NOT NULL,
    soyisim character varying(50) COLLATE pg_catalog."default" NOT NULL,
    email character varying(250) COLLATE pg_catalog."default" NOT NULL,
    sifre character varying(255) COLLATE pg_catalog."default" NOT NULL,
    rol character varying(20) COLLATE pg_catalog."default" DEFAULT 'uye'::character varying,
    guncel_ceza numeric(10,2) DEFAULT 0,
    CONSTRAINT kullanicilar_pkey PRIMARY KEY (id),
    CONSTRAINT kullanicilar_email_key UNIQUE (email)
)


    CREATE TABLE IF NOT EXISTS public.odunc_alinanlar
(
    id serial NOT NULL,
    kitap_id integer,
    kullanici_id integer,
    alinma_tarihi timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    son_teslim_tarihi timestamp with time zone NOT NULL,
    verilme_tarihi timestamp with time zone,
    CONSTRAINT odunc_alinanlar_pkey PRIMARY KEY (id),
    CONSTRAINT odunc_alinanlar_kitap_id_fkey FOREIGN KEY (kitap_id)
        REFERENCES public.kitaplar (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT odunc_alinanlar_kullanici_id_fkey FOREIGN KEY (kullanici_id)
        REFERENCES public.kullanicilar (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
    )

    public.yonetici
(
    id serial NOT NULL,
    isim character varying(50) COLLATE pg_catalog."default" NOT NULL,
    soyisim character varying(50) COLLATE pg_catalog."default" NOT NULL,
    email character varying(250) COLLATE pg_catalog."default" NOT NULL,
    sifre character varying(255) COLLATE pg_catalog."default" NOT NULL,
    rol character varying(20) COLLATE pg_catalog."default" DEFAULT 'yonetici'::character varying,
    CONSTRAINT yonetici_pkey PRIMARY KEY (id),
    CONSTRAINT yonetici_email_key UNIQUE (email)
)


    """
        )
    temiz_sql = response.text.replace("sql", "").replace("", "").strip()


    cursor=mydb.cursor()
    cursor.execute(temiz_sql)
    result=cursor.fetchall()
    response1 = client.models.generate_content(
            model="models/gemini-3.5-flash-lite",
            contents=f"{result} bu yazdigin responsein sonucu. {gonderilecek_metin} bu da kullanicinin istegiydi. Simdi elindeki verilerle kullanicinin sorusuna cevap ver. Ama yazdigin cevabi dogrudan gondericem kullaniciya ona gore yaz. Yani kullaniciya vericeğin cevap disi onlara herhangi bi ek bilgi veri verme cunku onlar musteri. O yuzden gereksiz :[]veya /n fln yazma gereksiz sadece guzel bi paragraf"
    )
    return response1.text
