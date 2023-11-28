import re
from graphviz import Digraph
from user_agents import parse
import matplotlib.pyplot as plt
import pandas as pd
import pycountry_convert as pc
from collections import defaultdict,Counter

class DataGetter():
    def __init__(self,file_path) -> None:
        self.file_path = file_path
        self.data = self.__load_data()
        self.countries = self.get_countries_data()
        self.countries_list = self.__get_countries_list()
        
    def __load_data(self):
        data = pd.read_json(self.file_path, lines=True)
        return data
    def __get_countries_list(self):
        data = self.data['visitor_country'].tolist()
        return data
    def __get_code_to_continent(self,country_code):
        try:
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            continent_name = pc.convert_continent_code_to_continent_name(continent_code)
            return continent_name
        except Exception as e:
            #print(f"Error: {e}")
            return "Unknown Region"  
    def get_countries_data(self):
        country_counts = self.data['visitor_country'].value_counts().to_dict()
        return country_counts
    def get_continent_data(self):
        data = Counter(self.__get_code_to_continent(country_code) for country_code in self.countries_list)
        return dict(data)
    def __identify_browser(self,user_agent):
        user_agent = parse(user_agent)
        return user_agent.browser.family
    def get_browser_data(self):
        d= self.data['visitor_useragent'].value_counts().to_dict()
        data = Counter(self.__identify_browser(i) for i in d)
        return dict(data)
    
    def get_reading_time(self):
        # Create a dictionary to store total reading time for each user
        user_reading_time = defaultdict(int)

        # Process DataFrame data to calculate total reading time for each user
        for index, entry in self.data.iterrows():
            if entry['event_type'] == 'pagereadtime':
                user_uuid = entry['visitor_uuid']
                read_time = entry.get('event_readtime', 0)
                user_reading_time[user_uuid] += read_time

        # Get the top 10 readers based on total reading time
        top_10_readers = sorted(user_reading_time.items(), key=lambda x: x[1], reverse=True)[:10]

        # Display the top 10 readers and their total reading time
        data = {
            "title": "Top 10 readers based on total reading time:",
            "data": [
                {
                    "rank": rank,
                    "User_ID": user_id,
                    "total_reading_time": f"{total_time} secs"
                }
                for rank, (user_id, total_time) in enumerate(top_10_readers, start=1)
            ]
        }
        return data
    
    def __get_document_readers(self,doc_id):
        readers = list(self.data.loc[self.data['subject_doc_id'] == doc_id, 'visitor_uuid'])
        return readers
    def __get_reader_documents(self,visitor_uuid):
        documents = list(self.data.loc[self.data['visitor_uuid'] == visitor_uuid, 'subject_doc_id'])
        return documents
    
    def order(self, array,order, limit):
        if order =="asc":
            return sorted(array)[:limit]
        if order =="desc":
            return sorted(array, reverse=True)[:limit]
    
    def get_also_like(self,doc_uuid, visitor_uuid=None, sorting_function=None):
        # Filter data based on provided document UUID and optional visitor UUID
        readers = self.__get_document_readers(doc_uuid)
        print(readers,"=====")
        also_liked = {doc_uuid:[]}
        for reader in readers:
            if reader ==visitor_uuid:
                also_liked[doc_uuid].append({reader:self.__get_reader_documents(reader)} )
        print(also_liked,"=====")
        top_liked_docs=sorting_function([self.__get_reader_documents(reader) for reader in readers if reader ==visitor_uuid][0])
        return (top_liked_docs)
    
    def show_histogram(self,dictionary,x_label,y_label, title):
        # Extracting keys and values from the dictionary
        categories = list(dictionary.keys())
        values = list(dictionary.values())

        # Creating the histogram
        plt.figure(figsize=(12, 6))  # Setting the figure size
        colors = ['blue', 'orange', 'green', 'red', 'purple', "gray","cyan"]
        plt.bar(categories, values, color=colors, width=0.6)  # Creating the bar chart

        # Adding labels and title
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)

        # Rotating x-axis labels for better readability if needed
        plt.xticks(rotation=45)

        # Displaying the histogram
        plt.tight_layout()
        plt.show()

    def generate_graph(self):

        # Create a Digraph object
        dot = Digraph()

        # List of documents and readers in the "also like" relationship
        documents = ['b4fe', 'd38c', '87c4', 'e16e', '2bb5', '9da6', '1b2b', '90c2', '56e3', 'a2c8']
        readers = ['6771']

        # Adding nodes for documents and readers
        for doc in documents:
            dot.node(doc[-4:], style='filled', color='lightblue')  # Shorten and shade document UUIDs

        for reader in readers:
            dot.node(reader[-4:], style='filled', color='lightgreen')  # Shorten and shade reader UUIDs

        # Adding edges to represent relationships (has-read relationship)
        for doc in documents:
            dot.edge(reader[-4:], doc[-4:], arrowhead='vee')

        # Save the .dot file
        dot.render('also_like_graph', format='pdf', view=True)  # Output .pdf file

if __name__ == "__main__":
    file_path = 'sample_tiny.json'

    # Load data from the file
    data_getter = DataGetter(file_path)
    #countries= data_getter.get_countries_data()
    #data_getter.show_histogram(countries,x_label='Countries', y_label='Frequency',title='Countries of viewers')
    #----
    #continents= data_getter.get_continent_data()
    #data_getter.show_histogram(continents,x_label='Continents', y_label='Frequency',title='Continents of viewers')
    #---
    #continents= data_getter.get_browser_data()
    #data_getter.show_histogram(continents,x_label='Browsers', y_label='Frequency',title='Browsers of viewers')
    #---
    """
    reading_time = data_getter.reading_time()
    print(reading_time)"""
    # Example usage:
    document_id = "100713205147-2ee05a98f1794324952eea5ca678c026"
    visitor_id = '232eeca785873d35'#'76175bb1ea9805a1'
    # Sort based on the number of readers
    
    result = data_getter.get_also_like(document_id, visitor_id, lambda x: data_getter.order(x, "desc", 10))
    print("Top 10 'also liked' documents based on number of readers:", result)
    #---
    data_getter.generate_graph()