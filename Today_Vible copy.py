import sqlite3
import random
import streamlit as st

# DB 연결 함수
def get_connection():
    return sqlite3.connect("bible_kor.db")

# 일일 퀴즈 기능
quiz_questions = [
    {"question": "하나님이 세상을 창조하신 순서는 무엇인가요?", "answer": "빛, 하늘, 땅, 식물, 동물, 사람"},
    {"question": "모세는 어디에서 하나님을 만났나요?", "answer": "불타는 떨기나무"},
    {"question": "예수님의 첫 번째 기적은 무엇인가요?", "answer": "물로 포도주 만들기"},
]

# 성경 구절 강조 및 메모 추가 기능
def add_verse_highlight(book, chapter, verse, text, memo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS verse_highlights (id INTEGER PRIMARY KEY, book TEXT, chapter INTEGER, verse INTEGER, text TEXT, memo TEXT)")
    cur.execute("INSERT INTO verse_highlights (book, chapter, verse, text, memo) VALUES (?, ?, ?, ?, ?)", (book, chapter, verse, text, memo))
    conn.commit()
    conn.close()

# 일일 퀴즈 랜덤 선택 및 상태 관리
def get_daily_quiz():
    if 'quiz_index' not in st.session_state:
        st.session_state.quiz_index = 0  # 처음 시작 시 첫 번째 퀴즈
    return quiz_questions[st.session_state.quiz_index]

# 다음 퀴즈로 이동
def next_quiz():
    if st.session_state.quiz_index < len(quiz_questions) - 1:
        st.session_state.quiz_index += 1
    else:
        st.session_state.quiz_index = 0  # 퀴즈가 끝나면 처음으로 돌아가기

# Streamlit 페이지 구성
st.title("📖 오늘의 말씀 & 성경 퀴즈")

# 일일 퀴즈
st.header("📜 성경 퀴즈")
quiz = get_daily_quiz()
st.subheader(f"질문: {quiz['question']}")

# 사용자 답 입력
user_answer = st.text_input("답을 입력하세요:")

# 정답 제출 버튼과 다음 질문으로 이동 버튼을 나란히 배치
col1, col2 = st.columns([1, 1])

with col1:
    # 정답 제출 버튼
    if st.button("정답 제출"):
        # 정답 확인
        if user_answer.strip().lower() == quiz['answer'].lower():
            st.session_state.quiz_feedback = "정답입니다! 🎉"
            st.session_state.is_correct = True  # 정답인 경우
        else:
            st.session_state.quiz_feedback = f"오답입니다. 정답은 '{quiz['answer']}'입니다."
            st.session_state.is_correct = False  # 오답인 경우
        
        # 화면 새로고침
        st.session_state.answer_submitted = True
        st.rerun()  # 화면을 새로고침하여 다음 퀴즈로 이동

with col2:
    # 다음 질문으로 이동 버튼
    if st.button("다음 질문으로 이동"):
        next_quiz()  # 다음 퀴즈로 이동
        st.session_state.answer_submitted = False  # 답변이 제출되지 않은 상태로 리셋
        st.rerun()  # 화면을 새로고침하여 변경 사항 반영

# 답변 피드백 표시
if 'quiz_feedback' in st.session_state and st.session_state.answer_submitted:
    # 정답일 때 초록색으로 표시
    if st.session_state.is_correct:
        st.success(st.session_state.quiz_feedback)
    else:
        st.error(st.session_state.quiz_feedback)  # 오답일 때 빨간색으로 표시

    st.session_state.answer_submitted = False  # 피드백이 한 번만 표시되도록

# 성경 구절 강조 & 메모
st.header("📖 성경 구절 강조 & 메모")
book = "요한복음"
chapter = 3
verse = 16
verse_text = "하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니..."
st.subheader(f"{book} {chapter}:{verse}")
st.write(verse_text)

memo = st.text_area("이 구절에 대한 메모를 추가하세요:")

if st.button("메모 저장"):
    add_verse_highlight(book, chapter, verse, verse_text, memo)
    st.success("메모가 저장되었습니다.")
