import pymupdf, os

p = r'C:\Users\23000\AppData\Local\Temp\codebuddy-dropped-files\bb005999-43de-476a-b696-272f7d0bc60d\2027年云南省中职职教高考职业技能考试说明（试行）04计算机信息类（原版PDF）.pdf'
d = pymupdf.open(p)
for i, page in enumerate(d):
    imgs = page.get_images(full=True)
    xrefs = [x[0] for x in imgs]
    info = []
    for x in imgs:
        info.append((x[0], x[2], x[3], x[8]))
    print(i + 1, 'imgs', info if info else '-')
print('total images', len(d.get_page_images(0)))
