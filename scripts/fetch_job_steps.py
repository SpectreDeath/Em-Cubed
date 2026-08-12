import os
import urllib.request
import json

def get_gh_token():
    t = os.getenv("GITHUB_TOKEN", os.getenv("GH_TOKEN", ""))
    if t:
        return t
    tokens_dir = r"D:\.tokens"
    if os.path.exists(tokens_dir):
        for fname in os.listdir(tokens_dir):
            if fname.endswith(".txt"):
                fpath = os.path.join(tokens_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        for line in f:
                            s = line.strip()
                            if s.startswith("ghp_") or s.startswith("github_pat_"):
                                return s
                except Exception:
                    pass
    return ""


token = get_gh_token()

url = 'https://api.github.com/repos/SpectreDeath/Em-Cubed/actions/jobs/92424989602'

req = urllib.request.Request(url, headers={
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Python-Agent'
})

try:
    with urllib.request.urlopen(req) as resp:
        j = json.loads(resp.read().decode())
        print(f"Job: {j['name']} | Status: {j['status']} | Conclusion: {j['conclusion']}")
        for step in j.get('steps', []):
            print(f"Step: {step['name']} | Conclusion: {step.get('conclusion')}")
except Exception as e:
    print('Error:', e)
