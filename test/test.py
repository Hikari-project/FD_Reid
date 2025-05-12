# -*- coding: UTF-8 -*-
'''
@Project :FD_Reid_Web 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/07 17:47 
@Describe:
'''
# -*- coding: UTF-8 -*-
'''
@Project :main.py 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/05/06 14:05 
@Describe:
'''
from openai import OpenAI
import httpx
import os


# 新增：自定义传输层，用于修改 HTTP 请求头以适配 APISIX 的 key-auth 插件
class CustomTransport(httpx.BaseTransport):
    def __init__(self, api_key):
        # 保存 API 密钥，用于设置 apikey 头
        self.api_key = api_key
        # 创建底层 httpx 传输对象，处理实际 HTTP 请求
        self._transport = httpx.HTTPTransport()

    def handle_request(self, request):
        # 移除 OpenAI SDK 默认的 Authorization 头（Bearer <api_key>）
        if "Authorization" in request.headers:
            del request.headers["Authorization"]

        # 添加 APISIX key-auth 插件要求的 apikey 头
        request.headers["apikey"] = self.api_key

        # 传递修改后的请求到 httpx 传输层
        return self._transport.handle_request(request)


# 新增：创建自定义 httpx 客户端，集成 CustomTransport
def get_custom_http_client(api_key):
    return httpx.Client(
        transport=CustomTransport(api_key),  # 使用自定义传输层
        timeout=30.0  # 设置 30 秒超时，适应 vLLM 响应时间
    )


# 修改：配置 OpenAI 客户端，使用自定义 httpx 客户端以发送 apikey 头
client = OpenAI(
    api_key="Wv5h2jpbsqD40jwtGyS0hMa7XVert6Un",  # 提供但不使用，防止 SDK 报错
    base_url="https://apiai.sztu.edu.cn:9443/v1",  # APISIX 路由入口
    http_client=get_custom_http_client("Wv5h2jpbsqD40jwtGyS0hMa7XVert6Un")  # 注入自定义客户端
)


def stream_chat_response(messages):
    """
    流式获取ChatGPT的回答
    """
    # 新增：添加异常处理以提高健壮性
    try:
        stream = client.chat.completions.create(
            model="qwen3-235b",
            messages=messages,
            stream=True,
            temperature=0.7,
        )

        full_response = []
        # 修改：使用 hasattr 检查 delta 属性，防止属性缺失
        for chunk in stream:
            if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta.content is not None:
                chunk_content = chunk.choices[0].delta.content
                print(chunk_content, end="", flush=True)  # 实时流式输出
                full_response.append(chunk_content)
        return "".join(full_response)
    # 新增：处理用户中断
    except KeyboardInterrupt:
        print("\n用户中断了生成")
        return "（回答被中断）"
    # 新增：捕获其他异常
    except Exception as e:
        print(f"\n生成过程出错: {e}")
        return f"（生成出错: {e}）"


def main():
    messages = []  # 保存对话历史
    print("ChatGPT流式交互示例（输入 'exit' 退出）")
    while True:
        user_input = input("\n\nYou: ")
        if user_input.lower() == "exit":
            # 新增：添加退出提示
            print("\n再见！")
            break
        # 将用户输入加入对话历史
        messages.append({"role": "user", "content": user_input})
        print("\nAssistant: ", end="", flush=True)
        # 新增：异常处理以防止交互中断
        try:
            # 获取流式响应并保存完整回答
            assistant_response = stream_chat_response(messages)
            messages.append({"role": "assistant", "content": assistant_response})
        except Exception as e:
            print(f"\n出错了: {e}")
            continue


if __name__ == "__main__":
    main()


item={
    "553690":107,
    "1511240":27,
    "179348":57,
    "182047":38,
    "88100":39,
    "235451":865,





}