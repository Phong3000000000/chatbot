from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
from flask_cors import CORS

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Cấu hình CORS chỉ cho endpoint /ask và chỉ cho phép origin cụ thể - ở đây là 62416 là cổng front end chạy cshtml
CORS(app, resources={r"/ask": {"origins": "http://localhost:62416"}})

client = OpenAI(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json["message"]

    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",  # hoặc "gpt-3.5-turbo"
    #     messages=[
    #         {"role": "user", "content": user_message + " gói gọn câu trả lời trong 200 token"}
    #     ],
    #     temperature=1,
    #     max_tokens=200,
    #     top_p=1,
    #     store=False
    # )

    # tinnhan = user_message + ", câu trả lời tối đa 200 token mà không làm mất nội dung"
    # print(tinnhan)


    response = client.responses.create(
    model="gpt-4o-mini",  
    input=[
        {
            "type": "message",
            "role": "user",
            "content": "Đây là câu hỏi: " + user_message + ", câu trả lời tối đa 200 token mà không làm mất nội dung, kiểm tra lại trước khi phản hồi để đảm bảo tính chính xác, chỉ trả lời khi biết chính xác 100%, sách nằm trong sách được bán bởi amazon, nếu tên sách là sách bạn chưa bao giờ nghe qua, hãy trả lời không biết"
        }
    ],
    temperature=1,
    max_output_tokens=225,
    top_p=1,
    store=True)

    # ý tưởng phát triển - kiểm tra sách có trong database hay không, nếu có thì hiển thị link đến detail của sách đó, nếu ko có thì thông báo là không có bán và xin lỗi người dùng

    reply = response.output[0].content[0].text
    input_tokens = response.usage.input_tokens
    cached_tokens = response.usage.input_tokens_details.cached_tokens
    output_tokens = response.usage.output_tokens
    total_tokens = response.usage.total_tokens

    # Đường dẫn file json để lưu
    usage_file = "token_usage.json"

    # Bước 1: Đọc file nếu đã tồn tại
    if os.path.exists(usage_file):
        with open(usage_file, "r") as f:
            current_data = json.load(f)
    else:
        current_data = {
            "total_input_tokens": 0,
            "total_cached_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0
        }

    # Bước 2: Cộng dồn
    current_data["total_input_tokens"] += input_tokens
    current_data["total_cached_tokens"] += cached_tokens
    current_data["total_output_tokens"] += output_tokens
    current_data["total_tokens"] += total_tokens

    # Bước 3: Ghi lại vào file
    with open(usage_file, "w") as f:
        json.dump(current_data, f, indent=4)



    return jsonify({
        "reply": reply,
        "tokens": {
            "input_tokens": input_tokens,
            "cached_tokens": cached_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }
    })

if __name__ == "__main__":
    app.run(debug=True)
