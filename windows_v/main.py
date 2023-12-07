import argparse
from gui import run_gui_app
from cli import run_cli_app

# Functionality for CLI
def cli_function(*args):
    run_cli_app(args[0])

# Graphical User Interface
def gui():
    run_gui_app()

# Main function to choose between CLI or GUI
def main():
    parser = argparse.ArgumentParser(description='Document Tracker functionality')
    #--file name-------------------------------------------------
    parser.add_argument('-f', '--file_name', help='e.g sample_tiny.json')
    #--histogram-------------------------------------------------
    parser.add_argument('-hs', '--histogram', help='\033[94m-f sample_tiny.json -hs True -hc country|continent|browser -x label -y label -a title\033[0m')
    parser.add_argument('-hc', '--hist_cat', help='category of histogram eg.countries etc')
    parser.add_argument('-x', '--x_label', help='X-axis label')
    parser.add_argument('-y', '--y_label', help='Y-axis label')
    parser.add_argument('-a', '--title', help='Histogram title')
    #------------------------------------------------------------

    #--reading time-------------------------------------------------
    parser.add_argument('-t', '--reading_time', help='\033[94m-f sample_tiny.json -t True -l 10\033[0m')
    parser.add_argument('-l', '--limit', help='Limit')
    #------------------------------------------------------------

    #--also like-------------------------------------------------
    parser.add_argument('-ld', '--also_like_documents', help='\033[94m-f sample_tiny.json -ld True -d document_uuid -v visitor_uuid\033[0m')
    parser.add_argument('-lg', '--also_like_graph', help='\033[94m-f sample_tiny.json -ld True -l 10\033[0m')
    parser.add_argument('-d', '--doc_uuid', help='Document UUID')
    parser.add_argument('-v', '--visitor_uuid', help='Document UUID')
    #------------------------------------------------------------

    #--convert dot to png, pdf, ps and dot-------------------------------------------------
    parser.add_argument('-dpng', '--dot_to_png', help='\033[94m-dpng True -src sample_tiny.dot -dest sample_tiny.png\033[0m')
    parser.add_argument('-dpdf', '--dot_to_pdf', help='\033[94m-dpdf True -src sample_tiny.dot -dest sample_tiny.pdf\033[0m')
    parser.add_argument('-dps', '--dot_to_ps', help='\033[94m-dps True -src sample_tiny.dot -dest sample_tiny.ps\033[0m')
    parser.add_argument('-ddot', '--dot_to_dot', help='\033[94m-ddot True -src sample_tiny.dot -dest sample_tiny.dot\033[0m')

    parser.add_argument('-src', '--source', help='Dot conversion source path')
    parser.add_argument('-dest', '--destination', help='Dot conversion destination path')
    #----------------------------------------------------------------------------
    args = parser.parse_args()
    _arg_dict = vars(args)
    if any(_arg_dict.values()):
        cli_function(_arg_dict)
    else:
        gui()

if __name__ == "__main__":
    main()
