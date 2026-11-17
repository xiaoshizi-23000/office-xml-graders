import os,sys
import win32com.client as wc
import pymupdf
BASE=os.path.abspath('.')
i=sys.argv[1]
src=os.path.join(BASE,'Excel 2010 操作题题库',i,'1结果.xlsx')
dst=os.path.join(BASE,'student_exam_app','materials','excel','samples',i)
os.makedirs(dst,exist_ok=True)
import glob
for _f in glob.glob(os.path.join(dst,'page_*.png')):
    os.remove(_f)
pdf=os.path.join(BASE,'student_exam_app','_kb_extract','ex_%s.pdf'%i)
if os.path.exists(pdf): os.remove(pdf)
app=wc.DispatchEx('Excel.Application')
app.Visible=False
app.DisplayAlerts=False
wb=app.Workbooks.Open(src,ReadOnly=True,UpdateLinks=0)
cnt=0
for ws in wb.Worksheets:
    try:
        ps=ws.PageSetup
        ps.PrintHeadings=True
        ps.PrintGridlines=True
        ps.Zoom=False
        ps.FitToPagesWide=1
        ps.FitToPagesTall=1
        ps.LeftMargin=18; ps.RightMargin=18; ps.TopMargin=22; ps.BottomMargin=22
        ps.CenterHorizontally=True
        w=ws.UsedRange.Width; h=ws.UsedRange.Height
        ps.Orientation=2 if w>h else 1
        cnt+=1
    except Exception as e:
        print('  skip',ws.Name,str(e)[:60])
wb.ExportAsFixedFormat(0,pdf)
wb.Close(False)
app.Quit()
d=pymupdf.open(pdf)
for j,page in enumerate(d): page.get_pixmap(dpi=130).save(os.path.join(dst,'page_%d.png'%(j+1)))
print('excel',i,'工作表',cnt,'页',len(d))
