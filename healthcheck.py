#Import required libraries
import sys
import yaml
import requests
import time
from urllib.parse import urlparse
import math

def parse_yaml(filename):
    with open(filename,"r") as file:
        try:
            yaml_data = yaml.safe_load(file)
            url_groups = {}
            for entry in yaml_data:
                url = entry.get('url')
                headers = entry.get('headers', {})
                method = entry.get('method', 'GET')
                name = entry.get('name')
                body = entry.get('body', {})
                
                if url:
                    if url not in url_groups:
                        url_groups[url] = []
                    
                    url_groups[url].append({
                        'headers': headers,
                        'method': method,
                        'name': name,
                        'body': body
                    })
            
            data = []
            # Process the grouped data
            for url, group in url_groups.items():
                temp = {}
                temp['url'] = url
                # print("URL:", url)
                for item in group:
                    temp['headers'] = item['headers']
                    temp['method'] = item['method']
                    temp['name']= item['name']
                    temp['body'] = item['body']
                temp['up'] = 0
                temp['down'] = 0
                data.append(temp)
            
            return data

        except yaml.YAMLError as exc:
            print(exc)            

def health_check(endpoint):
    if endpoint['method'] == 'POST':
        response = requests.post(url=endpoint['url'], headers=endpoint['headers'], data=endpoint['body'])
        if (response.status_code >= 200 and response.status_code < 300) and (response.elapsed.total_seconds() * 1000 < 500):
            endpoint['up'] += 1
        else:
            endpoint['down'] += 1
    else:
        response = requests.get(url=endpoint['url'], headers=endpoint['headers'], data=endpoint['body'])
        if (response.status_code >= 200 and response.status_code < 300) and (response.elapsed.total_seconds() * 1000 < 500):
            endpoint['up'] += 1
        else:
            endpoint['down'] += 1

def log_results(data, domains):
    for domain in domains:
        count_up = 0
        count_down = 0
        for d in data:
            if domain in d['url']:
                count_up += d['up']
                count_down += d['down']
        result = round(100 * (count_up/(count_up+count_down)))
        print(f"{domain} has {result} availibility percentage")


    

def main():
    if len(sys.argv) < 2:
        print("No filename provided Exiting!")
        return
    else:
        filename = sys.argv[1]
        data = parse_yaml(filename)
        domains = {urlparse(d['url']).netloc for d in data}
        while True:
            for d in data:
                health_check(d)
            log_results(data,domains)
            time.sleep(15)


if __name__ == "__main__":
    main()
