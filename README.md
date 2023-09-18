###  1. openAI的chatgpt提供新功能 code interpreter 

B站视频讲解： https://www.bilibili.com/video/BV1LH4y1Q7X8/

youtube视频讲解： https://youtu.be/erETVeOU_5U

<img width="600" alt="gpt-code-diagram" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/d3ffedac-03e5-4447-a620-ca4d24e1f974">

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

clone下来，运行起来，遇到一个错误。(https://github.com/shroominic/codeinterpreter-api/issues/97)

<img width="1283" alt="Screenshot 2023-08-22 at 15 22 40" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/d1ea5d97-e65a-4179-9395-b7b9d7018ad1">

### 3. 当前是从 https://github.com/ricklamers/gpt-code-ui 拷贝过来，做一些简单的分析。

#### a. prompt解析

   想应用LLM，prompt至关重要，所以首先来看一下prompt是怎么写的。
   
   在文件：gpt_code_ui/webapp/main.py中
   <img width="1453" alt="Screenshot 2023-08-22 at 15 36 34" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/22dafe9b-92b9-4701-a1bc-6600c6cb0518">

#### b. 配置
   根据.env.azure-exampl 来配置相应的变量，然后修改文件为.env文件。
   代码启动的时候，会去读这个文件。
   ```python
   load_dotenv('.env')
   ```

#### c. 运行方式

   除了直接通过pip install 生成可执行文件gptcode之外，还可以通过make 命令把静态资源打包到gpt_code_ui/webapp/static下面。
   
   （详细参见Makefile,我把Makefile中的 upload task删除了，本地编译不需要上传。）
     
    根据prompt或者文档预先安装一些包，如果后期运行报错，根据错误再来安装也可以。
   
   然后就可以直接运行 gpt_code_ui/webapp/main.py文件


#### d. 示例运行


功能视频演示如下：

https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/77fae716-4fa6-4375-a6b9-7e3936b771d7



##### 1） 上传一个csv文件，让它给出一些可视化统计。(Can you run some basic visualization?)
<img width="769" alt="Screenshot 2023-08-22 at 15 52 43" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/01f91eba-3cae-4841-8d67-e6fcca37885a">

##### 2） 根据URL等，生成QR code
<img width="1322" alt="Screenshot 2023-08-22 at 15 50 14" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/bd403f8b-0157-4e04-bbef-6fefd648cf19">

##### 3） 图片处理，变大小，改变颜色等。
<img width="1367" alt="Screenshot 2023-08-22 at 16 23 17" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/17e73f89-61ee-441c-82b5-691dac55fc40">

<img width="1444" alt="Screenshot 2023-08-22 at 16 36 20" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/94a97c02-05ff-4301-aac6-36c17ccb0b44">

##### 4) mysql 数据库连接，查询数据

      prompt :
   
      connect to the mysql server by the connection information:（
       host="codex-sample-server.mysql.database.azure.com",
       user="huqianghui",
       password="XXXXX",
       database="codex-sample"
   )，query the books table, group by column "authors" of top 5 in bar picture.
   
   <img width="1503" alt="262365764-8d27646a-aef1-471a-940d-b79cc1f54664" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/cba42275-8e3b-470d-82f9-40424fa1bb17">
   
   <img width="1435" alt="Screenshot 2023-08-22 at 21 24 41" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/2308848d-4718-4ebb-9aa7-71da18fe4f3c">


#### f. 运行稳定性优化

##### 1） Kernel 进程默认如果不指定资源cpu和memory会卡主。
   
         指定了2core 4G之后，得到明显好转
         (规范一下资源模版: 
         [为容器和 Pod 分配内存资源](https://kubernetes.io/zh-cn/docs/tasks/configure-pod-container/assign-memory-resource/) | [为容器和 Pods 分配 CPU 资源](https://kubernetes.io/zh-cn/docs/tasks/configure-pod-container/assign-cpu-resource/))
      
        ***如果使用其他的serverless,比如web app或者container app也要对资源做相应的配置***

##### 2） 如果单个azure openAI，用户多的时候，容易出现限流

         通过roundrobin 方式，轮训和retry

##### 3) 上传文件，如果部署多个pod的时候，出现文件找不到。(session也没有粘合)

         [绑定azure file的PVC](https://learn.microsoft.com/en-us/azure/aks/azure-csi-files-storage-provision)
      
         [NFS共享访问](https://learn.microsoft.com/zh-cn/azure/storage/blobs/network-file-system-protocol-support-how-to)
      
         或者serverless对storage的支持。
      
         ***代码都要做相应的调整***

##### 4) 代码出现错过的概率也有

         用python语法树，做语法检查。然后inject prompt，再re-generate code
      
         支持pip install 通过正则匹配过滤掉

##### 5) 使用过程中，数据出现错误，比如null值等。包括生成的代码里面运行时异常

         常见问候，导致的代码错误，通过拒绝回答来避免错误
      
         比如去访问的数据结构，比如询问天气，调用的API是401错误，但是没有判断，所以接下来会出现runtime Exception，不生成python来规避
      
         数据空指针等，目前应对，实际情况，考虑prompt内置一些防御的prompt，比如过滤null等让用户体验更好。

##### 6）回答的内容，需要用用户的语言来描述和注释

         用azure TextAnalyticsClient来检测语言的时候，***也有随机性如果输入太少比如：你好经常识别成英语，如果指定地域cn的话，容易识别成 繁体字***

##### 7） 在matlibplot中，图片中的字体乱码。
      
本地安装字体，然后指定一下字体内容。可以在font文档夹中获取到。

把font放到拷贝到：

   ~/python3.10/site-packages/matplotlib/mpl-data/fonts/ttf

修改文件：

   ~/python3.10/site-packages/matplotlib/mpl-data/matplotlibrc
   #font.sans-serif: SimHei,

效果如下图： 中文可以正常显示：

<img width="900" alt="Screenshot 2023-09-13 at 15 34 44" src="https://github.com/huqianghui/GPT-Code-Interpreter/assets/7360524/70f43b92-adb8-4290-90df-47e2f93f63fa">
   
 
#### g. 后续功能优化
      1. user kernel_env 隔离
      （https://github.com/dasmy/gpt-code-ui/tree/dev/kernel_env）
      （https://github.com/shroominic/codebox-api/tree/main）
      2. user session 管理（https://github.com/dasmy/gpt-code-ui/tree/dev/session_management）









