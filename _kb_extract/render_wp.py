import os,sys
import win32com.client as wc
import pymupdf
BASE=os.path.abspath('.')
subj=sys.argv[1]; i=sys.argv[2]
if subj=='word':
    src=os.path.join(BASE,'Word 2010 操作题题库',i,'1结果.docx')
else:
    src=os.path.join(BASE,'PPT 2010 操作题题库',i,'1结果.pptx')
dst=os.path.join(BASE,'student_exam_app','materials',subj,'samples',i)
os.makedirs(dst,exist_ok=True)
pdf=os.path.join(BASE,'student_exam_app','_kb_extract','%s_%s.pdf'%(subj,i))
if os.path.exists(pdf): os.remove(pdf)
if subj=='word':
    app=wc.DispatchEx('Word.Application');app.Visible=False;app.DisplayAlerts=0
    doc=app.Documents.Open(src,ReadOnly=True)
    doc.SaveAs(pdf,FileFormat=17)
    doc.Close(False);app.Quit()
else:
    app=wc.DispatchEx('PowerPoint.Application');app.DisplayAlerts=0
    prs=app.Presentations.Open(src,ReadOnly=True,WithWindow=False)
    prs.SaveAs(pdf,32);prs.Close();app.Quit()
d=pymupdf.open(pdf)
for j,page in enumerate(d):
    page.get_pixmap(dpi=140).save(os.path.join(dst,'page_%d.png'%(j+1)))
print(subj,i,len(d),'页')
