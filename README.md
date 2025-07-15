# 极简化记忆系统

一个基于Qdrant向量数据库和Qwen大语言模型的智能记忆系统，支持记忆的写入、检索和处理。

## 功能特性

### 1. 记忆写入
- **信息提取**: 使用LLM从用户对话中提取相关事实和偏好
- **相关记忆检索**: 通过语义搜索找到相关的已有记忆
- **记忆处理**: 智能决定添加、更新、删除或保持记忆不变
- **冲突处理**: 防止记忆冲突，保持数据一致性

### 2. 记忆搜索
- **元数据检索**: 支持通过user_id和agent_id快速过滤
- **语义检索**: 基于向量相似度的智能搜索
- **相似度阈值**: 可配置的相似度过滤

### 3. 记忆处理
- **ADD**: 添加新记忆
- **UPDATE**: 更新现有记忆
- **DELETE**: 删除冲突或过时的记忆
- **NONE**: 保持记忆不变

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置Qdrant

系统使用Qdrant的本地文件存储模式，无需Docker服务：

```bash
# 数据将存储在 ./qdrant_data 目录中
# 系统会自动创建该目录
```

### 3. 配置API密钥

复制环境变量示例文件并配置你的API密钥：

```bash
cp env_example.txt .env
```

编辑`.env`文件，添加你的DashScope API密钥：

```
DASHSCOPE_API_KEY=your_actual_api_key_here
```

## 使用方法

### 基本使用

```python
from memory_system import MemorySystem

# 初始化记忆系统
memory_system = MemorySystem()

# 写入记忆
memory_system.write_memory(
    conversation="我叫张三，是一名软件工程师，我喜欢看电影",
    user_id="user_001",
    agent_id="agent_001"
)

# 搜索记忆
results = memory_system.search_memory(
    query="张三的职业",
    user_id="user_001",
    agent_id="agent_001"
)

for result in results:
    print(f"记忆: {result['text']}, 相似度: {result['score']}")
```

### 运行示例

```bash
python example.py
```

### 测试Prompt模块

```bash
python test_prompt.py
```

### 运行Prompt示例

```bash
python prompt_example.py
```

## 系统架构

### 文件结构

```
mini_mem/
├── memory_system.py      # 核心记忆系统
├── prompt.py            # Prompt定义和管理
├── example.py           # 使用示例
├── test_memory.py       # 测试脚本
├── test_prompt.py       # Prompt测试脚本
├── requirements.txt     # 依赖包
├── docker-compose.yml   # Qdrant服务配置
├── start.sh            # 快速启动脚本
├── env_example.txt     # 环境变量示例
└── README.md           # 详细文档
```

### 核心组件

1. **MemorySystem**: 主记忆系统类
   - `extract_facts()`: 从对话中提取事实
   - `search_memories()`: 语义搜索记忆
   - `process_memory()`: 处理记忆冲突
   - `write_memory()`: 记忆写入主流程

2. **PromptManager**: Prompt管理类
   - `get_fact_extraction_prompt()`: 获取事实提取prompt
   - `get_memory_processing_prompt()`: 获取记忆处理prompt
   - `get_prompt_by_name()`: 根据名称获取prompt

3. **向量数据库**: Qdrant
   - 存储记忆的向量表示
   - 支持语义搜索
   - 元数据过滤

4. **大语言模型**: Qwen
   - 事实提取
   - 记忆冲突处理
   - 文本向量化

### 工作流程

1. **记忆写入流程**:
   ```
   用户对话 → 提取事实 → 检索相关记忆 → 处理冲突 → 更新数据库
   ```

2. **记忆搜索流程**:
   ```
   查询 → 向量化 → 语义搜索 → 过滤 → 返回结果
   ```

## API参考

### MemorySystem类

#### 初始化
```python
MemorySystem(collection_name: str = "memories")
```

#### 主要方法

- `write_memory(conversation, user_id=None, agent_id=None)`: 写入记忆
- `search_memory(query, user_id=None, agent_id=None, limit=5)`: 搜索记忆
- `extract_facts(conversation)`: 提取事实
- `add_memory(text, metadata=None)`: 添加记忆
- `update_memory(memory_id, new_text, metadata=None)`: 更新记忆
- `delete_memory(memory_id)`: 删除记忆

## Prompt管理

### Prompt模块

系统使用专门的`prompt.py`模块来管理所有的prompt定义：

- **FACT_EXTRACTION_PROMPT**: 用于从用户对话中提取事实和偏好的prompt
- **MEMORY_PROCESSING_PROMPT**: 用于处理记忆冲突和更新的prompt
- **PromptManager**: 提供统一的prompt访问接口

### 使用Prompt

```python
from prompt import PromptManager

# 获取事实提取prompt
fact_prompt = PromptManager.get_fact_extraction_prompt()

# 获取记忆处理prompt
memory_prompt = PromptManager.get_memory_processing_prompt()

# 通过名称获取prompt
prompt = PromptManager.get_prompt_by_name("fact_extraction")
```

## 配置选项

### 环境变量

- `DASHSCOPE_API_KEY`: 阿里云DashScope API密钥
- `QDRANT_HOST`: Qdrant主机地址（默认: localhost）
- `QDRANT_PORT`: Qdrant端口（默认: 6333）

### 系统参数

- 向量维度: 1536
- 距离度量: COSINE
- 默认搜索结果数量: 5
- 集合名称: "memories"

## 注意事项

1. **API密钥**: 确保你有有效的DashScope API密钥
2. **Qdrant服务**: 确保Qdrant服务正在运行
3. **网络连接**: 需要稳定的网络连接访问API服务
4. **数据隐私**: 注意用户数据的隐私保护

## 故障排除

### 常见问题

1. **API调用失败**: 检查API密钥是否正确配置
2. **Qdrant连接失败**: 确保Qdrant服务正在运行
3. **向量维度不匹配**: 确保使用正确的embedding模型

### 调试模式

在代码中添加调试信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 许可证

MIT License 