import zipfile,re
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/"data/raw";OUT=ROOT/"data/processed"
labels={"매출액":"revenue","영업이익":"operating_income","당기순이익":"net_income","자산총계":"total_assets","부채총계":"total_liabilities","자본총계":"total_equity","유동자산":"current_assets","유동부채":"current_liabilities","현금및현금성자산":"cash","매출채권":"receivables","재고자산":"inventory","영업활동으로 인한 현금흐름":"cfo"}
rows=[]
for f in RAW.glob("201*.zip"):
 try:
  parts=f.stem.split("_");y=int(parts[0]);typ=parts[1]
  with zipfile.ZipFile(f) as z:
   for n in z.namelist():
    if not n.lower().endswith((".xml",".html",".htm")): continue
    text=BeautifulSoup(z.read(n),"lxml-xml").get_text(" ",strip=True)
    for lab,metric in labels.items():
     p=text.find(lab)
     if p<0: continue
     m=re.search(r"[-()]?\d[\d,]*(?:\.\d+)?",text[p:p+800])
     if m:
      try: v=float(m.group(0).replace(",","").strip("()"))
      except: continue
      rows.append({"period":str(y)+"-12","report_type":typ,"fs_div":"legacy","account_nm":lab,"metric":metric,"amount":v,"unit":"reported"})
 except Exception as e: print("skip",f,e)
if rows:
 old=pd.read_csv(OUT/"financials.csv") if (OUT/"financials.csv").exists() else pd.DataFrame()
 new=pd.DataFrame(rows)
 if not old.empty: old=old[~old["fs_div"].fillna("").eq("legacy")]
 pd.concat([old,new],ignore_index=True).drop_duplicates(["period","report_type","account_nm"]).to_csv(OUT/"financials.csv",index=False,encoding="utf-8-sig")
 print("legacy extracted",len(new))
