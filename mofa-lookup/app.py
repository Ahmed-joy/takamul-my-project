import re
from flask import Flask, request, render_template_string
from playwright.sync_api import sync_playwright
app=Flask(__name__)
URL='https://visa.mofa.gov.sa/VISAPERSON/GETAPPLICANTDATA'
PAGE='''<!doctype html><meta charset="utf-8"><title>Visa Lookup</title><style>body{font:16px Arial;background:#eef2f5;color:#243653;margin:0}header{background:#16483e;color:white;padding:24px}main{max-width:900px;margin:35px auto;background:white;padding:28px;border-radius:12px}input,button{padding:13px;border:1px solid #bbc5ce;border-radius:6px;font:inherit}button{background:#186b56;color:white;cursor:pointer}pre{white-space:pre-wrap;line-height:1.7;background:#f5f5f5;padding:18px}</style><header>Independent Saudi Visa Lookup</header><main><h2>Search application</h2><form method="post"><input name="passport" required pattern="[A-Za-z0-9]{5,20}" placeholder="Passport number"><button>Open official search</button><p>Bangladesh · Work · Dhaka</p><label><input type="checkbox" name="authorized" required> I am authorized to access this applicant's information.</label></form><p>Complete CAPTCHA and submit in the opened browser. No records are saved.</p>{% if error %}<p>{{error}}</p>{% endif %}{% if result %}<h3>Official page text</h3><pre>{{result}}</pre>{% endif %}</main>'''
@app.after_request
def no_cache(response):
    response.headers['Cache-Control']='no-store'
    return response
@app.route('/',methods=['GET','POST'])
def index():
    result=error=None
    if request.method=='POST':
        passport=request.form.get('passport','').strip().upper()
        if not request.form.get('authorized') or not re.fullmatch(r'[A-Z0-9]{5,20}',passport):
            return render_template_string(PAGE,error='Authorization and valid passport required.',result=None)
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=False)
                page=browser.new_page()
                page.goto(URL,wait_until='domcontentloaded',timeout=60000)
                for name,value in [('PassportNumber',passport),('Nationality','BGD'),('VisaType','1'),('Embassy','218')]:
                    try:
                        field=page.locator('[name="'+name+'"]').first
                        if name=='PassportNumber': field.fill(value,timeout=3000)
                        else: field.select_option(value=value,timeout=3000)
                    except Exception: pass
                page.wait_for_url('**/GetPersonVisa*',timeout=300000)
                page.wait_for_load_state('domcontentloaded')
                body=page.locator('body').inner_text()
                if 'entered application' in body.lower() and passport in body.upper(): result=body
                else: error='No matching application result recognized.'
                browser.close()
        except Exception:
            error='Official browser search did not complete. Check connectivity and browser installation.'
    return render_template_string(PAGE,result=result,error=error)
if __name__=='__main__': app.run(host='127.0.0.1',port=8765,debug=False)
