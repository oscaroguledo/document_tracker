import json
import matplotlib.pyplot as plt
import pycountry
import pycountry_convert as pc

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
    
    def __code_to_continent(self,country_code):
        try:
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            continent_name = pc.convert_continent_code_to_continent_name(continent_code)
            return continent_name
        except Exception as e:
            print(f"Error: {e}")
            return "Unknown"
    
    def countries_data(self):
        data = {}
        for i in self.data:
            country = i['visitor_country']
            if country in data.keys():
                data[country]+=1
            else:
                data[country]=0
        return data
    def __countries_list(self):
        data = []
        for i in self.data:
            country = i['visitor_country']
            data.append(country)
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


if __name__ == "__main__":
    file_path = 'sample_tiny.json'

    # Load data from the file
    data_getter = DataGetter(file_path)
    load_data = data_getter.continent_data()
    print(load_data)