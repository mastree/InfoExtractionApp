import os.path
import re
import nltk
# nltk.download()

# abcdkonabcd
# 0 0 0 0 0 0 0 1 2 3 4

teks_test = '''
421 Orang di Jabar Terkonfirmasi Positif COVID-19
Yudha Maulana - detikNews
Sabtu, 11 Apr 2020 20:07 WIB
Bandung - Angka positif virus Corona atau COVID-19 di Jawa Barat menembus angka 400 kasus. Laman Pusat Informasi dan Koordinasi COVID-19 Jabar (Pikobar) pada Sabtu (11/4/2020) pukul 18.43 WIB, mencatat terdapat 421 orang yang terkonfirmasi positif COVID-19.
Dibandingkan sehari sebelumnya, jumlah tercatat yaitu 388 orang. Terjadi penambahan 8,5 persen atau 33 kasus per harinya. Sementara itu, secara nasional terdapat 3.842 kasus positif COVID-19.
Dari 421 kasus tersebut, 40 orang meninggal dunia dengan keterangan terpapar COVID-19. Sedangkan, angka kesembuhan di Jabar masih tetap berada di angka 19 orang.
Per hari jumlah Orang Dalam Pemantauan (ODP) di Jabar mencapai 28.775 orang. Sebanyak 15.363 di antaranya masih menjalani proses pemantauan dan 13.412 orang lainnya telah selesai menjalani proses pemantauan.
Sementara itu jumlah Pasien Dalam Pengawasan (PDP) mencapai 2.278 orang. Tercatat 1.344 orang masih menjalani proses pengawasan dan 934 orang lainnya telah selesai menjalani proses pengawasan.
'''
# MetaCharacters (Need to be escaped):
# . ^ $ * + ? { } [ ] \ | ( )

INFINITE = 1000000000

dd = r'(\d{1,2})'
mm = r'(\d{1,2})'
yy = r'(\d{4})'

day = r'(senin|selasa|rabu|kamis|jumat|sabtu|minggu)'
month = r'''(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember|
jan|feb|mar|apr|mei|jun|jul|aug|sep|okt|nov|des)''' 
tanggal = r'(({dd}(/|-)({mm}|{month})(/|-){yy})|({dd}\s{month}\s{yy}))'.format(dd = dd, day = day, mm = mm, month = month, yy = yy)

time_zone = r'(WIB|WITA|WIT|UTC)'
hh_mm = r'(([0-1][0-9]|2[0-3])(:|\.)[0-5][0-9])'
waktu = r'({hh_mm}\s{time_zone})'.format(hh_mm = hh_mm, time_zone = time_zone)

integer = r'([1-9]\d*|0)'
biginteger = r'([1-9]\d{0,2}(\.\d{3})*)'
angka = r'({integer},\d+|{biginteger}|{integer})'.format(integer = integer, biginteger = biginteger) # koma = ','

def prefixFunc(s):
    n = len(s)
    pref = []   
    pref.append(0)
    le = 0
    
    for ri in range(1, n):
        while (s[le] != s[ri] and le != 0): 
            le = pref[le - 1]
        if (s[le] == s[ri]):
            le += 1
        pref.append(le)
    return pref

def KMP(s1, s2): # finding pattern s1 in s2
    s1 = s1.lower()
    s2 = s2.lower()
    pref = prefixFunc(s1)
    le = 0
    len1 = len(s1)
    len2 = len(s2)

    result = []
    for ri in range(0, len2):
        while (s1[le] != s2[ri] and le != 0):
            le = pref[le - 1]
        if (s1[le] == s2[ri]):
            le += 1
        if (le == len1):
            result.append((ri - len1 + 1, ri + 1))
            le = pref[le - 1]
            # le = 0
    return result

def boyerMoore(s1, s2): # finding pattern s1 in s2
    s1 = s1.lower()
    s2 = s2.lower()
    len1 = len(s1)
    len2 = len(s2)
    last = [len1] * 256

    result = []
    for i in range(len2):
        last[ord(s2[i])] = i
    
    p = 0
    while (p + len1 <= len2):
        salah = len1 - 1
        while (salah >= 0):
            if (s1[salah] == s2[p + salah]):
                salah -= 1
            else:
                break
        if (salah < 0):
            result.append((p, p + len1))
            if (p + len1 >= len2):
                break
            p += max(1, len1 - last[ord(s2[p + len1])])
        else:
            p += max(1, salah - last[ord(s2[p + salah])])
    return result

def regex(s1, s2): # finding pattern s1 in s2
    s1 = s1.lower()
    s2 = s2.lower()
    temp = re.finditer(s1, s2)
    result = []
    for match in temp:
        result.append((match.start(), match.end()))
    return result

def cheat(s1, s2):
    s1 = r' ({s1}) '.format(s1 = s1)
    pat = re.compile(s1, re.I)
    temp = pat.finditer(s2)
    result = []
    for match in temp:
        result.append((match.start(), match.end()))
    return result

def findNearest(x, arr):
    temp = []
    for elmt in arr:
        if (x[1] <= elmt[0] + 1):
            temp.append((elmt[0] - x[1] + 1, elmt))
        elif (elmt[1] <= x[0] + 1):
            temp.append((x[0] - elmt[1] + 1, elmt))

    if (len(temp) == 0):
        return None
    temp.sort()
    return temp[0][1]

def textToCanonical(teks):
    result = []
    sents = nltk.sent_tokenize(teks)
    for sent in sents:
        result.append(nltk.word_tokenize(sent))
    return result

def intersect(pos1, pos2):
    if (pos1[1] < pos2[0]):
        return False
    if (pos1[0] > pos2[1]):
        return False
    return True

def findKeyword(pattern, text, algo): # algo kmp, bm, regex
    sents = nltk.sent_tokenize(text)
    text = textToCanonical(text)
    resOfDay = []
    resOfAlgo = []
    resOfDate = []
    resOfTime = []
    resOfNum = []

    result = []

    hariArtikel = '-'
    tanggalArtikel = '-'
    jamArtikel = '-'
    artIdx = -1

    idx = 0
    for sent in text:
        temp = ' '
        for word in sent:
            temp = temp + word + ' '
        if (algo == 'kmp'):
            resOfAlgo.append(KMP(pattern, temp))
        elif (algo == 'bm'):
            resOfAlgo.append(boyerMoore(pattern, temp))
        else:
            resOfAlgo.append(regex(pattern, temp))

        resOfDay.append(cheat(day, temp))
        resOfDate.append(cheat(tanggal, temp))
        resOfTime.append(cheat(waktu, temp))
        resOfNum.append(cheat(angka, temp))

        numLen = len(resOfNum[idx])
        dateLen = len(resOfDate[idx])
        timeLen = len(resOfTime[idx])
        # Eliminate intersection
        for i in range(numLen):
            for j in range(dateLen):
                if (intersect((resOfNum[idx][i][0] + 1, resOfNum[idx][i][1] - 2), (resOfDate[idx][j][0] + 1, resOfDate[idx][j][1] - 2))):
                    resOfNum[idx][i] = (-INFINITE, INFINITE)
                    break
            for j in range(timeLen):
                if (intersect((resOfNum[idx][i][0] + 1, resOfNum[idx][i][1] - 2), (resOfTime[idx][j][0] + 1, resOfTime[idx][j][1] - 2))):
                    resOfNum[idx][i] = (-INFINITE, INFINITE)
                    break

        for x in resOfAlgo[idx]:
            rangeOfDay = findNearest(x, resOfDay[idx])
            rangeOfDate = findNearest(x, resOfDate[idx])
            rangeOfTime = findNearest(x, resOfTime[idx])
            rangeOfNum = findNearest(x, resOfNum[idx])

            jumlah = '-'
            if (rangeOfNum != None):
                jumlah = temp[rangeOfNum[0] + 1:rangeOfNum[1] - 1]
            waktu_ = '-'
            if (rangeOfDay != None):
                waktu_ = temp[rangeOfDay[0] + 1:rangeOfDay[1] - 1]
            if (rangeOfDate != None):
                if (waktu_ == '-'):
                    waktu_ = temp[rangeOfDate[0] + 1:rangeOfDate[1] - 1]
                else:
                     waktu_ = waktu_ + ' ' + temp[rangeOfDate[0] + 1:rangeOfDate[1] - 1]
            if (rangeOfTime != None):
                if (waktu_ == '-'):
                     waktu_ = temp[rangeOfTime[0] + 1:rangeOfTime[1] - 1]
                else:
                     waktu_ = waktu_ + ' ' + temp[rangeOfTime[0] + 1:rangeOfTime[1] - 1]

            result.append(
                {
                    'keyword': pattern,
                    'jumlah': jumlah,
                    'waktu': waktu_,
                    'kalimat': sents[idx]
                }
            )
        if (hariArtikel == '-' and len(resOfDay[idx]) > 0 and artIdx == -1):
            hariArtikel = temp[resOfDay[idx][0][0] + 1: resOfDay[idx][0][1] - 1]
            artIdx = idx
        if (tanggalArtikel == '-' and len(resOfDate[idx]) > 0 and (artIdx == -1 or artIdx == idx)):
            tanggalArtikel = temp[resOfDate[idx][0][0] + 1: resOfDate[idx][0][1] - 1]
            artIdx = idx
        if (jamArtikel == '-' and len(resOfTime[idx]) > 0 and (artIdx == -1 or artIdx == idx)):
            jamArtikel = temp[resOfTime[idx][0][0] + 1: resOfTime[idx][0][1] - 1]
            artIdx = idx
        idx += 1
    
    artikel = '-'
    if (hariArtikel != '-'):
        artikel = hariArtikel
    if (tanggalArtikel != '-'):
        if (artikel == '-'):
            artikel = tanggalArtikel
        else:
                artikel = artikel + ' ' + tanggalArtikel
    if (jamArtikel != '-'):
        if (artikel == '-'):
                artikel = jamArtikel
        else:
                artikel = artikel + ' ' + jamArtikel
    idx = len(result)
    for i in range(idx):
        if (result[i]['waktu'] == '-'):
            result[i]['waktu'] = artikel

    return result
