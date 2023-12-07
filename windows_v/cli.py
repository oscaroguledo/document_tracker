
from backend import os, plt, pd, DataGetter
import math
class DocumentTrackerCli():
    def __init__(self, input_file) -> None:
        
        pass
    
def run_cli_app(args):
    while(True):
        #--filename------------------------
        if not args['file_name'] == None:
            if not os.path.exists(args['file_name']):
                print(f"\033[91mThe file {args['file_name']} doesn't exist\n\033[0m")
                break
            print(f"\033[94mLoading data...\n\033[0m")
            data_getter = DataGetter(args['file_name'])
            print(f"\033[94mData loaded...\n\033[0m")
            
            #--histogram------------------------
            if not (args['histogram'] == None or args['histogram'] == False):
                #check for the type of histogram
                hist_cats=['country', 'continent','browser']
                if not args['hist_cat'] == None:
                    if args['doc_uuid'] == None:
                        print("\033[91mError: You want to view a histogram. specify the doc_uuid using '-d'|'--doc_uuid' \n\033[0m") 
                        break

                    if args['hist_cat'] not in hist_cats:
                        print(f'\033[91mError: the select category must be one of {hist_cats}\n\033[0m')
                        break
                    if args['x_label'] == None:
                        print("\033[91mError: You want to view a histogram. specify the x_label using '-x'|'--x_label' \n\033[0m") 
                        break
                    if args['y_label'] == None:
                        print("\033[91mError: You want to view a histogram. specify the x_label using '-y'|'--y_label' \n\033[0m") 
                        break
                    if args['title'] == None:
                        print("\033[91mError: You want to view a histogram. specify the x_label using '-a'|'--title' \n\033[0m") 
                        break
                    if args['hist_cat'] == 'country':
                        country= data_getter.get_countries_data(document_uuid=args['doc_uuid'])
                        data_getter.show_histogram(country,x_label=args['x_label'], y_label=args['y_label'],title=args['title'])
                        break
                    elif args['hist_cat'] == 'continent':
                        continent= data_getter.get_continent_data(document_uuid=args['doc_uuid'])
                        data_getter.show_histogram(continent,x_label=args['x_label'], y_label=args['y_label'],title=args['title'])
                        break
                    elif args['hist_cat'] == 'browser':
                        browser= data_getter.get_browser_data()
                        data_getter.show_histogram(browser,x_label=args['x_label'], y_label=args['y_label'],title=args['title'])
                        break
                    else:
                        pass

                else:
                    print("\033[91mError: You want to view a histogram. specify the category using '-hc' \n\033[0m") 
                    break
            
            #--reading time--------------------
            elif not (args['reading_time'] == None or args['reading_time'] == False):
                if limit == None:
                    limit=10
                reading_time = data_getter.reading_time(limit=args['limit'])
                print(f"\033[94mThe top {limit} readers: \n\033[0m")
                print(reading_time)
                break
            #--also like-----------------------
            elif not (args['also_like_documents'] == None or args['also_like_documents'] == False):
                if args['doc_uuid'] == None:
                    print(f"\033[91mError: the document uuid must be set '-d' \n\033[0m")
                    break
                limit = args['limit']
                if limit == None:
                    limit=10
                also_like_doc = data_getter.get_also_like_documents(args['doc_uuid'], visitor_uuid=args['visitor_uuid'], sorting_function = lambda x: data_getter.order(x, "desc", limit))
                print(f"\033[94mThe top {limit} also liked documents: \n\033[0m")
                print(also_like_doc)
                break
            #--dot conversion------------------
            elif not (args['also_like_graph'] == None or args['also_like_graph'] == False):
                if args['doc_uuid'] == None:
                    print(f"\033[91mError: the document uuid must be set '-d' \n\033[0m")
                    break
                limit = args['limit']
                if limit == None:
                    limit=10
                data_getter.generate_also_like_graph(args['doc_uuid'], visitor_uuid=args['visitor_uuid'], limit=limit)
                print(f"\033[94mThe generated .dot graph has been saved at 'graph/also_like_graph.dot': \n\033[0m")
                break
            elif not (args['dot_to_pdf'] == None or args['dot_to_pdf'] == False):
                if args['source'] == None:
                    print(f"\033[91mSet the location of the .dot \n\033[0m")
                    break 
                if args['destination'] == None:
                    print(f"\033[91mSet the destination of the .pdf result\n\033[0m")
                    break 
                data_getter.convert_dot_to_pdf(args['source'], args['destination'])
                print(f"\033[94mThe generated pdf has been saved at 'graph/also_like_graph.pdf': \n\033[0m")
                break
            elif not (args['dot_to_ps'] == None or args['dot_to_ps'] == False):
                if args['source'] == None:
                    print(f"Set the location of the .dot\n")
                    break 
                if args['destination'] == None:
                    print(f"\033[91mSet the destination of the .ps result\n\033[0m")
                    break 
                data_getter.convert_dot_to_ps(args['source'], args['destination'])
                print(f"\033[94mThe generated .ps  has been saved at 'graph/also_like_graph.ps': \n\033[0m")
                break
            elif not (args['dot_to_png'] == None or args['dot_to_png'] == False):
                if args['source'] == None:
                    print(f"\033[91mSet the location of the .dot\033[0m")
                    break 
                if args['destination'] == None:
                    print(f"\033[91mSet the destination of the .png result\033[0m")
                    break 
                data_getter.convert_dot_to_png(args['source'], args['destination'])
                print(f"\033[94mThe generated .png graph has been saved at 'graph/also_like_graph.png': \n\033[0m")
                break
            elif not (args['dot_to_dot'] == None or args['dot_to_dot'] == False):
                if args['source'] == None:
                    print(f"\033[91mSet the location of the .dot\n\033[0m")
                    break 
                if args['destination'] == None:
                    print(f"\033[91mSet the destination of the .dot result\n\033[0m")
                    break 
                data_getter.convert_dot_to_dot(args['source'], args['destination'])
                print(f"\033[94mThe generated .dot graph has been saved at 'graph/also_like_graph.dot': \n\033[0m")
                break
        #--help--------------------------
            else:
                print("\033[93mFor help, ensure '-h' is in arguments\n\033[0m") 
                break 
        else:
            print("\033[91mError: No file has been passed. specify the file path using '-f'|'--file_name' \n\033[0m") 
            break
    