import json
import re
import matplotlib.pyplot as plt
import pycountry
import pycountry_convert as pc
from collections import defaultdict

class DataGetter():
    def __init__(self,file_path) -> None:
        self.file_path = file_path
        self.data = self.__load_data()
        self.countries = self.countries_data()
        self.countries_list = self.__countries_list()
        

    def __load_data(self):
        data = []
        with open(self.file_path, 'r') as file:
            data = [json.loads(line) for line in file]
        return data
    def __countries_list(self):
        data = []
        for i in self.data:
            country = i['visitor_country']
            data.append(country)
        return data
    
    def __code_to_continent(self,country_code):
        try:
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            continent_name = pc.convert_continent_code_to_continent_name(continent_code)
            return continent_name
        except Exception as e:
            #print(f"Error: {e}")
            return "Unknown Region"
    
    def countries_data(self):
        data = {}
        for i in self.data:
            country = i['visitor_country']
            if country in data.keys():
                data[country]+=1
            else:
                data[country]=1
        return data
    
    
    def continent_data(self):
        data={}
        for country_code in self.countries_list:
            continent = self.__code_to_continent(country_code)
            if continent in data.keys():
                data[continent]+=1
            else:
                data[continent]=1
        return data
    def __identify_browser(self,user_agent):
        if re.search(r'Chrome', user_agent):
            return 'Google Chrome'
        elif re.search(r'Safari', user_agent) and re.search(r'AppleWebKit', user_agent):
            return 'Safari'
        elif re.search(r'Firefox', user_agent):
            return 'Mozilla Firefox'
        elif re.search(r'Opera', user_agent):
            return 'Opera'
        elif re.search(r'Edge', user_agent):
            return 'Microsoft Edge'
        elif re.search(r'MSIE', user_agent):
            return 'Internet Explorer'
        else:
            return 'Unknown Browser'

    def browser_data(self):
        data = {}
        for i in self.data:
            browser = i['visitor_useragent']
            browser = self.__identify_browser(browser)
            if browser in data.keys():
                data[browser]+=1
            else:
                data[browser]=1
        return data
    def reading_time(self):
        # Create a dictionary to store total reading time for each user
        user_reading_time = defaultdict(int)

        # Process JSON data to calculate total reading time for each user
        
        for entry in self.data:
            if entry['event_type'] == 'pagereadtime':
                user_uuid = entry['visitor_uuid']
                read_time = entry['event_readtime'] if 'event_readtime' in entry else 0
                user_reading_time[user_uuid] += read_time

        # Get the top 10 readers based on total reading time
        top_10_readers = sorted(user_reading_time.items(), key=lambda x: x[1], reverse=True)[:10]

        # Display the top 10 readers and their total reading time
        data={"title":"Top 10 readers based on total reading time:", 'data':[]}
        
        for rank, (user_id, total_time) in enumerate(top_10_readers, start=1):
            data["data"].append({"rank:":rank,"User_ID:":user_id,"total_reading_time:":f"{total_time} secs"})
        return data
    
    def __get_document_readers(self,doc_id):
        readers = set()
        for i in self.data:
            if 'subject_doc_id' in i.keys():
                if i['subject_doc_id'] == doc_id:
                    readers.add(i['visitor_uuid'])
        return readers
    def __get_reader_documents(self,visitor_uuid):
        documents = set()
        for i in self.data:
            if 'visitor_uuid' in i.keys():
                if i['visitor_uuid'] == visitor_uuid:
                    documents.add(i['env_doc_id'])
        return documents
    def also_like(self,doc_id, visitor_uuid=None, sorting_function=None):
        all_readers = self.__get_document_readers(doc_id)
        related_docs_count = defaultdict(int)

        for reader in all_readers:
            related_documents = self.__get_reader_documents(reader)
            for related_doc in related_documents:
                if related_doc != doc_id:
                    related_docs_count[related_doc] += 1

        sorted_related_docs = sorted(related_docs_count.items(), key=lambda x: sorting_function(x[1]), reverse=True)

        if visitor_uuid:
            visitor_docs = self.__get_reader_documents(visitor_uuid)
            sorted_related_docs = [doc for doc in sorted_related_docs if doc[0] not in visitor_docs]

        return [doc[0] for doc in sorted_related_docs][:10]


if __name__ == "__main__":
    file_path = 'sample_tiny.json'

    # Load data from the file
    data_getter = DataGetter(file_path)
    """
    reading_time = data_getter.reading_time()
    print(reading_time)"""
    # Example usage:
    document_id = "140224195414-e5a9acedd5eb6631bb6b39422fba6798"
    visitor_id = "04daa9ed9dde73d3"
    # Sort based on the number of readers
    result = data_getter.also_like(document_id, visitor_id, lambda x: x)
    print("Top 10 'also liked' documents based on number of readers:", result)