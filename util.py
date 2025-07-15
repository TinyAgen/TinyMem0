import json
import re
from typing import List, Dict, Optional, Any
from dashscope import Generation


def extract_llm_response_content(response) -> Optional[str]:
    """
    从LLM响应中提取内容
    
    Args:
        response: LLM API响应对象
        
    Returns:
        提取的响应内容，如果失败返回None
    """
    if not response or response.status_code != 200:
        return None
    
    # 检查响应结构，兼容不同的返回格式
    if hasattr(response.output, 'choices') and response.output.choices:
        return response.output.choices[0].message.content
    elif hasattr(response.output, 'text'):
        return response.output.text
    else:
        print("无法获取响应内容")
        return None


def parse_json_response(response_text: str, expected_key: str = None) -> List[Dict]:
    """
    解析LLM的JSON响应
    
    Args:
        response_text: LLM返回的文本
        expected_key: 期望的JSON键名
        
    Returns:
        解析后的数据列表
    """
    try:
        # 尝试直接解析JSON
        data = json.loads(response_text)
        if expected_key:
            return data.get(expected_key, [])
        return data
    except json.JSONDecodeError:
        # 如果直接解析失败，尝试提取JSON部分
        try:
            # 查找JSON对象
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                if expected_key:
                    return data.get(expected_key, [])
                return data
            else:
                print(f"无法找到JSON内容: {response_text}")
                return []
        except Exception as e:
            print(f"JSON解析失败: {response_text}")
            print(f"解析错误: {e}")
            return []


def extract_embedding_from_response(response) -> List[float]:
    """
    从嵌入API响应中提取向量
    
    Args:
        response: 嵌入API响应对象
        
    Returns:
        向量嵌入列表
    """
    if not response or response.status_code != 200:
        return []
    
    # 检查响应结构，兼容不同的返回格式
    if hasattr(response.output, 'embeddings') and response.output.embeddings:
        return response.output.embeddings[0].embedding
    elif hasattr(response.output, 'data') and response.output.data:
        return response.output.data[0].embedding
    elif isinstance(response.output, dict) and 'embeddings' in response.output:
        return response.output['embeddings'][0]['embedding']
    else:
        print(f"无法获取嵌入向量，响应结构: {response.output}")
        return []


def call_llm_with_prompt(model: str, system_prompt: str, user_content: str) -> Optional[str]:
    """
    调用LLM并处理响应
    
    Args:
        model: 模型名称
        system_prompt: 系统提示词
        user_content: 用户内容
        
    Returns:
        处理后的响应内容
    """
    try:
        response = Generation.call(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_content}
            ],
            result_format='message'
        )
        
        return extract_llm_response_content(response)
    except Exception as e:
        print(f"LLM调用异常: {e}")
        return None


def handle_llm_error(response, operation_name: str = "操作"):
    """
    处理LLM错误
    
    Args:
        response: LLM响应对象
        operation_name: 操作名称
    """
    error_msg = f"{operation_name}失败: {response.status_code if response else 'No response'}"
    print(error_msg)
    if response and hasattr(response, 'message'):
        print(f"错误信息: {response.message}")