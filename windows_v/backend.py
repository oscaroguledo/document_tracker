import re
import os, json
from graphviz import Digraph
from user_agents import parse
import matplotlib.pyplot as plt
import pandas as pd
import pycountry_convert as pc
from collections import defaultdict,Counter

class DataGetter():
    # Initialize the class with the file path to JSON data
    def __init__(self,file_path) -> None:
        self.file_path = file_path
        self.data = self.__load_data()
        self.countries = self.get_countries_data()
        self.countries_list = self.__get_countries_list()

    # Load JSON data from the file  
    def __load_data(self):
        data = pd.read_json(self.file_path, lines=True)
        return data
    
    # Get a list of countries from the loaded data
    def __get_countries_list(self):
        data = self.data['visitor_country'].tolist()
        return data
    
    # Get the continent data from the list of countries
    def __get_code_to_continent(self, country_code):
        try:
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            continent_name = pc.convert_continent_code_to_continent_name(continent_code)
            return continent_name
        except Exception as e:
            return "Unknown Region"  
    
    # Get country-wise visit counts
    def get_countries_data(self):
        country_counts = self.data['visitor_country'].value_counts().to_dict()
        return country_counts
    
    # Get continent-wise visit counts
    def get_continent_data(self):
        data = Counter(self.__get_code_to_continent(country_code) for country_code in self.countries_list)
        return dict(data)
    
    # Identify browser from the user agent
    def __identify_browser(self, user_agent):
        user_agent = parse(user_agent)
        return user_agent.browser.family
    
     # Get counts of different browsers
    def get_browser_data(self):
        d = self.data['visitor_useragent'].value_counts().to_dict()
        data = Counter(self.__identify_browser(i) for i in d)
        return dict(data)
    
    # Calculate reading time for top readers
    def get_reading_time(self, limit=None):#limit=10
        # Create a dictionary to store total reading time for each user
        user_reading_time = defaultdict(int)

        # Process DataFrame data to calculate total reading time for each user
        for index, entry in self.data.iterrows():
            if entry['event_type'] == 'pagereadtime':
                user_uuid = entry['visitor_uuid']
                read_time = entry.get('event_readtime', 0)
                user_reading_time[user_uuid] += read_time

        # Get the top 10 readers based on total reading time
        if limit == None:
            limit =10
        top_10_readers = sorted(user_reading_time.items(), key=lambda x: x[1], reverse=True)[:limit]

        # Display the top 10 readers and their total reading time
        data = [
                {
                    "rank": rank,
                    "User_ID": user_id,
                    "total_reading_time": f"{total_time} secs"
                }
                for rank, (user_id, total_time) in enumerate(top_10_readers, start=1)
            ]
        return data
    
    # Get readers of a specific document
    def get_document_readers(self, doc_id):
        readers = list(self.data.loc[self.data['subject_doc_id'] == doc_id, 'visitor_uuid'])
        return readers
    
    # Get documents read by a specific reader
    def get_reader_documents(self, visitor_uuid):
        documents = list(self.data.loc[self.data['visitor_uuid'] == visitor_uuid, 'subject_doc_id'])
        return documents
    
    #Sorting Order function to sort an array based on order and limit
    def __order(self, array, order, limit):
        if order == "asc":
            return sorted(array)[:limit]
        if order == "desc":
            return sorted(array, reverse=True)[:limit]
    
    # Get documents that readers also liked
    def get_also_like_documents(self, doc_uuid, visitor_uuid=None, sorting_function=None):
        readers = self.get_document_readers(doc_uuid)
        res = sorting_function([self.get_reader_documents(reader) for reader in readers if reader == visitor_uuid][0])
        return res
    
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

        #from graphviz import Digraph

    # Create and save the graph showing related documents and readers
    def generate_also_like_graph(self,reader,document, format=None):
        also_liked = self.get_also_like(document, reader, sorting_function = lambda x: self.__order(x, "desc", 10))
        graph = Digraph() # Create a Digraph object
        
        for doc in also_liked:
            if doc == document:
                graph.node(doc[-4:], style='filled', color='green')  # Shorten and shade document UUIDs
            for r in self.get_document_readers(doc):
                print(r,"====")
                if r == reader:
                    graph.node(reader[-4:], style='filled', color='green')  # Shorten and shade reader UUIDs
                if doc in self.get_reader_documents(r):
                    graph.edge(r[-4:], doc[-4:], arrowhead='vee')

        if format == 'pdf':
            graph.render('also_like_graph', format='pdf', view=True)  # Output .pdf file
        if format == 'dot' or format == None:
            graph.render('also_like_graph', format='dot', view=True)  # Output .pdf file
        if format == 'ps':
            graph.render('also_like_graph', format='ps', view=True)  # Output .pdf file

        
    # Convert dot file to ps format
    def convert_dot_to_ps(self, dot_file_path, ps_file_path):
        cmd = f"dot -Tps {dot_file_path} -o {ps_file_path}"
        os.system(cmd)
    
    # Convert dot file to pdf format
    def convert_dot_to_pdf(self, dot_file_path, pdf_file_path):
        cmd = f"dot -Tpdf {dot_file_path} -o {pdf_file_path}"
        os.system(cmd)
    
    # Convert dot file to png format
    def convert_dot_to_png(self, dot_file_path, png_file_path):
        # Functionality yet to be implemented
        pass


if __name__ == "__main__":
    # Instantiate DataGetter class with file path to JSON data
    file_path = 'sample_tiny.json'
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
    
    #data_getter.generate_also_like_graph(reader=visitor_id, document=document_id, format='dot')
    data_getter.convert_dot_to_ps('also_like_graph.dot', 'also_like_graph.ps')