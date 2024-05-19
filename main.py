import os
import re
import requests
import subprocess
from time import sleep

version = "v1.5"
print("Starting CertRenewer " + version)

def read_command_output(process, lines):
    i=0
    command_response = []
    while i<lines:
        line = process.stdout.readline()
        if not line:
            break
        command_response.append(line.decode())
        i+=1
    return " ".join(command_response)

def get_txt_token(text):
    regular_expression = r'[^\s]{38,47}'
    search_result = re.search(regular_expression, text)
    if search_result != None:
        txt_token = search_result.group()
        return txt_token
    print("ERROR: Fail to get token")
    raise

def add_token_dns_record(token):
    params = {
        'key': os.getenv('API_KEY'),
        'command': 'set_dns2',
        'domain': 'linepixer.com',
        'subdomain1':'_acme-challenge',
        'sub_record_type1':'txt',
        'sub_record1':token,
        'add_dns_to_current_setting':'1'
        }
    response = requests.get(f'https://api.dynadot.com/api3.json', params=params)
    if response.status_code == 200:
        response_code = response.json().get('SetDnsResponse', {}).get('ResponseCode')
        if response_code == 0:
            print("INFO: Token added to dns records >>", token)
            return
        else:
            print("ERROR: Fail to add dns record (response code != 0)")
            raise
    else:
        print("ERROR: Fail to add dns record (response status != 200)")
        raise

def restore_records():
    public_ip = requests.get("https://ipinfo.io/json", verify = True).json()['ip']
    params = {
            'key': os.getenv('API_KEY'),
            'command': 'set_dns2',
            'domain': 'linepixer.com',
            'main_record_type0': 'a',
            'main_record0':public_ip,
            'main_record_type1':'mx',
            'main_record1':'mx.zoho.com',
            'main_recordx1':'10',
            'main_record_type2':'mx',
            'main_record2':'mx2.zoho.com',
            'main_recordx2':'20',
            'main_record_type3':'mx',
            'main_record3':'mx3.zoho.com',
            'main_recordx3':'50',
            'main_record_type4':'txt',
            'main_record4':'v=spf1 include:zohomail.com ~all',
            'subdomain1':'www',
            'sub_record_type1':'a',
            'sub_record1':public_ip,
            'subdomain2':'cloud',
            'sub_record_type2':'a',
            'sub_record2':public_ip,
            'subdomain3':'play',
            'sub_record_type3':'a',
            'sub_record3':public_ip,
            'subdomain4':'local',
            'sub_record_type4':'a',
            'sub_record4':'192.168.1.250',
            'subdomain5':'zmail._domainkey',
            'sub_record_type5':'txt',
            'sub_record5':'v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCfg3Wi1CNsx0kNG2Pd45uCvXhjItjWVNbXSD3NyRv/t+D4PdVUe7JT3QFmkhrOdTvCM+i3OVGqHguzMRLD7CjDkAsmcEvMP0yrn3L8GdSDzz+TNb5CT8DLGEYJAL5pIJQEDYInNuHVsziqpNwL9zACZeJ0JbKn+OhP2G74IYEIdwIDAQAB',
            'subdomain6':'_dmarc',
            'sub_record_type6':'txt',
            'sub_record6':'v=DMARC1; p=quarantine; rua=mailto:diazmatias@linepixer.com; ruf=mailto:diazmatias@linepixer.com; sp=quarantine; adkim=r; aspf=r',
            'ttl':'300'
            }
    response = requests.get(f'https://api.dynadot.com/api3.json', params=params)
    if response.status_code == 200:
        response_code = response.json().get('SetDnsResponse', {}).get('ResponseCode')
        if response_code == 0:
            print("INFO: dns records restored")
            return
        else:
            print("ERROR: Fail to update dns records (response code != 0)")
            raise
    else:
        print("ERROR: Fail to update dns records (response code != 200)")
        raise

if __name__ == "__main__":
    renew_command = "certbot certonly --manual --keep --preferred-challenges dns --email diazmatias@linepixer.com --agree-tos --no-eff-email --cert-name 'LinepixerCertificates' -d '*.linepixer.com'"
    while True:
        renew_process = subprocess.Popen(renew_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        command_response = read_command_output(renew_process, 15)
        if not "Certificate not yet due for renewal" in command_response:
                print("INFO: Initiating necessary renewal of certificates")
                try:
                    txt_token = get_txt_token(command_response)
                    add_token_dns_record(txt_token)
                    sleep(300)
                    renew_process.stdin.write(b'\n')
                    renew_process.stdin.flush()
                    command_response = read_command_output(renew_process, 10)
                    print(command_response)
                    restore_records()
                    print("SUCCESS: Certificates generated or renewed")
                except:
                    print("ERROR: Unhandled exception, restoring dns records")
                    restore_records()
                    print("INFO: Successful recovery")
        else:
            print("INFO: Renewal is not necessary")
        sleep(86400)
