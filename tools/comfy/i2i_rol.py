"""Figuur in een andere rol (22 nov 2026, Market Doodle): bestaande pose + prompt via Z-Image img2img, zodat gezicht en stijl blijven.
  python i2i_rol.py jobs.json   (lijst van {src, prompt, out, denoise}); kleding: denoise ~0.72; spullen eerst grof erop tekenen, dan ~0.45."""
import json, os, sys, time, urllib.parse, urllib.request, uuid
from PIL import Image
SERVER="http://127.0.0.1:8188"
def api(p,data=None,h=None):
    with urllib.request.urlopen(urllib.request.Request(SERVER+p,data=data,headers=h or {})) as r: return r.read()
def upload(img):
    b=uuid.uuid4().hex
    body=(f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{os.path.basename(img)}\"\r\nContent-Type: image/png\r\n\r\n").encode()+open(img,"rb").read()+f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
    return json.loads(api("/upload/image",body,{"Content-Type":f"multipart/form-data; boundary={b}"}))["name"]
def run(src, prompt, neg, out, denoise, seed, W=768, H=1024):
    im=Image.open(src).convert("RGB"); c=Image.new("RGB",(W,H),"white"); r=min((W-40)/im.width,(H-40)/im.height); im=im.resize((int(im.width*r),int(im.height*r)),Image.LANCZOS); c.paste(im,((W-im.width)//2,(H-im.height)//2))
    tmp=out+".in.png"; c.save(tmp); name=upload(tmp)
    wf=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zimage_api.json")))
    wf["4"]["inputs"]["text"]=prompt
    wf["11"]={"class_type":"LoadImage","inputs":{"image":name}}
    wf["13"]={"class_type":"VAEEncode","inputs":{"pixels":["11",0],"vae":["3",0]}}
    k=wf["8"]["inputs"]; k["latent_image"]=["13",0]; k["denoise"]=denoise; k["seed"]=seed
    wf["10"]["inputs"]["filename_prefix"]="alteraqon/i2i"
    del wf["6"]
    pid=json.loads(api("/prompt",json.dumps({"prompt":wf}).encode(),{"Content-Type":"application/json"}))["prompt_id"]
    while True:
        h=json.loads(api(f"/history/{pid}")).get(pid)
        if h and h.get("status",{}).get("completed"):
            for node in h["outputs"].values():
                for f in node.get("images",[]):
                    q=urllib.parse.urlencode({"filename":f["filename"],"subfolder":f.get("subfolder",""),"type":f.get("type","output")})
                    open(out,"wb").write(api(f"/view?{q}")); os.remove(tmp); return
        if h and h.get("status",{}).get("status_str")=="error": print("FOUT", h["status"]); return
        time.sleep(2)
if __name__=="__main__":
    jobs=json.load(open(sys.argv[1],encoding="utf-8"))
    for j in jobs:
        run(j["src"],j["prompt"],"",j["out"],j["denoise"],j.get("seed",7)); print("klaar",j["out"],flush=True)
