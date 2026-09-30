import os,json
from pathlib import Path
from datetime import date
import requests,pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
KEY=os.environ.get("DART"+"_"+"API"+"_"+"KEY","")
if not KEY: raise SystemExit("DART API key is not configured")
U="https://opendart.fss.or.kr/api"
OUT=ROOT/"data/processed";OUT.mkdir(parents=True,exist_ok=True)

def get(api,params):
 p=dict(params);p["crtfc_key"]=KEY
 r=requests.get(U+"/"+api+".json",params=p,timeout=90);r.raise_for_status();d=r.json()
 if d.get("status") not in ("000","013"): raise RuntimeError(d.get("message","DART error"))
 return d.get("list",[])

aliases={"매출액":"revenue","수익(매출액)":"revenue","영업이익":"operating_income","영업이익(손실)":"operating_income","당기순이익":"net_income","당기순이익(손실)":"net_income","자산총계":"total_assets","부채총계":"total_liabilities","자본총계":"total_equity","유동자산":"current_assets","유동부채":"current_liabilities","현금및현금성자산":"cash","매출채권":"receivables","재고자산":"inventory","영업활동으로 인한 현금흐름":"cfo"}
rows=[];reports=[]
for y in range(C["start_year"],date.today().year+1):
 for typ,rc in [("annual","11011"),("half_year","11012"),("quarterly","11013"),("quarterly","11014")]:
  try:
   xs=get("fnlttSinglAcntAll",{"corp_code":C["corp_code"],"bsns_year":str(y),"reprt_code":rc,"fs_div":"CFS"})
  except Exception as e:
   print(y,typ,e);continue
  mon={"11011":"12","11012":"06","11013":"03","11014":"09"}[rc]
  for x in xs:
   try:v=float(str(x.get("thstrm_amount","")).replace(",",""))
   except:continue
   rows.append({"period":str(y)+"-"+mon,"report_type":typ,"fs_div":x.get("fs_div"),"account_nm":x.get("account_nm"),"amount":v,"unit":"million KRW"})
  reports.append({"bsns_year":y,"report_type":typ,"source":"OpenDART structured financial API"})
df=pd.DataFrame(rows)
if df.empty:df=pd.DataFrame(columns=["period","report_type","fs_div","account_nm","amount","unit"])
df["metric"]=df["account_nm"].map(aliases)
df=df.dropna(subset=["metric"])
df.to_csv(OUT/"financials.csv",index=False,encoding="utf-8-sig")
pd.DataFrame(reports).drop_duplicates().to_csv(OUT/"reports.csv",index=False,encoding="utf-8-sig")
p=df.pivot_table(index=["period","report_type"],columns="metric",values="amount",aggfunc="first").reset_index()
def div(a,b):return a/b if pd.notna(a) and pd.notna(b) and b!=0 else None
rr=[]
for _,r in p.iterrows():
 for k,v in {"operating_margin":div(r.get("operating_income"),r.get("revenue")),"net_margin":div(r.get("net_income"),r.get("revenue")),"current_ratio":div(r.get("current_assets"),r.get("current_liabilities")),"debt_ratio":div(r.get("total_liabilities"),r.get("total_equity")),"equity_ratio":div(r.get("total_equity"),r.get("total_assets")),"cfo_to_net_income":div(r.get("cfo"),r.get("net_income"))}.items():
  rr.append({"period":r["period"],"report_type":r["report_type"],"ratio":k,"value":v})
pd.DataFrame(rr).to_csv(OUT/"ratios.csv",index=False,encoding="utf-8-sig")
(OUT/"status.json").write_text(json.dumps({"last_run":date.today().isoformat(),"records":len(df),"reports":len(reports)},ensure_ascii=False),encoding="utf-8")
