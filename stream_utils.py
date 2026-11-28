import codecs


def decode_utf8_chunks(byte_chunks):
    """把按字节切开的网络流，还原成完整的字符串。

    为什么不能每块直接 chunk.decode('utf-8')：
    一个汉字占 3 个字节，网络可能从汉字中间劈开送达。
    增量解码器会把"不完整的半截字"先存起来，等下一批字节到齐再一起吐。
    """
    decoder = codecs.getincrementaldecoder("utf-8")()
    for chunk in byte_chunks:
        if not chunk:
            continue
        text = decoder.decode(chunk)

        if text:
            yield text

    tail = decoder.decode(b"", final=True)   # 把最后剩下的残渣挤出来
    if tail:
        yield tail

