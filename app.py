from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from flask_cors import CORS

app = Flask(__name__)

# Cấu hình CORS cho cả localhost và domain thực tế
CORS(app, resources={r"/ask": {"origins": ["http://localhost:62416", "https://booksaw.nguyenlethanhphong.io.vn"]}})

# Lấy API key từ biến môi trường
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json["message"]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Đây là câu hỏi: " + user_message + ", câu trả lời tối đa 200 token mà không làm mất nội dung, kiểm tra lại trước khi phản hồi để đảm bảo tính chính xác, chỉ trả lời khi biết chính xác 100%, sách nằm trong sách được bán bởi Amazon, nếu tên sách là sách bạn chưa bao giờ nghe qua, hãy trả lời không biết"}
        ],
        temperature=1,
        max_tokens=225,
        top_p=1,
    )

    reply = response.choices[0].message.content
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    cached_tokens = 0  # API mới không có cached_tokens, đặt mặc định 0

    # Đường dẫn file json để lưu (tạm thời bỏ qua trên Heroku)
    usage_file = "token_usage.json"

    # Bước 1: Đọc file nếu đã tồn tại (bỏ qua trên Heroku)
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

    # Bước 3: Ghi lại vào file (comment để tránh lỗi trên Heroku)
    # with open(usage_file, "w") as f:
    #     json.dump(current_data, f, indent=4)

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
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)