import io


async def list_to_text(list: list):
    ss = io.StringIO()
    for i in list:
        ss.write(i)
    txt = ss.getvalue()
    return txt
