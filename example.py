#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆系统使用示例
"""

from memory_system import MemorySystem

def main():
    """主函数 - 演示记忆系统的使用"""
    import os 
    os.environ["DASHSCOPE_API_KEY"] = "sk-b8a3efbe07694d1484569b00fad91104"
    # 初始化记忆系统
    print("初始化记忆系统...")
    memory_system = MemorySystem()
    
    # 示例1: 写入记忆
    print("\n=== 示例1: 写入记忆 ===")
    conversation1 = "你好，我叫张三，是一名软件工程师，我喜欢看电影，特别是科幻片。"
    print(f"用户对话: {conversation1}")
    
    memory_system.write_memory(
        conversation=conversation1,
        user_id="user_001",
        agent_id="agent_001"
    )
    
    # 示例2: 搜索记忆
    print("\n=== 示例2: 搜索记忆 ===")
    query = "张三的职业是什么？"
    print(f"搜索查询: {query}")
    
    results = memory_system.search_memory(
        query=query,
        user_id="user_001",
        agent_id="agent_001",
        limit=3
    )
    
    print("搜索结果:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['text']} (相似度: {result['score']:.3f})")
    
    # 示例3: 更新记忆
    print("\n=== 示例3: 更新记忆 ===")
    conversation2 = "我最近改变了职业，现在是一名产品经理，不再做软件工程师了。"
    print(f"用户对话: {conversation2}")
    
    memory_system.write_memory(
        conversation=conversation2,
        user_id="user_001",
        agent_id="agent_001"
    )
    
    # 再次搜索验证更新
    print("\n更新后再次搜索:")
    results = memory_system.search_memory(
        query="张三的职业",
        user_id="user_001",
        agent_id="agent_001",
        limit=3
    )
    

def test_fact_extraction():
    """测试事实提取功能"""
    print("\n=== 测试事实提取 ===")
    
    memory_system = MemorySystem()
    
    test_conversations = [
        "你好",
        "我叫李四，今年25岁",
        "我最喜欢的电影是《泰坦尼克号》",
        "我计划下周去北京旅游",
        "我不喜欢吃辣的食物",
        "我是一名医生，在医院工作"
    ]
    
    for conversation in test_conversations:
        print(f"\n对话: {conversation}")
        facts = memory_system.extract_facts(conversation)
        print(f"提取的事实: {facts}")

if __name__ == "__main__":
    # 运行主示例
    main()
    
    # 运行事实提取测试
    # test_fact_extraction() 