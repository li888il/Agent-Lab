from stream_utils import decode_utf8_chunks


def test_汉字被从中间劈开():
    text = "你好世界，我是自动化专业的学生。"
    raw = text.encode("utf-8")
    chunks = [raw[:2], raw[2:5], raw[5:]]
    assert "".join(decode_utf8_chunks(chunks)) == text


def test_逐字节喂也不乱码():
    text = "流式输出不能乱码"
    chunks = [bytes([b]) for b in text.encode("utf-8")]
    assert "".join(decode_utf8_chunks(chunks)) == text
