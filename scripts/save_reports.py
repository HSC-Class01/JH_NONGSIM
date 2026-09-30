import os,json,requests,pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];C=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
KEY=os.environ.get("DART"+"_"+"API"+"_"+"KEY","");API="https://opendart.fss.or.kr/api";RAW=ROOT/"data/raw";OUT=ROOT/"data/processed";RAW.mkdir(parents=True,exist_ok=True)
if not KEY: raise SystemExit("DART API key is not configured")
def call(n,p):
 p=dict(p);p["crtfc_key"]=KEY;r=requests.get(API+"/"+n+".json",params=p,timeout=90);r.raise_for_status();return r.json()
rows=[]
for y in range(C["start_year"],__import__("datetime").date.today().year+1):
 for typ,rc in [("annual","11011"),("half_year","11012"),("quarterly","11013"),("quarterly","11014")]:
  if rc=="11011":b,e=str(y)+"0101",str(y+1)+"0430"
  elif rc=="11013":b,e=str(y)+"0401",str(y)+"0630"
  elif rc=="11012":b,e=str(y)+"0701",str(y)+"0930"
  else:b,e=str(y)+"1001",str(y+1)+"0331"
  xs=call("list",{"corp_code":C["corp_code"],"bgn_de":b,"end_de":e,"pblntf_ty":"A","last_reprt_at":"Y","sort":"date","sort_mth":"asc","page_no":"1","page_count":"100"}).get("list",[])
  target="사업보고서" if rc=="11011" else ("반기보고서" if rc=="11012" else "분기보고서");xs=[x for x in xs if target in x.get("report_nm","")]
  if not xs:continue
  x=xs[-1];rno=x["rcept_no"];f=RAW/(str(y)+"_"+typ+"_"+rno+".zip")
  if not f.exists():
   r=requests.get(API+"/document.xml",params={"crtfc_key":KEY,"rcept_no":rno},timeout=120);r.raise_for_status();f.write_bytes(r.content)
  rows.append({"bsns_year":y,"report_type":typ,"report_name":x.get("report_nm"),"rcept_no":rno,"receipt_date":x.get("rcept_dt"),"source_url":"https://dart.fss.or.kr/dsaf001/main.do?rcpNo="+rno})
pd.DataFrame(rows).drop_duplicates().to_csv(OUT/"reports.csv",index=False,encoding="utf-8-sig")
print("saved reports",len(rows))
