"""uniswap Data using Public API"""
"""
    Author  : Omkar Bahiwal
"""
import time
import datetime
import requests
import sys
import json
import csv
# import webbrowser
# import email.utils
import codecs
import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email.encoders import Encoders as encoders
import pandas


# import getpass

# print(sys.argv)




url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

def uniswap_get_klines_dict(symbol_id="0xa478c2975ab1ea89e8196811f51a7b7ade33eb11", urlsym="BTC_USDT",start=int((time.time()) - (7 * 86400) ), days=7, type='1d'):

    url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
    seven_day_query = """{
             pairDayDatas(first: %s, orderBy: date, orderDirection: asc,
           where: {
             pairAddress: "%s",
             date_gt: %s
           }
         ) {
             token0{
             id
             symbol
             }
             token1{
             id
             symbol
             }
             date
             dailyVolumeToken0
             dailyVolumeToken1
             dailyVolumeUSD
             reserveUSD
         }
    }""" % (days, symbol_id, start)
    # print(symbol_id)
    r = requests.post(url, json={'query': seven_day_query})
    # print(r.json()['data']['pairDayDatas'])
    data = r.json()['data']['pairDayDatas']
    # print(url, data['data'], len(data['data']))
    # data = data
    # print(data)
    # print('DATA LEN ', len(data))
    # invert array
    data.reverse()
    counter = len(data)



    if counter < days:
        seven_day_query = """{
                     pairDayDatas(first: %s, orderBy: date, orderDirection: asc,
                   where: {
                     pairAddress: "%s",
                     date_gt: %s
                   }
                 ) {
                     token0{
                     id
                     symbol
                     }
                     token1{
                     id
                     symbol
                     }
                     date
                     dailyVolumeToken0
                     dailyVolumeToken1
                     dailyVolumeUSD
                     reserveUSD
                 }
            }""" % (days, symbol_id, start)
        url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
        # "&startTime=" + start + "&endTime="+end
        response = requests.get(url)
        data = r.json()['data']['pairDayDatas']
        # print data, len(data)
        data.reverse()
        # counter = days if len(data) >= days else 0
    # print(counter, data)
    if counter < days:
        # print("API - Insufficient Data for "+symbol)
        raise TypeError("Insufficient Data for " + urlsym)

    urlsym = data[0]['token0']['symbol'] + "/" + data[0]['token1']['symbol']
    data_dict = {}
    data_dict['V2'] = {"URL": "https://info.uniswap.org/pair/" + symbol_id,
                           "Exchange": "uniswap",
                           "Pair": urlsym,
                        }
    # last week

    for i in range(0, counter-1):
        # for j in range(0, len(data[i])):
        vol_num = i
        if vol_num == 0:
            vol_num = "t"
        elif vol_num == 1:
            vol_num = "y"
        data_dict['V2']["vol" + str(vol_num)] = round(float(data[i]['dailyVolumeToken1']), 4) if float(data[i]['dailyVolumeToken1']) <= 100 else int(float(data[i]['dailyVolumeToken1']))

    data_dict['V2']['tgr'] = get_token_candle_color(data[0]['token0']['id'], data[0]['date'], data[1]['date'])

    data_dict['V1'] = {"URL": "https://info.uniswap.org/pair/" + symbol_id,
                       "Exchange": "uniswap",
                       "Pair": urlsym,
                       }
    # last week yesterday

    for i in range(1, counter):
        # for j in range(0, len(data[i])):
        vol_num = i
        if vol_num == 1:
            vol_num = "y"

        data_dict['V1']["vol" + str(vol_num)] = round(float(data[i]['dailyVolumeToken1']), 4) if float(data[i]['dailyVolumeToken1']) <= 100 else int(float(data[i]['dailyVolumeToken1']))

    data_dict['V1']['ygr'] = get_token_candle_color(data[0]['token0']['id'], data[1]['date'], data[2]['date'])

    return data_dict



def get_token_candle_color(id="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", t2=1616976000, t1=1617148800):

    # token price against USD

    query_token_price1 = """{
         tokenDayDatas(first:1, orderBy: date, orderDirection: asc,
          where: {
            token: "%s" 
            date: %s
          }
         ) {
            id
            date
            priceUSD
            totalLiquidityToken
            totalLiquidityUSD
            totalLiquidityETH
            dailyVolumeETH
            dailyVolumeToken
            dailyVolumeUSD
            token {
              id
              symbol
            }
         }
        }
    """ % (id, t1)

    query_token_price2 = """{
         tokenDayDatas(first:7, orderBy: date, orderDirection: asc,
          where: {
            token: "%s" 
            date: %s
          }
         ) {
            id
            date
            priceUSD
            totalLiquidityToken
            totalLiquidityUSD
            totalLiquidityETH
            dailyVolumeETH
            dailyVolumeToken
            dailyVolumeUSD
            token {
              id
              symbol
            }
         }
        }

    """ % (id, t2)
    # return color for t1 < t2
    return "red" if float(requests.post(url, json={'query': query_token_price1}).json()['data']['tokenDayDatas'][0]['priceUSD']) < float(requests.post(url, json={'query': query_token_price2}).json()['data']['tokenDayDatas'][0]['priceUSD']) else "green"
    # return "-"

def uniswap_get_symbol_list(num=100):
    uniswap_symbol_list_query = """
           {
         pairs(first: %s, orderBy: reserveUSD, orderDirection: desc) {
           id
            token0{
             symbol
            }
            token1{
            symbol
            }
         }
        }   
    """ % num

    r = requests.post(url, json={'query': uniswap_symbol_list_query})
    # print(r.json()['data']['pairDayDatas'])
    ids = []
    sym = []
    # print(len(data), data)
    for d in r.json()['data']['pairs']:
        ids.append(d['id'])
        sym.append(d['token0']['symbol']+"/"+d['token1']['symbol'])
    return  (ids, sym)

def uniswap_get_vols():
    # vols = []
    vols_dict_v1 = {}
    vols_dict_v2 = {}
    print('Using uniswap Public API')
    sys.stdout.write('\r' + 'Getting Symbol List...')

    t_calc = 0

    t_eta = 0

    klines_dict = {}
    sym_list, symbols = uniswap_get_symbol_list()
    sys.stdout.write('\r' + 'Top 100 Symbol List!\n')

    t_count = len(sym_list)
    t_len = t_count - 1
    t_sum_eta = 0
    # len(sym_list)
    for i in range(0, len(sym_list)):
        sym = sym_list[i]
        t_calc = time.time()
        t_count = t_count - 1

        try:
            klines_dict = uniswap_get_klines_dict(sym)
            vols_dict_v1[symbols[i]+"_V1"] = klines_dict['V1']
            vols_dict_v2[symbols[i]+"_V2"] = klines_dict['V2']
            t_calc = time.time() - t_calc
            t_sum_eta = (round(float(t_calc * t_count), 2) + t_sum_eta)
            t_eta = round((t_sum_eta / (t_len - t_count if t_len - t_count != 0 else 1)), 2)
            # print(t_eta, t_len, t_calc, )
            sys.stdout.write('\r' + 'Fetching (ETA ' + str(t_eta) + 's) : ' + symbols[i])

        except Exception as e:
            print('\nAPI : Insufficient Data for ' + symbols[i] + ' at https://info.uniswap.org/pair/' + sym)


    return (vols_dict_v1, vols_dict_v2)


# print(len(uniswap_get_symbol_list()))

def generate_json():

    (dictionary_v1, dictionary_v2) = uniswap_get_vols()
    sys.stdout.write('\rGenerating XLSX File...')
    (pandas.DataFrame(dictionary_v1).transpose()).to_excel('uniswap_data_v1.xlsx')
    (pandas.DataFrame(dictionary_v2).transpose()).to_excel('uniswap_data_v2.xlsx')
    sys.stdout.write('\rGenerated XLSX Files.')

    sys.stdout.write('\rGenerating Json File...')
    # data_json = None
    # data_v1 = {}
    # (pandas.DataFrame(pandas.read_json("kucoin_data_v1.json")).transpose()).to_excel("output.xlsx")

    with open("uniswap_data_v1.json", "w") as outfile:
        # data_json = json.dumps(dictionary, sort_keys=True, indent=4)
        json.dump(dictionary_v1, outfile)
        sys.stdout.write('\rGenerated : uniswap_data_v1.json\n')

    with open("uniswap_data_v2.json", "w") as outfile:
        json.dump(dictionary_v2, outfile)
        sys.stdout.write('Generated : uniswap_data_v2.json')
    print()

def convert_json_to_xlsx():
    sys.stdout.write('\rGenerating XLSX File from Existing JSON...')

    try:
        (pandas.DataFrame(pandas.read_json('uniswap_data_v1.json').transpose())).to_excel('uniswap_data_v1.xlsx')
        print('\rGenerated uniswap_data_v1.json')
    except:
        print('uniswap_data_v1.json Not Found')

    try:
        (pandas.DataFrame(pandas.read_json('uniswap_data_v2.json').transpose())).to_excel('uniswap_data_v2.xlsx')
        print('\rGenerated uniswap_data_v2.json')
    except:
        print('uniswap_data_v2.json Not Found')


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
    import email.utils
    import email
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    # from email import Encoders as encoders
    sys.stdout.write('Initiating...')
    flag = False
    try:
        mail_cred, mail_list = read_email_files()
        receivers = mail_list
        sender = mail_cred['email']
        # print(mail_cred, mail_list)
        msg = MIMEMultipart('PFA-uniswap.')
        msg.set_unixfrom('author')
        msg.set_charset('utf-8')

        # msg['To'] = email.utils.formataddr(('Recipients', 'bahiwal@aol.com'))
        msg['From'] = email.utils.formataddr((sys.argv[0], sender))

        msg['Subject'] = 'Data from uniswap Script '+datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')

        sys.stdout.write('\r' + 'Processing...\n')

        files = ['uniswap_data_v1.json', 'uniswap_data_v2.json', 'uniswap_data_v1.xlsx','uniswap_data_v2.xlsx']
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
                    email.encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="'+fn+"\"")
                    msg.attach(part)
                except Exception as e:
                    print(fn + " Not Attached")

        if flag:
            # sys.stdout.write('\r' + 'Connecting - '+mail_cred['server'])
            server = smtplib.SMTP(mail_cred['server'])
            # server = smtplib.SMTP(mail_cred['server'], int(mail_cred['port']))
            server.ehlo()
            server.starttls()
            server.ehlo()
            # server.set_debuglevel('-d' in sys.argv)
            # sys.stdout.write('\r' + 'Checking Credentials - ' + sender)
            server.login(sender, mail_cred['password'])
            # sys.stdout.write('\r' + 'Sending Emails...')
            server.sendmail(sender, receivers, msg.as_string())
            sys.stdout.write('\r' + 'Sent!          \n')
        else:
            sys.stdout.write('\r' + 'Mail not Sent!          \n')
    except Exception as e:
        print("Some Error Occured!", e)
    finally:
        try:
            server.quit()
        except:
            print('')



def main():
    if '-g' in sys.argv:
        generate_json()

    if '-ge' in sys.argv:
        generate_json()
        send_mail()

    if '--email' in sys.argv:
        print('- Email Routine - ')
        send_mail()

    if '--j2x' in sys.argv:
        print('- Json to XLSX - ')
        convert_json_to_xlsx()


    # send_mail()

    # webbrowser.open('mailto:?to=' + 'tset' + '&subject=' + 'test' + '&body=' + 'test', new=1)


if __name__ == "__main__":
    main()
