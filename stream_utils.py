import codecs


def decode_utf8_chunks(byte_chunks):
    decoder = codecs.getincrementaldecoder("utf-8")()
    for chunk in byte_chunks:
        if not chunk:
            continue
        text = decoder.decode(chunk)

        if text:
            yield text
    tail = decoder.decode(b"", final=True)
    if tail:
        yield tail
