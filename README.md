###  1. openAI的chatgpt提供新功能 code interpreter 
代码解释器特别有用的用例如下：

a) 解决定量和定性数学问题

b) 进行数据分析和可视化

c) 在不同文件格式之间进行转换

文档说明如下：

https://openai.com/blog/chatgpt-plugins#code-interpreter

功能演示如下：

https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/b79a4c86-8afb-4b87-affd-5f00ca0222a0

***需要开通openAI plus，每个月支付20刀才能使用***

### 2. 开源代码不同实现

a. https://github.com/ricklamers/gpt-code-ui
   ![image](https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/cfe0e09c-6598-4da0-84d9-8e2d0990c3ba)

b. https://github.com/shroominic/codeinterpreter-api
<img width="1283" alt="Screenshot 2023-08-22 at 15 22 40" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/d1ea5d97-e65a-4179-9395-b7b9d7018ad1">

### 3. 当前是从 https://github.com/ricklamers/gpt-code-ui 拷贝过来，做一些简单的分析。

a. prompt解析

想应用LLM，prompt至关重要，所以首先来看一下prompt是怎么写的。

在文件：gpt_code_ui/webapp/main.py中
<img width="1453" alt="Screenshot 2023-08-22 at 15 36 34" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/22dafe9b-92b9-4701-a1bc-6600c6cb0518">

b. 配置
根据.env.azure-exampl 来配置相应的变量，然后修改文件为.env文件。
代码启动的时候，会去读这个文件。
```python
load_dotenv('.env')
```

c. 运行方式

除了直接通过pip install 生成可执行文件gptcode之外，还可以通过make 命令把静态资源打包到gpt_code_ui/webapp/static下面。

（详细参见Makefile,我把Makefile中的 upload task删除了，本地编译不需要上传。）
  
 根据prompt或者文档预先安装一些包，如果后期运行报错，根据错误再来安装也可以。

然后就可以直接运行 gpt_code_ui/webapp/main.py文件


d. 示例运行

1） 上传一个csv文件，让它给出一些可视化统计。(Can you run some basic visualization?)
<img width="769" alt="Screenshot 2023-08-22 at 15 52 43" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/01f91eba-3cae-4841-8d67-e6fcca37885a">

2） 根据URL等，生成QR code
<img width="1322" alt="Screenshot 2023-08-22 at 15 50 14" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/bd403f8b-0157-4e04-bbef-6fefd648cf19">

3） 图片处理，变大小，改变颜色等。
<img width="1367" alt="Screenshot 2023-08-22 at 16 23 17" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/17e73f89-61ee-441c-82b5-691dac55fc40">

<img width="1444" alt="Screenshot 2023-08-22 at 16 36 20" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/94a97c02-05ff-4301-aac6-36c17ccb0b44">









