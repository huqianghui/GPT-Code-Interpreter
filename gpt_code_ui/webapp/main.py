# The GPT web UI as a template based Flask app
import os
import requests
import asyncio
import json
import re
import logging
import sys
import openai
import pandas as pd
import ast

from collections import deque

from flask_cors import CORS
from flask import Flask, request, jsonify, send_from_directory, Response,render_template
from dotenv import load_dotenv
from .prompt import code_prompt, error_code_prompt
from .openAIRoundRobin import isRoundRobinMode,get_openaiByRoundRobinMode
#from .VerticaDataDictionary import getDataDictionary,clearCache

from kernel_program.main import APP_PORT as KERNEL_APP_PORT

load_dotenv('.env')

openai.api_version = os.environ.get("OPENAI_API_VERSION")
openai.log = os.getenv("OPENAI_API_LOGLEVEL")
openai.api_type == "azure"
AVAILABLE_MODELS = json.loads(os.environ["AZURE_OPENAI_DEPLOYMENTS"])
SQL_CONNECTION_STR= os.getenv("SQL_CONNECTION_STR")

# setting log level
log = logging.getLogger('webapp')
log.setLevel(os.getenv("OPENAI_API_LOGLEVEL").upper())

UPLOAD_FOLDER = 'workspace/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

APP_PORT = int(os.environ.get("WEB_PORT", 8080))

class LimitedLengthString:
    def __init__(self, maxlen=2000):
        self.data = deque()
        self.len = 0
        self.maxlen = maxlen

    def append(self, string):
        self.data.append(string)
        self.len += len(string)
        while self.len > self.maxlen:
            popped = self.data.popleft()
            self.len -= len(popped)

    def get_string(self):
        result = ''.join(self.data)
        return result[-self.maxlen:]

message_buffer = LimitedLengthString()

def allowed_file(filename):
    return True

def inspect_file(filename: str) -> str:
    READER_MAP = {
        '.csv': pd.read_csv,
        '.tsv': pd.read_csv,
        '.xlsx': pd.read_excel,
        '.xls': pd.read_excel,
        '.xml': pd.read_xml,
        '.json': pd.read_json,
        '.hdf': pd.read_hdf,
        '.hdf5': pd.read_hdf,
        '.feather': pd.read_feather,
        '.parquet': pd.read_parquet,
        '.pkl': pd.read_pickle,
        '.sql': pd.read_sql,
    }

    _, ext = os.path.splitext(filename)

    try:
        df = READER_MAP[ext.lower()](filename)
        return f'The file contains the following columns: {", ".join(df.columns)}'
    except KeyError:
        return ''  # unsupported file type
    except Exception:
        return ''  # file reading failed. - Don't want to know why.


def detect_language(text: str) -> str:
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    # 你的Azure文本分析服务终结点和订阅密钥
    endpoint = os.environ.get("AZURE_TEXT_ANALYTICS_ENDPOINT")
    subscription_key = os.environ.get("AZURE_TEXT_ANALYTICS_KEY")
    # 创建Azure认证对象
    credential = AzureKeyCredential(subscription_key)
    # 创建文本分析客户端
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=credential)
    # 使用文本分析客户端检测文本的语言
    result = text_analytics_client.detect_language(documents=[text])
    log.warn(f"text:{text}")
    log.warn(f"result:{result}")
    # 获取语言检测结果
    if result[0].is_error:
        log.error(f"发生错误:{result[0].error}")
        return "Chinese"
    else:
        detected_language = result[0].primary_language.name
        log.warn(f"detected_language:{detected_language}")
        return detected_language


# 代码重试最大次数
code_generate_retry=2
# 代码重试计数
code_generate_count = 0

async def get_code(user_prompt,model,user_openai_key=None, user_prompt_suffix=None):
    detectedLanguage = detect_language(user_prompt)
    if user_prompt_suffix:
        prompt = code_prompt.format(history=message_buffer.get_string(), user_prompt=user_prompt + user_prompt_suffix,user_language=detectedLanguage)
    else:
        prompt = code_prompt.format(history=message_buffer.get_string(), user_prompt=user_prompt,user_language=detectedLanguage)

    if user_openai_key:
        openai.api_key = user_openai_key

    arguments = dict(
        temperature=0,
        deployment_id=model,
        timeout=30,
        messages=[
            # {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
    )

    try:

        # 通过roundrobin 方式，轮训和retry
        if(isRoundRobinMode()):
            log.info(">>>>>round robin mode to access azure openAI services")
            roundRobinOpenAI = get_openaiByRoundRobinMode()
            result_GPT = roundRobinOpenAI.ChatCompletion.create(**arguments)
        else:
            log.info(">>>>>default mode to access azure openAI services")        
            result_GPT = openai.ChatCompletion.create(**arguments)

        if 'error' in result_GPT:
            raise openai.APIError(code=result_GPT.error.code, message=result_GPT.error.message)

        if result_GPT.choices[0].finish_reason == 'content_filter':
            raise openai.APIError('Content Filter')

    except openai.OpenAIError as e:
        return None, f"Error from API: {e}", 500

    try:
        content = result_GPT.choices[0].message.content

    except AttributeError:
        return None, f"Malformed answer from API: {content}", 500

    def extract_code(text):
        # Match triple backtick blocks first
        triple_match = re.search(r'```(?:\w+\n)?(.+?)```', text, re.DOTALL)
        if triple_match:
            return triple_match.group(1).strip()
        else:
            # If no triple backtick blocks, match single backtick blocks
            single_match = re.search(r'`(.+?)`', text, re.DOTALL)
            if single_match:
                return single_match.group(1).strip()
            
    sourceCode = extract_code(content)
     # 4. 判断是否是python，排除一些pip install的情况，用python语法树，做语法检查
    try:
        if sourceCode:
            python_pattern = r'^\s*(import|from|def|class|if|for|while|try|except|print|.+=.+|.+\(.*\)|.+:\s*$)'
            if re.match(python_pattern, sourceCode) is not None:
               ast.parse(sourceCode)
               return  sourceCode, content.strip(), 200 
            else:
               return  sourceCode, content.strip(), 200  
        else:
            return sourceCode, content.strip(), 200
    except SyntaxError as e:
        global code_generate_count
        code_generate_count += 1
        if code_generate_count < code_generate_retry:
            exceptionstr = str(e)
            error_code_prompt_str= error_code_prompt.format(sourceCode, exceptionstr)

            user_prompt_suffix = prompt + error_code_prompt_str
            return await get_code(user_prompt,model,user_openai_key, user_prompt_suffix)
        else:
            return sourceCode, "The generated codes always have some error, please try fresh the page and reset the kernel and try to change some input words.", 500

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)

@app.route('/')
def index():

    # Check if index.html exists in the static folder
    if not os.path.exists(os.path.join(app.root_path, 'static/index.html')):
        print("index.html not found in static folder. Exiting. Did you forget to run `make compile_frontend` before installing the local package?")

    return send_from_directory('static', 'index.html')
    #return render_template('index.html')

@app.route("/models")
def models():
    return jsonify(AVAILABLE_MODELS)

@app.route('/api/<path:path>', methods=["GET", "POST"])
def proxy_kernel_manager(path):
    if request.method == "POST":
        resp = requests.post(
            f'http://localhost:{KERNEL_APP_PORT}/{path}', json=request.get_json())
    else:
        resp = requests.get(f'http://localhost:{KERNEL_APP_PORT}/{path}')

    excluded_headers = ['content-encoding',
                        'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

@app.route('/assets/<path:path>')
def serve_static(path):
    return send_from_directory('static/assets/', path)

@app.route('/download')
def download_file():

    # Get query argument file
    file = request.args.get('file')
    # from `workspace/` send the file
    # make sure to set required headers to make it download the file
    return send_from_directory(os.path.join(os.getcwd(), 'workspace'), file, as_attachment=True)

@app.route('/inject-context', methods=['POST'])
def inject_context():
    user_prompt = request.json.get('prompt', '')

    # Append all messages to the message buffer for later use
    message_buffer.append(user_prompt + "\n\n")

    return jsonify({"result": "success"})

@app.route('/generate', methods=['POST'])
def generate_code():
    user_prompt = request.json.get('prompt', '')
    user_openai_key = request.json.get('openAIKey', None)
    model = request.json.get('model', None)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    user_prompt_suffix = None
    if(("@sql" in user_prompt.lower() or "@mysql" in user_prompt.lower()) and SQL_CONNECTION_STR):
        # tableAndFieldSchema = getDataDictionary()
        # user_prompt_suffix = "database connection as follow" + SQL_CONNECTION_STR + "\n" + " Users typically input table names and field names, often using aliases. These aliases are defined in the TABLE_KEYWORDS and FIELD_KEYWORDS fields, with different aliases separated by commas. When you need to write SQL queries, you'll need to map these aliases to the correct TABLE_NAME and FIELD_NAME in the following schema information:\n" + tableAndFieldSchema
        user_prompt_suffix = "database connection as follow" + SQL_CONNECTION_STR
        
    code, text, status = loop.run_until_complete(
        get_code(user_prompt, model,user_openai_key,user_prompt_suffix))
    loop.close()

    # Append all messages to the message buffer for later use
    message_buffer.append(user_prompt + "\n\n")

    return jsonify({'code': code, 'text': text}), status

@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        file_target = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_target)
        file_info = inspect_file(file_target)
        return jsonify({'message': f'File {file.filename} uploaded successfully.\n{file_info}'}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400


@app.route('/clear', methods=["GET", "POST"])
def clear():
    pass
    #clearCache()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=APP_PORT, debug=True, use_reloader=False)
