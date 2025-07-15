import json
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import dashscope
from dashscope import Generation

# 导入prompt模块
from prompt import FACT_EXTRACTION_PROMPT, MEMORY_PROCESSING_PROMPT
# 导入工具函数
from util import extract_llm_response_content, parse_json_response, extract_embedding_from_response, call_llm_with_prompt, handle_llm_error

class MemorySystem:
    def __init__(self, collection_name: str = "memories", llm_model: str = "qwen-turbo", embedding_model: str = "text-embedding-v1"):
        """
        初始化记忆系统
        
        Args:
            collection_name: Qdrant集合名称
        """
        self.collection_name = collection_name
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        
        # 初始化Qdrant客户端，使用本地文件存储
        self.qdrant_client = QdrantClient(path="./qdrant_data")
        
        # 设置API密钥
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        # 初始化集合
        self._init_collection()
    
    def _init_collection(self):
        """初始化Qdrant集合"""
        collections = self.qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if self.collection_name not in collection_names:
            # 创建新集合
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"✅ 创建集合: {self.collection_name}")
        else:
            print(f"✅ 使用现有集合: {self.collection_name}")

    
    def extract_facts(self, conversation: str) -> List[str]:
        """
        从对话中提取事实信息
        
        Args:
            conversation: 用户对话内容
            
        Returns:
            提取的事实列表
        """
        result = call_llm_with_prompt(self.llm_model, FACT_EXTRACTION_PROMPT, conversation)
        
        if result:
            return parse_json_response(result, 'facts')
        else:
            return []
     
    
    def get_embeddings(self, text: str, operation: str = "search") -> List[float]:
        """
        获取文本的向量嵌入
        
        Args:
            text: 输入文本
            operation: 操作类型 ("search" 或 "add")
            
        Returns:
            向量嵌入
        """
        try:
            # 使用配置的embedding模型
            response = dashscope.TextEmbedding.call(
                model=self.embedding_model,
                input=text
            )
            
            return extract_embedding_from_response(response)
        except Exception as e:
            print(f"获取嵌入异常: {e}")
            return []
    
    def search_memories(self, query: str, filters: Optional[Dict] = None, 
                       limit: int = 5, threshold: Optional[float] = None) -> List[Dict]:
        """
        搜索相关记忆
        
        Args:
            query: 搜索查询
            filters: 过滤条件
            limit: 返回结果数量限制
            threshold: 相似度阈值
            
        Returns:
            相关记忆列表
        """
        try:
            embeddings = self.get_embeddings(query, "search")
            if not embeddings:
                return []
            
            # 构建Qdrant过滤器
            query_filter = None
            if filters:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                conditions = []
                for key, value in filters.items():
                    conditions.append(FieldCondition(key=f"metadata.{key}", match=MatchValue(value=value)))
                query_filter = Filter(must=conditions)
            
            # 执行向量搜索
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=embeddings,
                limit=limit,
                query_filter=query_filter,
                score_threshold=threshold
            )
            
            memories = []
            for result in search_result:
                memories.append({
                    "id": result.id,
                    "text": result.payload.get("data", ""),
                    "score": result.score,
                    "metadata": result.payload.get("metadata", {})
                })
            
            return memories
        except Exception as e:
            print(f"搜索记忆失败: {e}")
            return []
    
    def process_memory(self, new_facts: List[str], existing_memories: List[Dict]) -> List[Dict]:
        """
        处理记忆，决定添加、更新、删除或不做操作
        
        Args:
            new_facts: 新提取的事实
            existing_memories: 现有记忆
            
        Returns:
            处理后的记忆列表
        """
        try:
            # 准备输入数据
            input_data = {
                "new_facts": new_facts,
                "existing_memories": existing_memories
            }
            
            result = call_llm_with_prompt(
                self.llm_model, 
                MEMORY_PROCESSING_PROMPT, 
                json.dumps(input_data, ensure_ascii=False)
            )
            
            if result:
                return parse_json_response(result, 'memory')
            else:
                return []
        except Exception as e:
            print(f"处理记忆异常: {e}")
            return []
    
    def add_memory(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        添加新记忆
        
        Args:
            text: 记忆内容
            metadata: 元数据
            
        Returns:
            记忆ID
        """
        try:
            embeddings = self.get_embeddings(text, "add")
            if not embeddings:
                return ""
            
            memory_id = str(uuid.uuid4())
            point = PointStruct(
                id=memory_id,
                vector=embeddings,
                payload={
                    "data": text,
                    "metadata": metadata or {},
                    "created_at": datetime.now().isoformat()
                }
            )
            
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            return memory_id
        except Exception as e:
            print(f"添加记忆失败: {e}")
            return ""
    
    def update_memory(self, memory_id: str, new_text: str, metadata: Optional[Dict] = None):
        """
        更新记忆
        
        Args:
            memory_id: 记忆ID
            new_text: 新的记忆内容
            metadata: 新的元数据
        """
        try:
            embeddings = self.get_embeddings(new_text, "add")
            if not embeddings:
                return
            
            point = PointStruct(
                id=memory_id,
                vector=embeddings,
                payload={
                    "data": new_text,
                    "metadata": metadata or {},
                    "updated_at": datetime.now().isoformat()
                }
            )
            
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
        except Exception as e:
            print(f"更新记忆失败: {e}")
    
    def delete_memory(self, memory_id: str):
        """
        删除记忆
        
        Args:
            memory_id: 记忆ID
        """
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[memory_id]
            )
        except Exception as e:
            print(f"删除记忆失败: {e}")
    
    def write_memory(self, conversation: str, user_id: str = None, agent_id: str = None):
        """
        记忆写入主流程
        
        Args:
            conversation: 用户对话
            user_id: 用户ID
            agent_id: 代理ID
        """
        # 1. 提取事实
        new_facts = self.extract_facts(conversation)
        if not new_facts:
            print("未提取到相关事实")
            return
        
        print(f"提取到的事实: {new_facts}")
        
        # 2. 检索相关记忆
        retrieved_old_memory = []
        for new_fact in new_facts:
            # 构建过滤条件
            filters = {}
            if user_id:
                filters["user_id"] = user_id
            if agent_id:
                filters["agent_id"] = agent_id
            
            # 搜索相关记忆
            existing_memories = self.search_memories(
                query=new_fact,
                filters=filters,
                limit=5
            )
            
            for mem in existing_memories:
                retrieved_old_memory.append({
                    "id": mem["id"],
                    "text": mem["text"]
                })
        
        print(f"检索到的相关记忆: {retrieved_old_memory}")
        
        # 3. 处理记忆
        processed_memories = self.process_memory(new_facts, retrieved_old_memory)
        
        # 4. 执行记忆操作
        for memory in processed_memories:
            event = memory.get("event", "NONE")
            memory_id = memory.get("id")
            text = memory.get("text")
            
            metadata = {
                "user_id": user_id,
                "agent_id": agent_id,
                "created_at": datetime.now().isoformat()
            }
            
            if event == "ADD":
                self.add_memory(text, metadata)
                print(f"添加记忆: {text}")
            elif event == "UPDATE":
                self.update_memory(memory_id, text, metadata)
                print(f"更新记忆: {text}")
            elif event == "DELETE":
                self.delete_memory(memory_id)
                print(f"删除记忆: {memory_id}")
            elif event == "NONE":
                print(f"保持记忆不变: {text}")
    
    def search_memory(self, query: str, user_id: str = None, agent_id: str = None, 
                     limit: int = 5) -> List[Dict]:
        """
        记忆搜索
        
        Args:
            query: 搜索查询
            user_id: 用户ID
            agent_id: 代理ID
            limit: 返回结果数量
            
        Returns:
            相关记忆列表
        """
        # 构建过滤条件
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if agent_id:
            filters["agent_id"] = agent_id
        
        return self.search_memories(query, filters, limit) 