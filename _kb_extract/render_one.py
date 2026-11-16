import os,sys
import win32com.client as wc
import pymupdf
BASE=os.path.abspath('.')
subj=sys.argv[1]; i=int(sys.argv[2])
src=os.path.join(BASE,'%s 2010 操作题题库'%subj.capitalize() if subj!='ppt' else 'PPT 2010 操作题题库',str(i),
                 '1结果.'+('xlsx' if subj=='excel' else 'pptx'))
dst=os.path.join(BASE,'student_exam_app','materials',subj,'samples',str(i))
os.makedirs(dst,exist_ok=True)
pdf=os.path.join(BASE,'student_exam_app','_kb_extract','%s_%d.pdf'%(subj,i))
if subj=='excel':
    app=wc.Dispatch('Excel.Application');app.Visible=False;app.DisplayAlerts=False
    wb=app.Workbooks.Open(src,ReadOnly=True,UpdateLinks=0)
    wb.ExportAsFixedFormat(0,pdf)
    wb.Close(False);app.Quit()
else:
    app=wc.Dispatch('PowerPoint.Application');app.DisplayAlerts=0
    prs=app.Presentations.Open(src,ReadOnly=True,WithWindow=False)
    prs.SaveAs(pdf,32);prs.Close();app.Quit()
d=pymupdf.open(pdf)
for j,page in enumerate(d):
    page.get_pixmap(dpi=110).save(os.path.join(dst,'page_%d.png'%(j+1)))
print(subj,i,len(d),'页')
