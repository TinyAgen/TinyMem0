# 极简化记忆系统 - 学习项目

> **⚠️ 学习项目声明**: 这是一个用于学习和研究目的的开源项目，旨在探索和实现基于向量数据库的智能记忆系统。本项目仅供学习交流使用，不适用于生产环境。

## 项目概述

这是一个基于Qdrant向量数据库和Qwen大语言模型的智能记忆系统**学习项目**，支持记忆的写入、检索和处理。通过这个项目，您可以学习：

- 向量数据库的实际应用
- 大语言模型在记忆系统中的应用
- 语义搜索的实现原理
- 记忆冲突处理机制
- 智能记忆系统的架构设计

## 学习目标

通过本项目的学习，您将掌握：

1. **向量数据库集成**: 学习如何使用Qdrant进行向量存储和检索
2. **LLM应用开发**: 了解如何将大语言模型集成到实际应用中
3. **语义搜索实现**: 掌握基于向量相似度的智能搜索技术
4. **记忆冲突处理**: 学习如何处理和解决记忆系统中的冲突
5. **系统架构设计**: 理解智能记忆系统的整体架构设计

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

## 学习环境搭建

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

**注意**: 请确保您有有效的API密钥用于学习目的：

```
DASHSCOPE_API_KEY=your_actual_api_key_here
```

## 学习使用方法

### 基本使用示例

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

### 运行学习示例

```bash
python example.py
```

## 学习架构分析

### 文件结构

```
mini_mem/
├── memory_system.py      # 核心记忆系统 - 学习重点
├── prompt.py            # Prompt定义和管理 - 学习LLM应用
├── example.py           # 使用示例 - 学习如何使用
├── requirements.txt     # 依赖包
└── README.md           # 详细文档
```

### 核心学习组件

1. **MemorySystem**: 主记忆系统类 - 学习系统设计
   - `extract_facts()`: 从对话中提取事实 - 学习LLM应用
   - `search_memories()`: 语义搜索记忆 - 学习向量搜索
   - `process_memory()`: 处理记忆冲突 - 学习冲突解决
   - `write_memory()`: 记忆写入主流程 - 学习系统流程

2. **向量数据库**: Qdrant - 学习向量数据库应用
   - 存储记忆的向量表示
   - 支持语义搜索
   - 元数据过滤

3. **大语言模型**: Qwen - 学习LLM集成
   - 事实提取
   - 记忆冲突处理
   - 文本向量化

### 学习工作流程

1. **记忆写入流程**:
   ```
   用户对话 → 提取事实 → 检索相关记忆 → 处理冲突 → 更新数据库
   ```

2. **记忆搜索流程**:
   ```
   查询 → 向量化 → 语义搜索 → 过滤 → 返回结果
   ```

## 学习API参考

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

## 学习Prompt管理

### Prompt模块

系统使用专门的`prompt.py`模块来管理所有的prompt定义，这是学习LLM应用的重要部分：

- **FACT_EXTRACTION_PROMPT**: 用于从用户对话中提取事实和偏好的prompt
- **MEMORY_PROCESSING_PROMPT**: 用于处理记忆冲突和更新的prompt
- **PromptManager**: 提供统一的prompt访问接口

## 学习建议

1. **从example.py开始**: 先运行示例代码，理解基本用法
2. **阅读源码**: 深入理解memory_system.py的实现原理
3. **修改参数**: 尝试调整相似度阈值、搜索限制等参数
4. **扩展功能**: 基于现有代码添加新的记忆处理逻辑
5. **性能优化**: 学习如何优化向量搜索和LLM调用

## 学习资源

- [Qdrant官方文档](https://qdrant.tech/documentation/)
- [Qwen模型介绍](https://github.com/QwenLM/Qwen)
- [向量数据库应用指南](https://www.pinecone.io/learn/)

## 贡献学习

欢迎提交学习心得、代码改进建议或问题报告！

---

**免责声明**: 本项目仅用于学习和研究目的，使用者需自行承担使用风险。

