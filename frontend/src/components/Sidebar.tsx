import AssistantIcon from '@mui/icons-material/Assistant';

import "./Sidebar.css";

export default function Sidebar(props: {
  models: Array<{ name: string; displayName: string }>;
  selectedModel: string;
  onSelectModel: any;
  setOpenAIKey: any;
  openAIKey: string;
}) {
  return (
    <>
      <div className="sidebar">
        <div className="logo">
            <AssistantIcon /> Advanced Data Analysis

            <div className='github'>
                <a href='https://github.com/huqianghui/GPT-Code-Interpreter'>Open Source - v2.0.0</a>
            </div>
            <div>
              <br/>
            </div>
            <div>
            <div className="content">您好！我是您的高级数据分析师助理。<br/>
                可以为您效劳数据相关的任何事情！<br/>
                <br/>  
                温馨提示:<br/> 
                <br/> 
                        1. 您可以上传一个文件（excel，csv等等），<br/>
                        我可以基于它来做数据分析和展示。<br/> 
                        <br/> 
                        2. 如果遇到问题，只需键入“reset”，我将重新启动内核。<br/>
                        <br/> 
                        3. 你可以用英文或者中文来提出问题。<br/>
                        <br/> 
                        4. 如果后端配置数据库， <br/>
                          那么可以询问基于数据库的数据，提出您的问题<br/>
                          以"@sql"开始，例如：@sql，查询books表，<br/>
                          按照"authors"列的前5名进行分组，生成柱状图。 <br/>
                          并且"authors"列不为空。
                        <br/> 
            </div>
            <div>
              <br/>
            </div>
            <div className="content">Hello! I'm an Advanced Data Analysis.<br/>
                Ask me to do something for you!<br/>
                <br/>  
                Pro tip:<br/> 
                <br/> 
                        1. You can upload a file and I'll be able to use it.<br/>
                        <br/> 
                        2. If I get stuck just type 'reset' and I'll restart the kernel.<br/>
                        <br/> 
                        3. You also can use Chinese to ask any questions.<br/>
                        <br/> 
                        4. If you config database, <br/>
                          then you can ask questions about database,<br/>
                          start with "@sql" for example: @sql,query the books table,<br/>
                          group by column "authors" of top 5 in bar picture <br/>
                          and the column "authors" is not null.
                        <br/> 
            </div>
            

        </div>

        </div>
        

        <div className="settings">
            <label className="header">Settings</label>
            <label>Model</label>
            <select
            value={props.selectedModel}
            onChange={(event) => props.onSelectModel(event.target.value)}
            >
            {props.models.map((model, index) => {
                return (
                <option key={index} value={model.name}>
                    {model.displayName}
                </option>
                );
            })}
            </select>
        </div>
      </div>
    </>
  );
}
