import os,sys,glob
import win32com.client as wc
import pymupdf
from PIL import Image

BASE=os.path.abspath('.')
APP=os.path.join(BASE,'student_exam_app')
OUT=os.path.join(APP,'materials')
os.makedirs(OUT,exist_ok=True)

def pdf_to_imgs(pdf,outdir,prefix,dpi=110):
    d=pymupdf.open(pdf)
    paths=[]
    for i,page in enumerate(d):
        pix=page.get_pixmap(dpi=dpi)
        p=os.path.join(outdir,'%s_%d.png'%(prefix,i+1))
        pix.save(p)
        paths.append(p)
    d.close()
    return paths

def word_pdf(src,pdf):
    app=wc.Dispatch('Word.Application');app.Visible=False;app.DisplayAlerts=0
    doc=app.Documents.Open(src,ReadOnly=True)
    doc.SaveAs(pdf,FileFormat=17)
    doc.Close(False);app.Quit()

def excel_pdf(src,pdf):
    app=wc.Dispatch('Excel.Application');app.Visible=False;app.DisplayAlerts=False
    wb=app.Workbooks.Open(src,ReadOnly=True)
    try:
        for ws in wb.Worksheets:
            ws.PageSetup.Orientation=2
            ws.PageSetup.Zoom=False
            ws.PageSetup.FitToPagesWide=1
            ws.PageSetup.FitToPagesTall=1
    except Exception as e: print('  pagesetup',str(e)[:60])
    wb.ExportAsFixedFormat(0,pdf)
    wb.Close(False);app.Quit()

def ppt_pdf(src,pdf):
    app=wc.Dispatch('PowerPoint.Application');app.Visible=False;app.DisplayAlerts=0
    prs=app.Presentations.Open(src,ReadOnly=True,WithWindow=False)
    prs.SaveAs(pdf,32)
    prs.Close();app.Quit()

task=sys.argv[1]
if task=='word':
    for i in range(6,11):
        src=os.path.join(BASE,'Word 2010 操作题题库',str(i),'1结果.docx')
        dst=os.path.join(OUT,'word','samples',str(i))
        os.makedirs(dst,exist_ok=True)
        pdf=os.path.join(APP,'_kb_extract','word_%d.pdf'%i)
        word_pdf(src,pdf)
        ps=pdf_to_imgs(pdf,dst,'page')
        print('word',i,'->',len(ps),'页',[os.path.basename(x) for x in ps])
elif task=='excel':
    for i in range(1,11):
        src=os.path.join(BASE,'Excel 2010 操作题题库',str(i),'1结果.xlsx')
        dst=os.path.join(OUT,'excel','samples',str(i))
        os.makedirs(dst,exist_ok=True)
        pdf=os.path.join(APP,'_kb_extract','excel_%d.pdf'%i)
        excel_pdf(src,pdf)
        ps=pdf_to_imgs(pdf,dst,'page')
        print('excel',i,'->',len(ps),'页')
elif task=='ppt':
    for i in range(1,11):
        src=os.path.join(BASE,'PPT 2010 操作题题库',str(i),'1结果.pptx')
        dst=os.path.join(OUT,'ppt','samples',str(i))
        os.makedirs(dst,exist_ok=True)
        pdf=os.path.join(APP,'_kb_extract','ppt_%d.pdf'%i)
        ppt_pdf(src,pdf)
        ps=pdf_to_imgs(pdf,dst,'page')
        print('ppt',i,'->',len(ps),'页')
