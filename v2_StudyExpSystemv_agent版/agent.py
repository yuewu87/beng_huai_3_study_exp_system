from ollama import Client

class Agent:
    def __init__(self):
        self.client = Client(host='http://localhost:11434')
        self.true_titles = set()  # 新增true缓存
        self.false_titles = set()  # 新增false缓存
        self.prompt_template = """请判断以下窗口标题是否属于学习内容（编程/数学/科学/技术文档/论文/课程）：
        
        "{title}"
        
        回答True或False, 附带解释。"""

    def check_title(self, title: str) -> bool:
        """判断窗口标题是否属于学习内容"""
        # 统一处理标题格式
        normalized_title = title.strip().lower()
        
        # 先检查缓存
        if normalized_title in self.true_titles:
            return True
        if normalized_title in self.false_titles:
            return False
        
        try:
            # 调用模型获取结果
            response = self.client.chat(
                model='qwen2.5:7b',
                messages=[{
                    'role': 'user',
                    'content': self.prompt_template.format(title=title)
                }]
            )
            result = response['message']['content'].strip().lower() == 'true'
            
            # 更新缓存
            if result:
                self.true_titles.add(normalized_title)
            else:
                self.false_titles.add(normalized_title)
                
            return result
        except Exception as e:
            print(f"模型调用失败: {str(e)}")
            return False
        
# 使用示例
if __name__ == "__main__":
    agent = Agent()
    print(agent.check_title("VS Code - 未命名文件"))  # 学习内容