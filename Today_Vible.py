import streamlit as st
import sqlite3
import random
import datetime
import urllib.parse

# DB 연결 함수
def get_connection():
    return sqlite3.connect("bible_kor.db", check_same_thread=False)

# 구절 검색 함수 정의 (위치를 코드 상단으로 이동)
def search_verses(keyword):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT book, chapter, verse, text FROM bible WHERE text LIKE ?", (f'%{keyword}%',))
    search_results = cur.fetchall()
    conn.close()  # 명시적으로 연결을 닫습니다.
    return search_results

# 랜덤 구절 하루 1회 고정
def get_daily_verse():
    if 'daily_verse' in st.session_state and st.session_state['last_shown'] == datetime.date.today():
        return st.session_state['daily_verse']
    verse = get_random_verse()
    st.session_state['daily_verse'] = verse
    st.session_state['last_shown'] = datetime.date.today()
    return verse

# 랜덤 구절 가져오기
def get_random_verse():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bible")
    total = cur.fetchone()[0]
    random_index = random.randint(0, total - 1)
    cur.execute("SELECT book, chapter, verse, text FROM bible LIMIT 1 OFFSET ?", (random_index,))
    result = cur.fetchone()
    conn.close()  # 명시적으로 연결을 닫습니다.
    return result

# 책 목록 가져오기
def get_books():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT book FROM bible")
    books = sorted([row[0] for row in cur.fetchall()])
    conn.close()  # 명시적으로 연결을 닫습니다.
    return books

# 장 목록 가져오기
def get_chapters(book):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT chapter FROM bible WHERE book = ?", (book,))
    chapters = sorted([row[0] for row in cur.fetchall()])
    conn.close()  # 명시적으로 연결을 닫습니다.
    return chapters

# 구절 가져오기
def get_verses(book, chapter):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT verse, text FROM bible WHERE book = ? AND chapter = ? ORDER BY verse", (book, chapter))
    verses = cur.fetchall()
    conn.close()  # 명시적으로 연결을 닫습니다.
    return verses

# 즐겨찾기 추가 (중복 방지)
def add_to_favorites(book, chapter, verse, text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS favorites (id INTEGER PRIMARY KEY, book TEXT, chapter INTEGER, verse INTEGER, text TEXT)")
    cur.execute("SELECT 1 FROM favorites WHERE book = ? AND chapter = ? AND verse = ?", (book, chapter, verse))
    if not cur.fetchone():
        cur.execute("INSERT INTO favorites (book, chapter, verse, text) VALUES (?, ?, ?, ?)", (book, chapter, verse, text))
        conn.commit()
    conn.close()  # 명시적으로 연결을 닫습니다.

# 즐겨찾기 조회
def get_favorites():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, book, chapter, verse, text FROM favorites")
    favorites = cur.fetchall()
    conn.close()  # 명시적으로 연결을 닫습니다.
    return favorites

# 즐겨찾기 삭제
def delete_favorite(favorite_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM favorites WHERE id = ?", (favorite_id,))
    conn.commit()
    conn.close()  # 명시적으로 연결을 닫습니다.

# 구절 날짜별 기록 저장
def record_daily_verse(book, chapter, verse, text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS daily_verse_records (id INTEGER PRIMARY KEY, date TEXT, book TEXT, chapter INTEGER, verse INTEGER, text TEXT)")
    today = datetime.date.today().isoformat()
    cur.execute("INSERT INTO daily_verse_records (date, book, chapter, verse, text) VALUES (?, ?, ?, ?, ?)", 
                (today, book, chapter, verse, text))
    conn.commit()
    conn.close()  # 명시적으로 연결을 닫습니다.

# 사용자 맞춤형 구절 추천 (즐겨찾기 기반)
def recommend_similar_verses(favorite_text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT book, chapter, verse, text FROM bible WHERE text LIKE ?", (f'%{favorite_text}%',))
    recommended_verses = cur.fetchall()
    conn.close()  # 명시적으로 연결을 닫습니다.
    return recommended_verses

# 구절 공유 링크 생성
def create_shareable_link(book, chapter, verse):
    base_url = "https://bible.com"
    verse_url = f"{base_url}/{book}/{chapter}/{verse}"
    return urllib.parse.quote(verse_url)

# ─────────────────────────────────────────────
# Streamlit UI 설정
st.set_page_config(page_title="성경 말씀 뷰어", layout="wide")
st.title("📖 오늘의 말씀 & 성경 뷰어")

# 언어 선택 기능 추가
language = st.selectbox("성경 언어 선택", ["한국어", "English"])

# 탭 구성
탭1, 탭2, 탭3, 탭4, 탭5 = st.tabs(["🌟 오늘의 말씀", "🔍 성경 보기", "💖 즐겨찾기", "🔎 구절 검색", "📤 구절 공유"])

# ─────────────────────────────────────────────
# 오늘의 말씀
with 탭1:
    book, chapter, verse, text = get_daily_verse()
    st.subheader(f"📜 {book} {chapter}:{verse}")
    st.write(text)
    record_daily_verse(book, chapter, verse, text)  # 날짜별 기록 저장
    if st.button("이 구절을 즐겨찾기에 추가하기"):
        add_to_favorites(book, chapter, verse, text)
        st.success("즐겨찾기에 추가되었습니다.")

# ─────────────────────────────────────────────
# 성경 보기
with 탭2:
    books = get_books()
    selected_book = st.selectbox("책을 선택하세요:", books)
    chapters = get_chapters(selected_book)
    selected_chapter = st.selectbox("장을 선택하세요:", chapters)

    verses = get_verses(selected_book, selected_chapter)
    for verse_num, verse_text in verses:
        st.markdown(f"**{verse_num}**. {verse_text}")

# ─────────────────────────────────────────────
# 즐겨찾기
with 탭3:
    st.subheader("💖 즐겨찾기 목록")
    favorites = get_favorites()
    if favorites:
        selected_favorites = []
        for favorite in favorites:
            favorite_id, book, chapter, verse, text = favorite
            checkbox = st.checkbox(f"{book} {chapter}:{verse} - {text}", key=favorite_id)
            if checkbox:
                selected_favorites.append(favorite_id)

        if st.button("선택된 구절 삭제"):
            for favorite_id in selected_favorites:
                delete_favorite(favorite_id)
            st.success("선택된 구절이 삭제되었습니다.")
    else:
        st.info("아직 즐겨찾기가 없습니다.")

# ─────────────────────────────────────────────
# 구절 검색
with 탭4:
    st.subheader("🔎 성경 구절 키워드 검색")
    keyword = st.text_input("검색할 단어를 입력하세요 (예: 예수, 사랑, 평안...)")
    if keyword:
        results = search_verses(keyword)
        st.write(f"🔍 총 {len(results)}개의 결과가 있습니다.")
        for book, chapter, verse, text in results:
            st.markdown(f"📘 **{book} {chapter}:{verse}** — {text}")

# ─────────────────────────────────────────────
# 구절 공유
with 탭5:
    st.subheader("📤 구절 공유하기")
    book, chapter, verse, text = get_daily_verse()
    share_link = create_shareable_link(book, chapter, verse)
    st.markdown(f"**구절 공유 링크**: [링크 복사하기](https://bible.com/{book}/{chapter}/{verse})")
