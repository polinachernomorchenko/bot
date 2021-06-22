import telebot
from telebot import types
import requests
import random
import json
import random
import markovify
from PIL import Image, ImageDraw, ImageFont
from pymorphy2 import MorphAnalyzer


bot = telebot.TeleBot('1792988792:AAF5reUA92SkReBsMs7E2yGzarUAPFat-A4')
m = MorphAnalyzer()
voc = ['а', 'о', 'у', 'и', 'ы', 'е', 'э', 'ю', 'я']
im_list = ['гора.jpg', 'фудзи.jpeg', 'animejpg.jpg', 'мост.jpg', 'город.jpg',
           'бамбук.jpg', 'гора2.jpg', 'вода.jpg', 'bamboo.jpeg']

with open('home/ofawkes/bot/mark_json.json', 'r', encoding='utf-8') as f:
    model_json = json.load(f)
    mark = markovify.Text.from_json(model_json)

with open('home/ofawkes/bot/hokky_dict.json', 'r', encoding='utf-8') as f:
    d = json.load(f)


def gen_text(mark, d):
    g = mark.make_sentence()
    if g:
        h = g.split()[:20]
    else:
        g = mark.make_sentence()
        h = g.split()[:17]

    # hh = [i for i in h if i != '.']
    # h = hh

    for i in range(len(h)):
        if h[i] in d:
            h[i] = random.choice(d[h[i]])

    return h


def gen_hokku(h, voc, w):
    c = 0
    b = ''
    end1 = 0
    end2 = 0
    end3 = 0
    for i in range(len(h)):
        for j in h[i]:
            if j in voc:
                c += 1
                if c == 7:
                    end1 = i
                elif c == 12:
                    end2 = i
                elif c == 19:
                    end3 = i

    lw = m.parse(h[end3-1])
    if lw[0].tag.POS in ['CONJ', 'PRCL', 'PREP']:
        end3 -= 1

    ht = h[:end3]
    wp = m.parse(w)
    w_list = []
    print(wp[0].tag)

    for i in ht:
        ip = m.parse(i)
        if ip[0].tag.POS == wp[0].tag.POS:   # если слово такой части речи есть в тексте, добавляем в рандомосписок
            w_list.append(ip)

    if w_list:
        ip = random.choice(w_list)
        if len(str(ip[0].tag).split()) > 1:   # если есть список, выбираем из него рандомное слово для замены и флексим так же
            a = str(ip[0].tag).split()[1]
            b = a.split(',')
        if b:
            for j in b:
                if wp[0].inflect({j}):
                    wp[0] = wp[0].inflect({j})

        if wp[0].tag.POS in ['NOUN', 'NPRO']:   # согласовать прилагательное перед новым существительным по роду
            ww = list(ip[0].word)
            for i in range(len(ww)):
                if ww[i] == 'ё':
                    ww[i] = 'е'
            ww = ''.join(ww)
            idx_h = h.index(ww) - 1
            if m.parse(h[idx_h])[0].tag.POS in ['ADJF', 'ADJS']:
                hhh = m.parse(h[idx_h])
                hhh = hhh[0].inflect({wp[0].tag.gender})
                hhh = hhh.inflect({wp[0].tag.number})
                hhh = hhh.inflect({wp[0].tag.case})
                h[idx_h] = hhh.word

    else:
        l_pos = [m.parse(i)[0].tag.POS for i in h]
        if wp[0].tag.POS == 'ADVB':
            for i in l_pos:
                if i in ['VERB', 'INFN', 'PRTF', 'PRTS']:
                    idx = l_pos.index(i)
                    h.insert(idx, wp[0].word)
                    break
        elif wp[0].tag.POS in ['ADJF', 'ADJS', 'COMP']:
            for i in l_pos:
                if i in ['NOUN', 'NPRO']:
                    idx = l_pos.index(i)
                    hip = m.parse(h[idx])
                    a = str(hip[0].tag).split()[1]
                    b = a.split(',')
                    r = str(hip[0].tag).split()[0].split(',')[-1]
                    b.append(r)
                    for j in b:
                        wp[0] = wp[0].inflect({j})

                    h.insert(idx, wp[0].word)
                    break

    ww = list(ip[0].word)
    for i in range(len(ww)):
        if ww[i] == 'ё':
            ww[i] = 'е'
    ww = ''.join(ww)
    idx = h.index(ww)
    h[idx] = wp[0].word

    for i in range(len(h)-5):
        if h[i] == '.':
            h[i-1] += '.'
            h.remove(h[i])
    if len(h[:end2]) > 5:
        end2 -= 1
    if len(h[:end3]) > 5:
        end3 -= 1

    s1 = ' '.join(h[:end1])
    s2 = ' '.join(h[end1:end2])
    s3 = ' '.join(h[end2:end3])
    hokku = '\n'.join([s1, s2, s3])

    return hokku


def gen_image(hokku, im_list):
    im_name = random.choice(im_list)
    im = Image.open('home/ofawkes/bot/pic/' + im_name)
    xi, yi = im.size
    x = round(xi/8)
    y = round(yi/5.3)
    sz = round(0.05*xi)
    font = ImageFont.truetype('manga.ttf', size=sz)
    print(im.size)
    draw_text = ImageDraw.Draw(im)
    draw_text.text((x, y), hokku, font=font)
    return im


@bot.message_handler(commands=['text'])
def txt(message):
    bot.send_message(message.chat.id, hokku)


@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    bot.send_message(message.chat.id, 'Привет! Я генерирую картинку с хокку по ведённому слову.\
                                      Чтобы получить только текст, воспользуйтесь командой /text после генерации картинки')


@bot.message_handler(content_types=['text'])
def txt(message):
    global w
    global hokku
    w = message.text
    h = gen_text(mark, d)
    hokku = gen_hokku(h, voc, w)
    global im
    im = gen_image(hokku, im_list)
    bot.send_photo(message.chat.id, im)


bot.polling(none_stop=True)
