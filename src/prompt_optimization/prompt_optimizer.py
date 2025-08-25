import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..content_generation.llm_client import LLMClient

class PromptOptimizer:
    def __init__(self):
        self.llm_client = LLMClient()
    
    def analyze_prompt(self, original_prompt: str) -> Dict[str, Any]:
        analysis_prompt = f"""
请分析以下提示词的质量和结构：

原始提示词：
{original_prompt}

请从以下几个方面进行分析：
1. 清晰度 - 提示词是否表达清楚
2. 具体性 - 是否有足够的具体信息
3. 结构性 - 逻辑结构是否合理
4. 完整性 - 是否包含必要的要素
5. 可操作性 - AI是否能够理解和执行

对每个方面给出1-10分的评分，并简要说明理由。
同时指出存在的主要问题和改进空间。

请以JSON格式返回分析结果：
{{
    "clarity_score": 分数,
    "clarity_comment": "评价",
    "specificity_score": 分数,
    "specificity_comment": "评价",
    "structure_score": 分数,
    "structure_comment": "评价",
    "completeness_score": 分数,
    "completeness_comment": "评价",
    "actionability_score": 分数,
    "actionability_comment": "评价",
    "overall_score": 总分,
    "main_issues": ["问题1", "问题2"],
    "improvement_areas": ["改进点1", "改进点2"]
}}
"""
        
        try:
            analysis_text = self.llm_client.generate(analysis_prompt, max_tokens=1500)
            
            scores = self._extract_scores(analysis_text)
            issues = self._extract_issues(analysis_text)
            
            return {
                "original_prompt": original_prompt,
                "analysis": analysis_text,
                "scores": scores,
                "issues": issues,
                "analyzed_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"分析失败: {str(e)}",
                "original_prompt": original_prompt
            }
    
    def optimize_prompt(
        self, 
        original_prompt: str, 
        optimization_goal: str = "全面优化",
        target_domain: str = "通用"
    ) -> Dict[str, Any]:
        
        goal_descriptions = {
            "全面优化": "从各个方面全面提升提示词质量",
            "提高清晰度": "重点提升表达的清晰度和准确性",
            "增强具体性": "增加具体的细节和要求",
            "改进结构": "优化逻辑结构和组织方式",
            "提升可操作性": "让AI更容易理解和执行"
        }
        
        domain_contexts = {
            "通用": "适用于各种场景的通用优化",
            "写作": "专门针对文本创作和写作任务",
            "分析": "适用于数据分析和研究任务",
            "创意": "针对创意设计和创新思维",
            "技术": "适用于技术文档和编程任务",
            "教育": "针对教学和培训内容",
            "营销": "适用于营销和推广内容"
        }
        
        optimization_prompt = f"""
请优化以下提示词，使其更加有效和专业：

原始提示词：
{original_prompt}

优化目标：{goal_descriptions.get(optimization_goal, optimization_goal)}
应用领域：{domain_contexts.get(target_domain, target_domain)}

请提供以下内容：
1. 优化后的提示词（完整版本）
2. 主要改进点说明
3. 为什么这样改进
4. 预期效果提升
5. 使用建议

优化原则：
- 保持原始意图不变
- 增加必要的上下文信息
- 提供清晰的格式要求
- 添加具体的评价标准
- 包含角色设定（如需要）
- 提供输出格式指导

请以以下JSON格式返回：
{{
    "optimized_prompt": "优化后的完整提示词",
    "improvements": [
        {{
            "aspect": "改进方面",
            "before": "原来的问题",
            "after": "改进后的优点",
            "reason": "改进理由"
        }}
    ],
    "expected_benefits": ["预期收益1", "预期收益2"],
    "usage_tips": ["使用建议1", "使用建议2"],
    "confidence_score": 评分(1-10)
}}
"""
        
        try:
            optimization_result = self.llm_client.generate(optimization_prompt, max_tokens=3000)
            
            return {
                "original_prompt": original_prompt,
                "optimization_goal": optimization_goal,
                "target_domain": target_domain,
                "result": optimization_result,
                "optimized_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"优化失败: {str(e)}",
                "original_prompt": original_prompt
            }
    
    def generate_prompt_variations(self, base_prompt: str, variation_count: int = 3) -> Dict[str, Any]:
        variation_prompt = f"""
基于以下基础提示词，生成{variation_count}个不同的变体版本：

基础提示词：
{base_prompt}

请为每个变体提供：
1. 变体提示词内容
2. 变体特点说明（与原版本的主要差异）
3. 适用场景建议
4. 预期输出风格差异

变体要求：
- 保持核心目标一致
- 每个变体有不同的表达方式或侧重点
- 覆盖不同的使用场景或风格偏好
- 长度可以有所不同

请以JSON格式返回：
{{
    "base_prompt": "基础提示词",
    "variations": [
        {{
            "id": 1,
            "prompt": "变体提示词1",
            "characteristics": "特点说明",
            "use_cases": "适用场景",
            "output_style": "输出风格"
        }}
    ]
}}
"""
        
        try:
            variations_result = self.llm_client.generate(variation_prompt, max_tokens=3000)
            
            return {
                "base_prompt": base_prompt,
                "variation_count": variation_count,
                "variations": variations_result,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"生成变体失败: {str(e)}",
                "base_prompt": base_prompt
            }
    
    def create_structured_prompt(
        self,
        task_description: str,
        output_format: str = "文本",
        role_context: str = "",
        constraints: List[str] = None,
        examples: List[str] = None
    ) -> Dict[str, Any]:
        
        constraints = constraints or []
        examples = examples or []
        
        structure_template = f"""
# 任务描述
{task_description}

"""
        
        if role_context:
            structure_template += f"# 角色设定\n{role_context}\n\n"
        
        if constraints:
            structure_template += "# 约束条件\n"
            for i, constraint in enumerate(constraints, 1):
                structure_template += f"{i}. {constraint}\n"
            structure_template += "\n"
        
        structure_template += f"# 输出格式\n{output_format}\n\n"
        
        if examples:
            structure_template += "# 示例\n"
            for i, example in enumerate(examples, 1):
                structure_template += f"## 示例{i}\n{example}\n\n"
        
        structure_template += "# 执行要求\n请严格按照以上要求完成任务，确保输出质量和格式正确性。"
        
        return {
            "structured_prompt": structure_template,
            "components": {
                "task_description": task_description,
                "role_context": role_context,
                "output_format": output_format,
                "constraints": constraints,
                "examples": examples
            },
            "created_at": datetime.now().isoformat()
        }
    
    def _extract_scores(self, analysis_text: str) -> Dict[str, int]:
        scores = {}
        
        score_patterns = {
            "clarity_score": r"清晰度.*?(\d+)",
            "specificity_score": r"具体性.*?(\d+)",
            "structure_score": r"结构性.*?(\d+)",
            "completeness_score": r"完整性.*?(\d+)",
            "actionability_score": r"可操作性.*?(\d+)",
            "overall_score": r"总分.*?(\d+)"
        }
        
        for score_name, pattern in score_patterns.items():
            match = re.search(pattern, analysis_text)
            if match:
                scores[score_name] = int(match.group(1))
            else:
                scores[score_name] = 0
        
        return scores
    
    def _extract_issues(self, analysis_text: str) -> List[str]:
        issues = []
        
        issues_match = re.search(r"主要问题.*?:(.*?)改进", analysis_text, re.DOTALL)
        if issues_match:
            issues_text = issues_match.group(1)
            issues = [issue.strip() for issue in issues_text.split('\n') if issue.strip() and not issue.strip().startswith('-')]
        
        return issues[:5]
    
    def batch_optimize_prompts(self, prompts: List[str], **kwargs) -> Dict[str, Any]:
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"优化提示词 {i+1}/{len(prompts)}")
            
            analysis = self.analyze_prompt(prompt)
            optimization = self.optimize_prompt(prompt, **kwargs)
            
            results.append({
                "original_prompt": prompt,
                "analysis": analysis,
                "optimization": optimization
            })
        
        return {
            "results": results,
            "total_processed": len(prompts),
            "processed_at": datetime.now().isoformat()
        }