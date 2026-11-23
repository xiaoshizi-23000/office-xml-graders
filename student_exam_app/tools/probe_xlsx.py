import sys,os,re
sys.path.insert(0,'graders')
from _core import ExcelBook
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
b=ExcelBook(os.path.abspath(sys.argv[1]))
print('工作表:',b.sheet_names)
for n in b.names:
    if n.startswith('xl/tables/') and n.endswith('.xml'):
        x=b.read(n)
        nm=re.search(r'<table[^>]*name="([^"]*)"',x)
        st=re.search(r'tableStyleInfo[^>]*name="([^"]*)"',x)
        rf=re.search(r'<table[^>]*ref="([^"]*)"',x)
        print('  表:',nm.group(1) if nm else '?','样式:',st.group(1) if st else '?','范围:',rf.group(1) if rf else '?')
print('图表文件:',[n for n in b.names if re.match(r'xl/charts/chart\d+\.xml$',n)])
print('透视表:',[n for n in b.names if re.match(r'xl/pivotTables/pivotTable\d+\.xml$',n)])
for n in b.names:
    if re.match(r'xl/charts/chart\d+\.xml$',n):
        x=b.read(n)
        typ=[k for k in ('barChart','pieChart','lineChart','scatterChart','radarChart','areaChart','doughnutChart','bubbleChart') if '<c:'+k in x]
        ttl=re.findall(r'<a:t>([^<]*)</a:t>',x)[:3]
        sty=re.search(r'<c:style val="(\d+)"',x)
        print('  图表',n,'类型',typ,'标题',ttl,'style',sty.group(1) if sty else '-')
for n in b.names:
    if re.match(r'xl/pivotTables/pivotTable\d+\.xml$',n):
        x=b.read(n)
        loc=re.search(r'<location[^>]*ref="([A-Z]+\d+)',x)
        rows=len(re.findall(r'axis="axisRow"',x));cols=len(re.findall(r'axis="axisCol"',x))
        df=re.findall(r'<dataField name="([^"]*)"',x)
        print('  透视表',n,'位置',loc.group(1) if loc else '?','行%d列%d'%(rows,cols),'值',df)
print('条件格式:')
for ws in b.sheets:
    for cf in ws.root.iter('{%s}conditionalFormatting'%S):
        for r in cf:
            print('  [%s]'%ws.name,cf.get('sqref'),r.get('type'),r.get('operator') or '',r.get('text') or '')
