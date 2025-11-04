import streamlit as st
import hashlib
import struct

# ----------------------------
# Custom TinyHash32 Function
# ----------------------------
def rotl32(x, r):
    return ((x << r) & 0xFFFFFFFF) | (x >> (32 - r))

def tiny_hash32(s: str) -> str:
    b = s.encode('utf-8')
    n = len(b)
    state = [0x243F6A88 ^ n, 0x85A308D3, 0x13198A2E, 0x03707344 ^ (n << 3 & 0xFFFFFFFF)]
    i = 0
    while i + 8 <= n:
        chunk = b[i:i+8]
        w1, w2 = struct.unpack('<II', chunk)
        state[0] = (state[0] + w1) & 0xFFFFFFFF
        state[1] = (state[1] ^ w2) & 0xFFFFFFFF
        state[2] = (state[2] + rotl32(w1 ^ state[1], 5)) & 0xFFFFFFFF
        state[3] = (state[3] ^ rotl32(w2 + state[0], 11)) & 0xFFFFFFFF
        state[0] = (rotl32(state[0] ^ state[3], 7) * 0x9E3779B1) & 0xFFFFFFFF
        state[1] = (rotl32(state[1] + state[0], 13) * 0x85EBCA6B) & 0xFFFFFFFF
        state[2] = (rotl32(state[2] ^ state[1], 17) * 0xC2B2AE35) & 0xFFFFFFFF
        state[3] = (rotl32(state[3] + state[2], 19) * 0x27D4EB2F) & 0xFFFFFFFF
        i += 8
    tail = b[i:]
    if tail:
        tail_padded = tail + bytes(8 - len(tail))
        w1, w2 = struct.unpack('<II', tail_padded)
        state[0] = (state[0] + (w1 ^ (n << 3))) & 0xFFFFFFFF
        state[1] = (state[1] ^ (w2 + n)) & 0xFFFFFFFF
        state[2] = (state[2] + rotl32(w1, 3)) & 0xFFFFFFFF
        state[3] = (state[3] ^ rotl32(w2, 7)) & 0xFFFFFFFF
    for r in range(6):
        state[0] = (rotl32(state[0] + state[1], (r*3 + 5) % 32) ^ ((state[2] << (r+1)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        state[1] = (rotl32(state[1] + state[2], (r*7 + 3) % 32) ^ ((state[3] >> (r+2)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        state[2] = (rotl32(state[2] + state[3], (r*11 + 9) % 32) ^ ((state[0] << (r+2)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        state[3] = (rotl32(state[3] + state[0], (r*5 + 13) % 32) ^ ((state[1] >> (r+1)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        state[0] = (state[0] * 0xDEADBEEF) & 0xFFFFFFFF
        state[1] = (state[1] * 0xBEEFDEAD) & 0xFFFFFFFF
    out = b''.join(struct.pack('<I', w) for w in state)
    return out.hex()

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def hex_hamming_distance(h1: str, h2: str) -> int:
    b1 = bytes.fromhex(h1)
    b2 = bytes.fromhex(h2)
    return sum(bin(x ^ y).count('1') for x, y in zip(b1, b2))

# ----------------------------
# Streamlit UI Setup
# ----------------------------
st.set_page_config(
    page_title="TinyHash32 - Custom Hash Function",
    
    layout="centered"
)

# Apply pastel background style
st.markdown(
    """
    <style>
    body {
        background-color: #fdf6f0;
    }
    .stApp {
        background-color: #f8ede3;
        color: #2b2d42;
        font-family: 'Poppins', sans-serif;
    }
    div.block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        border-radius: 20px;
        background-color: #f9f7f7;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.05);
    }
    .stTextInput>div>div>input {
        background-color: #e8f0f2;
        color: #2b2d42;
    }
    .stButton>button {
        background-color: #b5e48c;
        color: #1d3557;
        font-weight: bold;
        border-radius: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffd6a5;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# App Content
# ----------------------------
st.title("TinyHash32: Custom Hash Function")


st.write("### Enter text below to generate hash values and compare with SHA-256:")
user_input = st.text_area("Input text:", placeholder="Type something here...")

if st.button("Generate Hashes"):
    tiny = tiny_hash32(user_input)
    sha = sha256_hex(user_input)
    diff = hex_hamming_distance(tiny, sha[:len(tiny)])  # compare equal length
    
    st.success("✅ Hashes generated successfully!")
    st.markdown(f"**Custom TinyHash32 (32 hex chars):** `{tiny}`")
    st.markdown(f"**SHA-256 (64 hex chars):** `{sha}`")
    
    st.write(f"🔁 **Bit-level difference (Hamming distance between first 16 bytes):** `{diff}` bits")
    
    

st.markdown("---")

