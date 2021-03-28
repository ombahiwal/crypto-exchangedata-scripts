"""Kucoin v1 and v2
    Author  : Omkar Bahiwal
"""

import time
import requests
import sys
import json
import csv
import datetime
# import webbrowser
import email.utils
import codecs
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders as encoders
import pandas

# prototype (symbol, start, end, type)
# default BTC-USDT Json

def kucoin_get_klines_dict(symbol="ETH-BTC", start=str(int(time.time()) - (60*60*24*7)), end=str(int(time.time())), type='1day'):
    # print(int(time.time()))
    # 1 week
    # end = str(int(time.time()))
    # start = str(int(end) - (60*60*24*7))
    # symbol = "BTC-USDT"
    # type = '1day'
    url = "https://api.kucoin.com/api/v1/market/candles?type="+type+"&symbol="+symbol+"&startAt="+start+"&endAt="+end

    response = requests.get(url)
    data = response.json()
    # print(url, data['data'], len(data['data']))
    data = data['data']
    # print(len(data))


    final = []
    data_dict = {}
    data_dict['V2'] = {"URL": "https://trade.kucoin.com/" + symbol,
                       "Exchange": "Kucoin",
                       "Pair": symbol,
                       }
    # last week
    for i in range(0, len(data)-1):
        # for j in range(0, len(data[i])):
        vol_num = i
        if vol_num == 0:
            vol_num = "t"
        elif vol_num == 1:
            vol_num = "y"
        data_dict['V2']["vol"+str(vol_num)] = round(float(data[i][6]), 4) if float(data[i][6]) <= 100 else int(float(data[i][6]))


    data_dict['V2']['tgr'] = "red" if float(data[0][1]) > float(data[0][2]) else "green"

    # final.append(data_dict)
    # print(final[0]['V2'])
    # data_dict = {}
    data_dict['V1'] = {"URL": "https://trade.kucoin.com/" + symbol,
                       "Exchange": "Kucoin",
                       "Pair": symbol,
                       }
    # last week yesterday
    for i in range(1, len(data)):
        # for j in range(0, len(data[i])):
        vol_num = i
        if vol_num == 1:
            vol_num = "y"
        data_dict['V1']["vol"+str(vol_num)] = round(float(data[i][6]), 4) if float(data[i][6]) <= 100 else int(float(data[i][6]))

    # print(data)

    data_dict['V1']['ygr'] = "red" if float(data[1][1]) > float(data[1][2]) else "green"

    # final.append(data_dict)

    # print(final[1]['V1'])
    return data_dict


# print(kucoin_get_klines_dict('XMR-USDT'))


# fetch symbols - BTC+crypto, FIAT + crypto



def kucoin_get_symbol_list(symbol="BTC-USDT"):
    # print(int(time.time()))
    # 1 week
    # end = str(int(time.time()))
    # start = str(int(end) - (60*60*24*7))
    # symbol = "BTC-USDT"
    # type = '1day'
    symbol_list_url = "https://api.kucoin.com/api/v1/symbols"

    response = requests.get(symbol_list_url)
    data = response.json()
    # print(url, data['data'], len(data['data']))
    data = data['data']

    # return data


    btc_fiat_mirror_list = ['BTC','USDT','USDC','USDC','TUSD','PAX', 'DAI']

    sym_list = []

    sym = None
    for i in range(0, len(data)):
        sym = data[i]
        if sym['feeCurrency'] in btc_fiat_mirror_list:
            sym_list.append(sym['symbol'])

    return sym_list

# print(kucoin_get_symbol_list())
#
# for i in kucoin_get_symbol_list():
#     print(kucoin_get_klines_dict(i))

def kucoin_get_vols():
    # vols = []
    vols_dict_v1 = {}
    vols_dict_v2 = {}
    print('Using Kucoin Public API')
    t_calc = 0

    t_eta = 0

    klines_dict = {}
    sym_list = kucoin_get_symbol_list()
    t_count = len(sym_list)
    t_len = len(sym_list) - 1
    t_sum_eta = 0

    for sym in sym_list:
        # sym = sym_list[i]
        t_calc = time.time()
        try:
            klines_dict = kucoin_get_klines_dict(sym)
            vols_dict_v1[sym + "_V1"] = klines_dict['V1']
            vols_dict_v2[sym + "_V2"] = klines_dict['V2']
        except:
            print('API : Insufficient Data for ', sym)

        t_count = t_count - 1
        t_calc = time.time() - t_calc
        t_sum_eta = (round(float(t_calc * t_count), 2) + t_sum_eta)
        t_eta = round((t_sum_eta / (t_len - t_count if t_len-t_count != 0 else 1)), 2)
        # print(t_eta, t_len, t_calc, )
        sys.stdout.write('\r' + 'Fetching (ETA '+str(t_eta)+'s) : ' + sym)

    return (vols_dict_v1, vols_dict_v2)


def generate_json():

    (dictionary_v1, dictionary_v2) = kucoin_get_vols()
    sys.stdout.write('\rGenerating XLSX File...')
    (pandas.DataFrame(dictionary_v1).transpose()).to_excel('kucoin_data_v1.xlsx')
    (pandas.DataFrame(dictionary_v2).transpose()).to_excel('kucoin_data_v2.xlsx')

    sys.stdout.write('\rGenerating Json File...')
    # data_json = None
    # data_v1 = {}
    with open("kucoin_data_v1.json", "w") as outfile:
        # data_json = json.dumps(dictionary, sort_keys=True, indent=4)
        json.dump(dictionary_v1, outfile)
        sys.stdout.write('\rGenerated : kucoin_data_v1.json\n')

    with open("kucoin_data_v2.json", "w") as outfile:
        json.dump(dictionary_v2, outfile)
        sys.stdout.write('Generated : kucoin_data_v2.json')



def read_email_files():
    mail_cred = {}
    mail_list = []
    with open('./mail_cred.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            mail_cred['server'] = row['server']
            mail_cred['email'] = row['email']
            mail_cred['password'] = row['password']
            mail_cred['port'] = row['port']
            line_count += 1
        # print('Processed {line_count} lines.')
        csv_file.close()

    with open('./mail_list.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            mail_list.append(row['emails'])
        csv_file.close()

    return (mail_cred, mail_list)


def send_mail():
    sys.stdout.write('Initiating...')
    try:
        mail_cred, mail_list = read_email_files()
        receivers = mail_list
        sender = mail_cred['email']
        # print(mail_cred, mail_list)
        msg = MIMEMultipart('PFA - Kucoin ')
        msg.set_unixfrom('author')
        msg.set_charset('utf-8')

        # msg['To'] = email.utils.formataddr(('Recipients', 'bahiwal@aol.com'))
        msg['From'] = email.utils.formataddr((sys.argv[0], sender))
        msg['Subject'] = 'Data from Kucoin Script '+datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')

        sys.stdout.write('\r' + 'Processing...')

        files = ['kucoin_data_v1.json', 'kucoin_data_v2.json', 'kucoin_data_v1.xlsx', 'kucoin_data_v2.xlsx']
        for fn in files:
            if fn.split('.')[-1] == 'json':
                try:
                    filename = "./"+fn
                    with open(filename) as data_file:

                        data = json.load(data_file)
                    # print json.dumps(data)  # I tried to print here, and the output looks good, valid json.
                    f = codecs.open(filename, "r", "utf-8")
                    # f = file(filename)
                    attachment = MIMEText(f.read().rstrip("\n"), 'plain', 'utf-8')
                    attachment.add_header('Content-Disposition', 'attachment', filename=fn)
                    msg.attach(attachment)
                    print(fn + " Attached")
                    flag = True
                except Exception as e:
                    print(fn + " Not Attached",e)
            else:
                try:
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload(open('./'+fn, "rb").read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="'+fn+"\"")
                    msg.attach(part)
                    print(fn + " Attached")
                except Exception as e:
                    print(fn + " Not Attached")

        # sys.stdout.write('\r' + 'Connecting - '+mail_cred['server'])
        server = smtplib.SMTP(mail_cred['server'])
        # server = smtplib.SMTP(mail_cred['server'], int(mail_cred['port']))
        server.ehlo()
        # server.set_debuglevel('-d' in sys.argv)
        # sys.stdout.write('\r' + 'Checking Credentials - ' + sender)
        server.login(sender, mail_cred['password'])
        # sys.stdout.write('\r' + 'Sending Emails...')
        server.sendmail(sender, receivers, msg.as_string())
        sys.stdout.write('\r' + 'Sent!          \n')

    except Exception as e:
        print("Some Error Occured!", e)
    finally:
        server.quit()

def convert_json_to_xlsx():
    sys.stdout.write('\rGenerating XLSX File from Existing JSON...')

    try:
        (pandas.DataFrame(pandas.read_json('kucoin_data_v1.json').transpose())).to_excel('kucoin_data_v1.xlsx')
        print('\rGenerated kucoin_data_v1.json')
    except:
        print('kucoin_data_v1.json Not Found')

    try:
        (pandas.DataFrame(pandas.read_json('kucoin_data_v2.json').transpose())).to_excel('kucoin_data_v2.xlsx')
        print('\rGenerated kucoin_data_v2.json')
    except:
        print('kucoin_data_v2.json Not Found')



def main():
    if '-g' in sys.argv:
        generate_json()

    if '-ge' in sys.argv:
        generate_json()
        send_mail()

    if '--email' in sys.argv:
        print('- Email Routine - ')
        send_mail()

    if '-j2x' in sys.argv:
        print('- Json to XLSX - ')
        convert_json_to_xlsx()

    # send_mail()
    # webbrowser.open('mailto:?to=' + 'tset' + '&subject=' + 'test' + '&body=' + 'test', new=1)


if __name__ == "__main__":
    main()
