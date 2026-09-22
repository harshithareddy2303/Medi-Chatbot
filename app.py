from flask import Flask, render_template, request, jsonify
import json
import re
import sqlite3

app = Flask(__name__)

DATABASE = "chat_history.db"


# ==========================================
# DATABASE
# ==========================================

def init_database():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_chat(user_message, bot_response):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO chat_history
        (user_message, bot_response)
        VALUES (?, ?)
    """, (user_message, bot_response))

    connection.commit()
    connection.close()


# ==========================================
# LOAD KNOWLEDGE BASE
# ==========================================

with open("knowledge_base.json", "r", encoding="utf-8") as file:
    knowledge_base = json.load(file)


# ==========================================
# TEXT CLEANING
# ==========================================

def clean_text(text):
    text = text.lower()

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================
# EMERGENCY CHECK
# ==========================================

def check_emergency(message):

    emergency_keywords = [
        "severe chest pain",
        "chest pain",
        "cannot breathe",
        "difficulty breathing",
        "severe bleeding",
        "unconscious",
        "fainted",
        "seizure",
        "stroke",
        "poisoning"
    ]

    message = clean_text(message)

    for keyword in emergency_keywords:

        if keyword in message:
            return True

    return False


# ==========================================
# FIND MEDICAL TOPIC
# ==========================================

def find_topic(user_message):

    message = clean_text(user_message)

    words = set(message.split())

    best_topic = None
    best_score = 0

    for topic_id, topic in knowledge_base.items():

        score = 0

        # --------------------------------------
        # Check topic name
        # --------------------------------------

        topic_name = clean_text(
            topic["name"]
        )

        if topic_name in message:
            score += 10

        # --------------------------------------
        # Check keywords
        # --------------------------------------

        for keyword in topic["keywords"]:

            keyword = clean_text(keyword)

            # Full keyword / phrase
            if keyword in message:
                score += 8

            # Individual keyword
            keyword_words = keyword.split()

            for word in keyword_words:

                if (
                    word in words
                    and len(word) > 3
                ):
                    score += 3

        # --------------------------------------
        # Check symptoms
        # --------------------------------------

        for symptom in topic["symptoms"]:

            symptom_text = clean_text(
                symptom
            )

            symptom_words = symptom_text.split()

            for word in symptom_words:

                if (
                    word in words
                    and len(word) > 4
                ):
                    score += 1

        # --------------------------------------
        # Select highest score
        # --------------------------------------

        if score > best_score:

            best_score = score
            best_topic = topic_id

    return best_topic


# ==========================================
# GENERATE RESPONSE
# ==========================================

def generate_response(user_message):

    message = clean_text(user_message)

    # --------------------------------------
    # Emergency check
    # --------------------------------------

    if check_emergency(message):

        return (
            "<h3>⚠️ Urgent Medical Attention</h3>"

            "<p>"
            "The symptoms or situation you described "
            "may require urgent medical evaluation."
            "</p>"

            "<p>"
            "<b>"
            "Please contact your local emergency service "
            "or seek urgent medical care."
            "</b>"
            "</p>"

            "<p>"
            "Do not rely on a chatbot for emergency "
            "diagnosis or treatment."
            "</p>"
        )

    # --------------------------------------
    # Greeting
    # --------------------------------------

    if message in [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]:

        return (
            "<h3>Hello! 👋</h3>"

            "<p>"
            "I am <b>MediChatbot</b>, "
            "a medical information assistant."
            "</p>"

            "<p>"
            "I can provide general information about "
            "common health conditions, symptoms, "
            "prevention and general self-care."
            "</p>"

            "<p>"
            "You can ask about conditions such as "
            "<b>"
            "cold, headache, fever, diabetes, "
            "high blood pressure, asthma or stomach pain."
            "</b>"
            "</p>"

            "<small>"
            "This chatbot provides educational information "
            "and does not replace professional medical advice."
            "</small>"
        )

    # --------------------------------------
    # Find topic
    # --------------------------------------

    topic_id = find_topic(user_message)

    # --------------------------------------
    # No matching topic
    # --------------------------------------

    if topic_id is None:

        return (
            "<h3>Sorry, I couldn't find a matching topic.</h3>"

            "<p>"
            "My current knowledge base contains information "
            "about several common health conditions."
            "</p>"

            "<p>"
            "Try asking about:"
            "</p>"

            "<p>"
            "• Common Cold<br>"
            "• Headache<br>"
            "• Fever<br>"
            "• Diabetes<br>"
            "• High Blood Pressure<br>"
            "• Asthma<br>"
            "• Stomach Pain<br>"
            "• Acid Reflux<br>"
            "• Migraine"
            "</p>"

            "<p>"
            "<b>Tip:</b> "
            "Describe your question using simple "
            "health-related words."
            "</p>"

            "<small>"
            "This chatbot provides general educational "
            "information and does not diagnose diseases."
            "</small>"
        )

    # --------------------------------------
    # Get topic information
    # --------------------------------------

    topic = knowledge_base[topic_id]

    # --------------------------------------
    # Format symptoms
    # --------------------------------------

    symptoms = "<br>".join(
        "• " + item
        for item in topic["symptoms"]
    )

    # --------------------------------------
    # Format self-care
    # --------------------------------------

    self_care = "<br>".join(
        "• " + item
        for item in topic["self_care"]
    )

    # --------------------------------------
    # Format prevention
    # --------------------------------------

    prevention = "<br>".join(
        "• " + item
        for item in topic["prevention"]
    )

    # --------------------------------------
    # Create response
    # --------------------------------------

    response = f"""
    <h3>{topic['name']}</h3>

    <b>About:</b>

    <p>
        {topic['description']}
    </p>


    <b>Common Symptoms:</b>

    <p>
        {symptoms}
    </p>


    <b>General Self-Care:</b>

    <p>
        {self_care}
    </p>


    <b>Prevention:</b>

    <p>
        {prevention}
    </p>


    <b>When to Seek Medical Advice:</b>

    <p>
        {topic['medical_help']}
    </p>


    <b>General Recommendation:</b>

    <p>
        Based on this topic, consider the general
        self-care measures listed above and monitor
        your symptoms.

        If symptoms are severe, persistent,
        or getting worse, consult a qualified
        healthcare professional.
    </p>


    <b>Medication Note:</b>

    <p>
        {topic['medicine_note']}
    </p>


    <small>
        This information is for educational purposes only.

        MediChatbot does not diagnose diseases,
        prescribe medicines, or replace professional
        medical diagnosis or treatment.
    </small>
    """

    return response


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================
# CHAT HISTORY
# ==========================================

@app.route(
    "/history",
    methods=["GET"]
)
def history():

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_message,
            bot_response,
            created_at
        FROM chat_history
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    connection.close()

    history_data = []

    for row in rows:

        history_data.append({
            "user_message": row[0],
            "bot_response": row[1],
            "created_at": row[2]
        })

    return jsonify(
        history_data
    )


# ==========================================
# CLEAR CHAT HISTORY
# ==========================================

@app.route(
    "/clear-history",
    methods=["DELETE"]
)
def clear_history():

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM chat_history"
    )

    connection.commit()

    connection.close()

    return jsonify({
        "success": True,
        "message": "Chat history cleared successfully."
    })


# ==========================================
# GET ALL MEDICAL TOPICS
# ==========================================

@app.route(
    "/api/topics",
    methods=["GET"]
)
def get_topics():

    topics = []

    for topic_id, topic in knowledge_base.items():

        topics.append({
            "id": topic_id,
            "name": topic["name"],
            "description": topic["description"]
        })

    return jsonify({
        "success": True,
        "count": len(topics),
        "topics": topics
    })


# ==========================================
# GET ONE MEDICAL TOPIC
# ==========================================

@app.route(
    "/api/topics/<topic_id>",
    methods=["GET"]
)
def get_topic(topic_id):

    if topic_id not in knowledge_base:

        return jsonify({
            "success": False,
            "message": "Medical topic not found."
        }), 404

    topic = knowledge_base[topic_id]

    return jsonify({
        "success": True,

        "topic": {
            "id": topic_id,
            "name": topic["name"],
            "keywords": topic["keywords"],
            "description": topic["description"],
            "symptoms": topic["symptoms"],
            "self_care": topic["self_care"],
            "prevention": topic["prevention"],
            "medical_help": topic["medical_help"],
            "medicine_note": topic["medicine_note"]
        }
    })


# ==========================================
# SEARCH MEDICAL TOPICS
# ==========================================

@app.route(
    "/api/search",
    methods=["GET"]
)
def search_topics():

    query = request.args.get(
        "q",
        ""
    ).strip()

    if not query:

        return jsonify({
            "success": False,
            "message": "Please provide a search term."
        }), 400

    search_text = clean_text(
        query
    )

    search_words = set(
        search_text.split()
    )

    results = []

    for topic_id, topic in knowledge_base.items():

        score = 0

        # --------------------------------------
        # Topic name
        # --------------------------------------

        topic_name = clean_text(
            topic["name"]
        )

        if search_text == topic_name:

            score += 10

        elif search_text in topic_name:

            score += 5

        # --------------------------------------
        # Keywords
        # --------------------------------------

        for keyword in topic["keywords"]:

            keyword_text = clean_text(
                keyword
            )

            if search_text == keyword_text:

                score += 8

            elif search_text in keyword_text:

                score += 5

            keyword_words = keyword_text.split()

            for word in keyword_words:

                if word in search_words:

                    score += 2

        # --------------------------------------
        # Description
        # --------------------------------------

        description = clean_text(
            topic["description"]
        )

        if search_text in description:

            score += 2

        # --------------------------------------
        # Add matching result
        # --------------------------------------

        if score > 0:

            results.append({
                "id": topic_id,
                "name": topic["name"],
                "description": topic["description"],
                "score": score
            })

    # Highest score first
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "results": results
    })


# ==========================================
# CHAT API
# ==========================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json()

    if not data:

        return jsonify({
            "response":
            "Please enter a health-related question."
        })

    user_message = data.get(
        "message",
        ""
    ).strip()

    if not user_message:

        return jsonify({
            "response":
            "Please enter a health-related question."
        })

    response = generate_response(
        user_message
    )

    # Save conversation
    save_chat(
        user_message,
        response
    )

    return jsonify({
        "response": response
    })


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    init_database()

    app.run(
        debug=True
    )