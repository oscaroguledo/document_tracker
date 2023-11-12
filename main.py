import json
import matplotlib.pyplot as plt
import pycountry

class DataGetter():
    def __init__(self,file_path) -> None:
        self.file_path = file_path
        self.data = self.__load_data()
        self.countries = self.countries_data()
        

    def __load_data(self):
        data = []
        with open(self.file_path, 'r') as file:
            data = [json.loads(line) for line in file]
        return data
    
    def __code_to_continent(self,country_code):
        try:
            print(country_code)
            country_info = pycountry.countries.get(name='United States')
            print(country_info.alpha_2,pycountry.subdivisions.,"======================",pycountry.subdivisions.get(code=country_code))
            return pycountry.subdivisions.get(code=country_code).continent
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
    
    def continent_data(self):
        data={}
        for country_code in self.countries:
            continent = self.__code_to_continent(country_code)
            if continent in data.keys():
                data[continent]+=1
            else:
                data[continent]=0
        return data


if __name__ == "__main__":
    file_path = 'sample_tiny.json'

    # Load data from the file
    data_getter = DataGetter(file_path)
    load_data = data_getter.continent_data()
    print(load_data)