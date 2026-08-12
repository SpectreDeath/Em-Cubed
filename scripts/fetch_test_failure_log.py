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


# Run 31045199826 (commit 05f39b8)
url = 'https://api.github.com/repos/SpectreDeath/Em-Cubed/actions/runs/31045199826/jobs'

req = urllib.request.Request(url, headers={
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Python-Agent'
})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        for j in data['jobs']:
            if j['name'].startswith('Test'):
                print(f"Job: {j['name']} | ID: {j['id']}")
                log_url = f"https://api.github.com/repos/SpectreDeath/Em-Cubed/actions/jobs/{j['id']}/logs"
                lreq = urllib.request.Request(log_url, headers={
                    'Authorization': f'token {token}',
                    'User-Agent': 'Python-Agent'
                })
                try:
                    with urllib.request.urlopen(lreq) as lresp:
                        content = lresp.read().decode('utf-8', errors='replace')
                        lines = content.splitlines()
                        print(f"   Total log lines: {len(lines)}")
                        # Print last 60 lines containing test failure summary
                        for line in lines[-60:]:
                            print("   ", line)
                except Exception as le:
                    print("   Log fetch failed:", le)
except Exception as e:
    print('Error:', e)
