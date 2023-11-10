

code_prompt = """First, here is a history of what I asked you to do earlier. 
    The actual prompt follows after ENDOFHISTORY. 
    History:
    {history}
    ENDOFHISTORY.
    Write Python code, in a triple backtick Markdown code block, that does the following:
    {user_prompt}
    If there are some data result in the procees,show the as more as posibble insights about the data result.
    If there are some data result in the procees,show the as more as posibble insights about the data result.
    If there are some data result in the procees,show the as more as posibble insights about the data result.
    
    Notes: 
        First, think step by step what you want to do and write it down in {user_language}.
        If the user's input cannot be implemented through Python code, then simply respond without writing Python code.
        For example:
            hello! 你好。之类的问候语。
            今天天气，这样是现状事实描述和问题。
            who's the president of the United States? and so on.
        If the user's input cannot be implemented through Python code then generate valid Python code in a code block 
        Make sure all code is valid - it be run in a Jupyter Python 3 kernel environment. 
        Define every variable before you use it.
        For data munging, you can use 
            'numpy', # numpy==1.24.3
            'dateparser' #dateparser==1.1.8
            'pandas', # matplotlib==1.5.3
            'geopandas' # geopandas==0.13.2
        For pdf extraction, you can use
            'PyPDF2', # PyPDF2==3.0.1
            'pdfminer', # pdfminer==20191125
            'pdfplumber', # pdfplumber==0.9.0
        
        For table show, you can use
            'Pillow'  # Pillow==10.0.0
            'prettytable' # prettytable==3.9.0
        If the data has multiple columns and no specific graphical representation is specified,
          you can use the Python image processing library Pillow to show prattytable table as an image.
          Then you save an image using Pillow and then visualize the processed image with matplotlib

          Such as:
            from PIL import Image, ImageDraw, ImageFont
            from prettytable import PrettyTable
            import matplotlib.pyplot as plt

            
            populationTable = PrettyTable()
            populationTable.field_names = ["City name", "Area", "Population", "Annual Rainfall"]
            populationTable.add_row(["Adelaide", 1295, 1158259, 600.5])
            populationTableImage = Image.new("RGB", (500, 200), "white")
            font = ImageFont.truetype("../font/Microsoft Yahei.ttf", 15)
            draw = ImageDraw.Draw(populationTableImage)
            populationTableImage.save("populationTable.png")
            plt.imshow(populationTableImage)
            plt.title("populationTable")
            plt.show()

        You can choose Arial.tff,SimHei.tff and Microsoft Yahei.tff in the ../font folder as the font.
        Do not print prattytable's table directly.
        
        For data visualization, you can use
            'matplotlib', # matplotlib==3.7.1
        Be sure to generate charts with matplotlib. If you need geographical charts, use geopandas with the geopandas.datasets module.
        If the user has just uploaded a file, focus on the file that was most recently uploaded (and optionally all previously uploaded files)
        If the language is Chinese and you need Matplotlib to display Chinese characters, please configure Matplotlib to use a suitable font for Chinese display as follows:
            font_options = {{
                'family' : 'serif', # Set font family
                'serif' : 'SimHei', # Set font
            }}
            plt.rc('font',**font_options)
        then Chinese characters can be displayed correctly in Matplotlib charts as well.

    Teacher mode:if the code modifies or produces a file, at the end of the code block insert a print statement that prints a link to it as HTML string: <a href='/download?file=INSERT_FILENAME_HERE'>Download file</a>. Replace INSERT_FILENAME_HERE with the actual filename.
    If you display an image, please zoom in as much as possible so that the content on the x-axis can be fully visible.
    """

error_code_prompt =  """
The code you generated last time is as follows: 
            {}
            And there are the following issues detected through the syntax tree: 
            {}. 
            Please avoid these errors and generate code that can run correctly.

"""