# Crypto Exchanges API Scraper
##### Supported API

- Binance v3
- Kucoin v1

##### Features

- Fetch and Generate Volumes of All API listed Symbols
- Send The Generated files as attachment to multiple emails using SMTP.
- Convert Json to Xlsx Files.

##### Dependencies

- Default : time datetime sys json codec requests
- Email : smtplib email.mime.multipart email.mime.text
- Data : pandas openpyxl


## Installation

This script requires Python v2.7+ to run.
Install these dependencies to run the script.

```sh
pip install pandas openpyxl
pip install time datetime sys json codec requests
pip install email email.utils smtplib
```

## Email Configuration

To configure the mailer feature, add two files in the same directory of the script
##### mail_cred.csv
the file should be in such format
| server     | email | password     | port |
| :---        |    :----:   |  :----:   |   ---: |
| smtp.test.com      | test@test.com       | testpass123   | 587|

##### mail_list.csv
this file is the list of recipients in a vertical format
| emails    |
| --- |
| recipient1@test.com |
| recipient2@test.com |
| ... |
| recipientsN@test.com |


## Functions
script.py can be binance.py or kucoin.py


#####  Plain Run
this will generate two json files _v1.json and _v2.json

```sh
python script.py -g
```

#####  Generate and Send Email
this will generate two json and two xlsx files, attach them and send to recipients

```sh
python script.py -ge
```

#####  Send Email
this will attach already generated files and send email to the recipients

```sh
python script.py --email
```

#####  Convert Json to Xlsx
This will convert the already generated json files to xlsx files
```sh
python script.py --j2x
```


######  "Thanks"
*written for A.O.*
Author : Omkar B