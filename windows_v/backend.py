import re
import os, json
import shutil
import time
import threading
from graphviz import Digraph, Source
from user_agents import parse
import matplotlib.pyplot as plt
import pandas as pd
import glob
import pycountry_convert as pc
from collections import defaultdict,Counter
import pandas as pd
import glob
from concurrent.futures import ThreadPoolExecutor

class JsonLoader():
    def __init__(self, file_path) -> None:
        self.file = file_path
        self.__sharding()
        self.data= self.__retrieve_data()

    def __sharding(self):
        # Open the large JSON file
        with open(self.file,'r', encoding='utf-8') as file:
            lines = file.readlines()
            data = [json.loads(line.strip()) for line in lines]

        # Define the number of records in each shard
        records_per_shard = 100000
        num_records = len(data)

        # Shard the data
        def shard_data(start_index, end_index, shard_index):
            shard = data[start_index:end_index]
            path = f'tmp/{self.file[-8:-5]}/'
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except Exception:
                    pass
            shard_filename = f'{path}shard_{shard_index}.json'
            with open(shard_filename, 'w') as file:
                for dictionary in shard:
                    json.dump(dictionary, file)
                    file.write('\n')

        # Execute sharding operation using threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            
            futures = []
            for i in range(0, num_records, records_per_shard):
                future = executor.submit(shard_data, i, i + records_per_shard, i // records_per_shard)
                futures.append(future)

            # Wait for all threads to complete
            for future in futures:
                future.result()  # Wait for each thread to finish

    
    def __retrieve_data(self):
        # Function to read a JSON file and return a DataFrame
        def read_json_to_dataframe(file):
            return pd.read_json(file, lines=True)

        # List all JSON files in the directory
        shard_files = glob.glob(f'tmp/{self.file[-8:-5]}/shard_*.json')

        # Initialize an empty list to hold data frames
        dfs = []

        # Function to read JSON files using threads
        def read_files_with_threads(files):
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(read_json_to_dataframe, files))
            return results

        # Read JSON files using threads
        dfs = read_files_with_threads(shard_files)

        # Concatenate all data frames into a single data frame
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df

class DataGetter():
    # Initialize the class with the file path to JSON data
    def __init__(self,file_path) -> None:
        self.file_path = file_path
        self.data = self.__load_data()
        
        self.countries_list = self.__get_countries_list()
        #self.get_countries = self.get_countries_data()
        #self.get_continents = self.get_continent_data()
        self.get_browsers = self.get_browser_data()
        #self.get_readingtime = self.get_reading_time(limit=self.limit)
        #self.get_also_like = self.get_also_like_documents(document_id, visitor_id, sorting_function = lambda x: self.order(x, "desc", self.limit))
        
    # Load JSON data from the file  
    def __load_data(self):
        loader = JsonLoader(self.file_path)
        data = loader.data
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
    def get_countries_data(self,document_uuid):
        # Filter the data for the given document_uuid
        
        filtered_data = self.data[self.data["subject_doc_id"] == document_uuid]
        # Count visitor countries for the filtered data
        country_counts = filtered_data['visitor_country'].value_counts().to_dict()
        print(country_counts,"===")
        return country_counts
    
    # Get continent-wise visit counts
    def get_continent_data(self,document_uuid):
        # Assuming self.data contains the data with 'visitor_country' and 'document_uuid' columns
        filtered_data = self.data[self.data["subject_doc_id"] == document_uuid]

        continent_counts = Counter(self.__get_code_to_continent(country_code) for country_code in filtered_data['visitor_country'])
        return dict(continent_counts)
    
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
    def get_reading_time(self, limit=None):
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
                    "Total Reading Time": f"{total_time} secs"
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
    def order(self, array, order, limit):
        if order == "asc":
            return sorted(array)[:limit]
        if order == "desc":
            return sorted(array, reverse=True)[:limit]
    
    # Get documents that readers also liked
    def get_also_like_documents(self, doc_uuid, visitor_uuid=None, sorting_function=None):
        readers = self.get_document_readers(doc_uuid)
        if visitor_uuid ==None:
            l = [self.get_reader_documents(reader) for reader in readers]
        else:
            l = [self.get_reader_documents(reader) for reader in readers if reader == visitor_uuid]
        if len(l)>=1:
            uuids = [value for value in l[0] if isinstance(value, str)]

            res = sorting_function(uuids)
            counter=Counter(res)
            
            data = [
                    {
                        "rank": rank,
                        "document": document_id,
                        "readers_cnt": f"{counter[document_id]} reader" if counter[document_id]==1 else f"{counter[document_id]} readers"
                    }
                    for rank, document_id in enumerate(set(res), start=1)
                ]
        else:
            data=[]
        
        return data
    
    def show_histogram(self,dictionary,x_label,y_label, title):
        # Extracting keys and values from the dictionary
        categories = list(dictionary.keys())
        values = list(dictionary.values())

        # Creating the histogram
        plt.figure(figsize=(12, 6))  # Setting the figure size
        colors = ['blue', 'orange', 'green', 'red', 'purple', "gray","cyan"]
        plt.bar(categories, values, color=colors, width=1)  # Creating the bar chart
        
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
    def generate_also_like_graph(self,document,reader, format=None, limit=None):
        if limit ==None:
            limit=10
        also_liked = self.get_also_like_documents(document, reader, sorting_function = lambda x: self.order(x, "desc", limit))
        graph = Digraph() # Create a Digraph objects
        for doc in also_liked:
            if doc['document'] == document:
                graph.node(doc['document'][-4:], style='filled', color='green')  # Shorten and shade document UUIDs
            doc_readers = self.get_document_readers(doc['document'])
            for r in set(doc_readers):
                if r == reader:
                    graph.node(r[-4:], style='filled', color='green')  # Shorten and shade reader UUIDs
                graph.edge(r[-4:], doc['document'][-4:], arrowhead='vee')

        if format == 'pdf':
            graph.render('graph/also_like_graph', format='pdf', view=True)  # Output .pdf file
        if format == 'dot' or format == None:
            graph.render('graph/also_like_graph', format='dot', view=True)  # Output .dot file
        if format == 'ps':
            graph.render('graph/also_like_graph', format='ps', view=True)  # Output .pdf file

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
        try:
            # Read the DOT file
            with open(dot_file_path, 'r') as dot_file:
                dot_data = dot_file.read()
            
            # Create a Source object from the DOT data
            graph = Source(dot_data)
            
            # Render the graph to a PNG file
            graph.format = 'png'
            graph.render(filename=png_file_path, view=False, cleanup=True)
        except Exception:
            pass
    # Convert dot file to dot format
    def convert_dot_to_dot(self, src, dest):
        try:
            shutil.copyfile(src, dest)
        except Exception as e:
            pass

if __name__ == "__main__":
    # Instantiate DataGetter class with file path to JSON data
    #file_path = 'sample_3m_lines.json'
    #file_path = 'sample_600k_lines.json'
    #file_path = 'sample_400k_lines.json'
    #file_path = 'sample_100k_lines.json'
    #file_path = 'sample_small.json'
    file_path = 'sample_small.json'
    data_getter = DataGetter(file_path)
    document_id = "140224132818-2a89379e80cb7340d8504ad002fab76d"
    #countries= data_getter.get_countries_data(document_uuid=document_id)
    #data_getter.show_histogram(countries,x_label='Countries', y_label='Frequency',title='Countries of viewers')
    #----
    #continents= data_getter.get_continent_data(document_uuid=document_id)
    #data_getter.show_histogram(continents,x_label='Continents', y_label='Frequency',title='Continents of viewers')
    #---
    #continents= data_getter.get_browser_data()
    #data_getter.show_histogram(continents,x_label='Browsers', y_label='Frequency',title='Browsers of viewers')
    #---
    """
    reading_time = data_getter.reading_time()
    print(reading_time)"""
    # Example usage:
    document_id = "140224132818-2a89379e80cb7340d8504ad002fab76d"
    visitor_id = '92026debfb082ca4'#'76175bb1ea9805a1'
    # Sort based on the number of readers
    
    #data_getter.generate_also_like_graph(reader=visitor_id, document=document_id, format='dot')
    #data_getter.convert_dot_to_ps('also_like_graph.dot', 'also_like_graph.ps')

    ##deleting temporary folders
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')
    