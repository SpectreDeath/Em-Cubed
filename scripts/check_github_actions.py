import os
import urllib.request
import json

def get_gh_token():
    tokens_dir = r"D:\.tokens"
    if os.path.exists(tokens_dir):
        for fname in os.listdir(tokens_dir):
            if fname.endswith(".txt"):
                fpath = os.path.join(tokens_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        for line in f:
                            s = line.strip()
                            if s.startswith("ghp_"):
                                return s
                except Exception:
                    pass
    return os.getenv("GITHUB_TOKEN", os.getenv("GH_TOKEN", ""))



token = get_gh_token()

url = 'https://api.github.com/repos/SpectreDeath/Em-Cubed/actions/runs'

req = urllib.request.Request(url, headers={
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Python-Agent'
})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        runs = data.get('workflow_runs', [])[:10]
        print(f"Total runs fetched: {len(runs)}")
        for r in runs:
            print(f"ID: {r['id']} | Name: {r['name']} | Status: {r['status']} | Conclusion: {r['conclusion']} | SHA: {r['head_sha'][:7]} | Event: {r['event']}")
            
            # Fetch jobs for this run
            jobs_url = r['jobs_url']
            jobs_req = urllib.request.Request(jobs_url, headers={
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Python-Agent'
            })
            with urllib.request.urlopen(jobs_req) as jresp:
                jdata = json.loads(jresp.read().decode())
                for j in jdata.get('jobs', []):
                    print(f"   -> Job: {j['name']} | Status: {j['status']} | Conclusion: {j['conclusion']}")
                    if j['conclusion'] == 'failure':
                        for step in j.get('steps', []):
                            if step.get('conclusion') == 'failure':
                                print(f"      -> Failed Step: {step['name']}")
except Exception as e:
    import traceback
    print('Error:', e)
    traceback.print_exc()
