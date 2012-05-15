def csv_to_html(data_dir, output_dir): 
    """Generates a HTML file of tables of the dataset - useful for quick viewing. Ideally, 
       the tables would be sortable, searcheable, summarizeable etc., but right now, that
       functionality doesn't work. Not sure why.
       Probably want to switch to: http://tablesorter.com/docs/ 
    """
    html = open(os.path.join(output_dir, "consolidated_data.html"), "w")
    html.write("""
    <html>
    <head>
    <script type="text/javascript" src='../libraries/sorttable.js'></script>
    </head><body>""")
    csv_files = [c for c in os.listdir(data_dir) if re.search(r'.+\.csv', c)]
    for csv_file in csv_files:
        html.write("<h1>%s</h1>" % csv_file)
        html.write("<table class='sortable'>")
        for line in csv.reader(open(os.path.join(data_dir, csv_file), "r")):
            html.write("<tr>\n")
            html.write("</tr>\n")
            for item in line: 
                html.write('<td>' + item + '</td>')
        html.write("</table>")
    html.close() 
