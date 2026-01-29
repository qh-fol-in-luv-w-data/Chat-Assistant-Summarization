# 🧠 Chat Assistant Demo  
## Session Memory & Ambiguous Query Handling

---

## 1. Mục tiêu project

Project này minh hoạ một **chat assistant backend** có:

### Session Memory
- Lưu hội thoại ngắn hạn (<= 10000 tokens)
- Tự động **tóm tắt (summary)** khi context quá dài

### Ambiguous Query Handling
- Phát hiện câu hỏi mơ hồ / nhiều lỗi chính tả
- Rewrite câu hỏi
- **Hỏi lại để làm rõ (clarifying question)**
- KHÔNG trả lời khi chưa rõ ý

---

## 2. Cấu trúc thư mục & giải thích từng file

```
chat_assistant/
├── main.py
├── demo.py
├── config.py
├── requirements.txt
│
├── memory/
│   ├── session_store.py
│   └── context_manager.py
│
├── query/
│   └── pipeline.py
│
├── data/
│   ├── session.json
│   ├── test_long.jsonl
│   └── test_ambiguous.jsonl
│
└── README.md
```
## 3. Giải thích từng file
```main.py```

- Entry point chính
- Chạy chat assistant dạng CLI
- Gọi run_query_pipeline
- Kết hợp:
    - session memory
    - summary
    - ambiguity handling


```demo.py```

- File demo để test 
- Chạy sẵn 2 flow:
    - Flow 1: hội thoại dài → sinh summary
    - Flow 2: câu mơ hồ → hỏi lại
- Không cần nhập tay


```config.py```

- Chứa các cấu hình chung:
    - model name
    - context limit
    - summary threshold

```requirements.txt```

Danh sách các thư viện cần cài

```memory/session_store.py```

Quản lý session memory
Session gồm:
    - summary
    - recent messages

```memory/context_manager.py```

- Theo dõi độ dài context
- Kiểm tra khi nào vượt ngưỡng
- Gọi LLM để tóm tắt hội thoại
- Reset recent messages sau khi summary

```query/pipeline.py```

Cài đặt run_query_pipeline

```
User Input
   ↓
Ambiguity Analysis
   ↓
Clarifying Question (nếu mơ hồ)
   ↓
Normal Response (nếu rõ)
   ↓
Update Session + Summary

```

```data/session.json```

- Lưu trạng thái hội thoại hiện tại
- Được tạo và cập nhật tự động và sẽ xoá sau khi summary để tránh tràn bộ nhớ

```data/test_long.jsonl```

- Dữ liệu test hội thoại dài
- Dùng để:
    - làm đầy context
    - kích hoạt summary

```data/test_ambiguous.jsonl```

Dữ liệu test câu mơ hồ

## 4. Cài đặt môi trường
**4.1 Tạo virtual environment** 
```
python -m venv .venv
source .venv/bin/activate
```

**4.2 Cài đặt thư viện**
```
pip install -r requirements.txt
```

## 5. Cấu hình API Key

```
export GOOGLE_API_KEY="YOUR_API_KEY"

```
Dùng để set API Key để summary text, dùng bản free với model gemini-flash-2.5

## 6. Chạy DEMO
```
python demo.py
```
**Flow 1 — Session Memory + Summary**
Intput:

Một đoạn hội thoại dài giữa user và assistant

Output mẫu :
```
==============================
🚀 FLOW 1 — SESSION MEMORY DEMO
==============================
[1] Context tokens: 1433
[2] Context tokens: 2518
[3] Context tokens: 2612
[4] Context tokens: 4049
[5] Context tokens: 4126
[6] Context tokens: 5136
[7] Context tokens: 5189
[8] Context tokens: 6114
[9] Context tokens: 6203
[10] Context tokens: 8139
[11] Context tokens: 8180
[12] Context tokens: 9109
[13] Context tokens: 9140
[14] Context tokens: 9895
[15] Context tokens: 9936
[16] Context tokens: 10632
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.

⚠️ Context limit exceeded → summarizing
🧠 Generated summary:
{
  "session_summary": {
    "user_profile": {
      "prefs": [
        "Wants detailed explanations.",
        "Interested in practical applications, especially in data science and real-world examples (e.g., in Vietnam).",
        "Wants clear distinctions between related concepts (e.g., Deep Learning vs Traditional Machine Learning vs Classical Statistics).",
        "Interested in specific architectural comparisons (e.g., Transformer vs RNN/LSTM).",
        "Interested in 'Scaling law', 'post-training techniques' (RLHF, DPO, ORPO, PPO), 'emergent abilities', 'Chain-of-Thought prompting', and 'multimodal learning'."
      ],
      "constraints": [
        "Notes that concepts like Classical Statistics, Traditional ML, and Deep Learning are often confused."
      ]
    },
    "key_facts": [
      "Deep Learning (DL) is a subfield of Machine Learning using multi-layered artificial neural networks to automatically learn hierarchical feature representations from raw data, eliminating manual feature engineering.",
      "Common DL Architectures: CNN, RNN/LSTM/GRU, Transformer, Vision Transformer, Diffusion Models, Graph Neural Networks, Neural ODE, Neural Fields, Mamba.",
      "DL Applications: Computer Vision, Natural Language Processing, Speech Recognition & Synthesis, Recommendation Systems, Time Series Forecasting, Generative AI, Fraud Detection, Biomedicine, Robotics, Materials Science.",
      "Comparison of Classical Statistics, Traditional ML, and Deep Learning across dimensions like Main Goal, Parameters, Feature Engineering, Data Type, Generalization, Large Data Handling, Computational Complexity, and Interpretability.",
      "Classical Statistics focuses on causal relationships and interpretability with few parameters and structured data. Traditional ML focuses on predictive performance with more parameters and structured/some unstructured data. Deep Learning focuses on optimal prediction on complex, large-scale, multimodal data with millions-trillions of parameters and minimal feature engineering.",
      "The current trend (2025-2026) is to combine Classical Statistics, Traditional ML, and Deep Learning for different stages of a project.",
      "Transformer models overcome RNN/LSTM/GRU limitations (vanishing/exploding gradient, sequential processing, long-range dependencies, fixed-size context) through Self-Attention, parallel processing, Positional Encoding, Feed-Forward layers, Layer Normalization, and Residual connections.",
      "Transformer's ability to scale well with parameters and data led to the discovery of 'scaling law'.",
      "Scaling Law (2020-2025) states that increasing parameters (N), training data (D), and computation (C) exponentially improves model performance along a power-law curve.",
      "Scaling Law's importance: predictable performance, cost-effective improvement (data + compute), explains large investments, and leads to 'emergent abilities'.",
      "Post-training techniques (2025-2026) are crucial for aligning pre-trained LLMs with human values (useful, safe, non-toxic), often involving Supervised Fine-Tuning (SFT) followed by Reinforcement Learning (RL) based alignment.",
      "RLHF (Reinforcement Learning from Human Feedback) uses human preference data to train a Reward Model (RM), then PPO optimizes the policy to maximize RM reward. It offers strong alignment but is expensive and slow.",
      "PPO (Proximal Policy Optimization) is an RL algorithm used in RLHF, known for stability but still compute-intensive.",
      "DPO (Direct Preference Optimization) directly optimizes policy from preference data (chosen vs rejected pairs) without an explicit RM, offering simplicity, stability, and compute efficiency.",
      "ORPO (Odds Ratio Preference Optimization) combines SFT with preference optimization in a single loss, improving alignment and reducing hallucination.",
      "KTO (Kahneman-Tversky Optimization) uses binary desirable/undesirable labels, making data collection easier.",
      "Newer post-training techniques include SPIN, RLAIF, Constitutional AI, Self-Reward, and Rejection Sampling.",
      "Emergent Abilities are new capabilities that appear suddenly when a model reaches a certain scale (parameters, data, compute), rather than improving gradually (e.g., few-shot learning, Chain-of-Thought reasoning, instruction following).",
      "Emergent abilities are linked to the threshold effect from scaling law, grokked behaviors, compositionality of skills, and diversity in data.",
      "Chain-of-Thought (CoT) Prompting is a technique to improve LLM reasoning by eliciting intermediate reasoning steps (e.g., by adding 'Let's think step by step').",
      "CoT prompting significantly boosts performance in large models on complex reasoning tasks, suggesting it elicits latent 'internal reasoning' from pre-training.",
      "Multimodal Learning involves models processing and integrating multiple data types (text, image, video, audio, sensor data) within a single framework.",
      "Key components of multimodal learning include separate encoders for each modality, fusion mechanisms (early, late, cross-modal attention), and multimodal pre-training objectives (contrastive, generative, masked modeling).",
      "Popular Multimodal Models (2025-2026): CLIP, DALL·E, Stable Diffusion, Flamingo, BLIP/BLIP-2, Kosmos, GPT-4V/GPT-4o, Gemini, Claude 3, LLaVA/MiniGPT-4, VideoPoet, Sora, AudioGPT, MusicGen, PaLM-E.",
      "Applications of these technologies in Vietnam (2025-2026) include medical AI (VinBigData/VinAI), chatbots/voicebots (FPT AI, Zalo AI), speech recognition/synthesis (Viettel AI, VNG/Vbee), e-commerce recommendations, fintech fraud detection, smart cities (VinAI), and education (FPT)."
    ],
    "decisions": [
      "User decided to first understand the difference between Deep Learning, Traditional Machine Learning, and Classical Statistics.",
      "User decided to then understand why Transformer is stronger than RNN/LSTM.",
      "User decided to then understand Scaling Law.",
      "User decided to then understand post-training techniques (RLHF, DPO, ORPO, PPO).",
      "User decided to then understand emergent abilities.",
      "User decided to then understand Chain-of-Thought prompting.",
      "User decided to then understand multimodal learning."
    ],
    "open_questions": [
      "Bạn muốn đi sâu vào cách implement một VLM đơn giản với HuggingFace, hay thảo luận về AI alignment trong multimodal?"
    ],
    "todos": []
  },
  "message_range_summarized": {
    "from": 0,
    "to": 15
  }
}

```

**Flow 2 - Ambiguous Query**

Input:

```
Tôi dawng awn com
```

Output: 

```
==============================
❓ FLOW 2 — AMBIGUOUS QUERY DEMO
==============================
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
User query: Tôi dawng awn com

🧠 Analysis:
{
  "original_query": "Tôi dawng awn com",
  "is_ambiguous": true,
  "rewritten_query": "Tôi đang ăn cơm",
  "needed_context_from_memory": [
    "recent_topic",
    "open_questions",
    "conversation_state",
    "user_preferences"
  ],
  "clarifying_questions": [
    "Bạn có phải đang muốn nói 'Tôi đang ăn cơm' không?",
    "Bạn có muốn tiếp tục thảo luận về các chủ đề AI trước đó không, hay bạn đang muốn chuyển sang một chủ đề khác?"
  ],
  "final_augmented_context": "The user query contains heavy typos, likely meaning 'Tôi đang ăn cơm' (I am eating). This personal statement, combined with the lack of relation to the `recent_topic` (multimodal learning) and `open_questions` (VLM implementation vs. AI alignment), suggests the user might be making a personal comment or signaling a pause in the conversation, rather than asking a technical question related to the `conversation_state` or `user_preferences`."
}

💬 Assistant response:
Bạn có phải đang muốn nói 'Tôi đang ăn cơm' không?
```

## 7. Test Real Time trên Chat Assistant

```
python main.py
```
