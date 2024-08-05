import bs4 as bs
import urllib
import jellyfish as jf
import heapq
import urllib.request
import pandas as pd


KEYS_TO_SEARCH = None
with open("keywords.txt") as f:
    KEYS_TO_SEARCH = f.read().split('\n')

QUALIS_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vTZsntDnttAWGHA8NZRvdvK5A_FgOAQ_tPMzP7UUf-CHwF_3PHMj_TImyXN2Q_Tmcqm2MqVknpHPoT2/pubhtml?gid=0&single=true"

def get_table_rows_papers(soup):
    return soup.find_all(
        'table',
        {
            'cellpadding': '2',
            'cellspacing': '1',
            'align': 'center',
            'width': '100%'
        }
    )[0].find_all('tr')

def get_sail_and_full_name(td):
    raw_sail, full_name = td.text.strip().split("\n")
    sail = raw_sail.replace('2024','').strip()
    return sail, ' '.join([slice.strip() for slice in full_name.strip().split()])

def get_when_location_deadline(td):
    return td.text.strip().split("\n")

def treat_rows(rows):
    real_rows = rows[1:]
    pear_rows = [(real_rows[i], real_rows[i+1]) for i in range(0,len(real_rows)-1,2)]
    events = []
    for pear in pear_rows:
        sail, full_name = get_sail_and_full_name(pear[0])
        when, location, deadline = get_when_location_deadline(pear[1])
        link = get_link(pear[0])
        events.append({
            'sail': sail,
            'full_name': full_name,
            'when': when,
            'location': location,
            'deadline': deadline,
            'link': link,
        })
    return events

def get_wikicfp_data():
    str_keys = '+'.join(KEYS_TO_SEARCH)
    url = f"http://www.wikicfp.com/cfp/servlet/tool.search?q={str_keys}&year=f"
    print(url)
    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source,'lxml')
    return treat_rows(
        get_table_rows_papers(soup)
    )

def get_qualis(conference, conferences_qualis):
    qualis_to_conference = []
    for qualis in conferences_qualis:
        similarity = jf.levenshtein_distance(conference, qualis['full_name'])
        qualis_to_conference.append({
            **qualis,
            'similarity': similarity,
        })
    return heapq.nsmallest(1, qualis_to_conference, lambda x: x['similarity'])[0]

def get_raw_qualis_data():
    source = urllib.request.urlopen(QUALIS_URL).read()
    qualis_data = bs.BeautifulSoup(source, 'lxml')
    data = []
    for row in qualis_data.find('tbody'):
        raw_sail, raw_full_name, raw_qualis = row.find_all('td')
        data.append({
            'sail': raw_sail.text,
            'full_name': ' '.join([slice.strip() for slice in raw_full_name.text.strip().split()]),
            'qualis': raw_qualis.text,
        })
    return data

def get_link(pear):
    link = pear.find_all('a', href=True)[0]['href']
    print(f'http://www.wikicfp.com{link}')
    source = urllib.request.urlopen(f'http://www.wikicfp.com{link}').read()
    soup = bs.BeautifulSoup(source,'lxml')
    a = soup.find_all('a', target='_newtab')[0]
    return a['href']

def get_qualis_data(conferences):
    conferences_with_qualis = []
    conferences_qualis = get_raw_qualis_data()
    for conference in conferences:
        qualis = get_qualis(conference=conference['full_name'], conferences_qualis=conferences_qualis)
        # print(qualis)
        conferences_with_qualis.append({
            **conference,
            'qualis': qualis['qualis'],
            '_full_name': qualis['full_name'],
            'similarity': qualis['similarity'],
            '_sail': qualis['sail'],
        })    
    return conferences_with_qualis

def to_date(date_str):
    if date_str == "N/A":
        return None
    return pd.to_datetime(date_str, errors='coerce')

def generate_table():
    conferences = get_wikicfp_data()
    # print(conferences)
    conferences_with_qualis = get_qualis_data(conferences=conferences)
    # print(conferences_with_qualis[3])
    df = pd.DataFrame(conferences_with_qualis).sort_values(by='deadline', ascending=True)
    df['when_start'] = df['when'].apply(lambda row: to_date(row.split(" - ")[0]) if row != "N/A" else None)
    df['when_end'] = df['when'].apply(lambda row: to_date(row.split(" - ")[1]) if row != "N/A" else None)
    df['deadline'] = df['deadline'].apply(lambda row: to_date(row))
    df = df.drop(columns=['when']).sort_values(by='deadline')
    df.to_csv('qualis_table.csv', index=False)

def main():
    generate_table()

if __name__ == '__main__':
    main()