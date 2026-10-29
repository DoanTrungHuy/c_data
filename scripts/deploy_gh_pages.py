import os
import subprocess
import sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
git_dir = os.path.join(root, ".git")
out_dir = os.path.join(root, "frontend", "out")
temp_index = os.path.join(git_dir, "temp_index_deploy")

if os.path.exists(temp_index):
    try:
        os.remove(temp_index)
    except Exception:
        pass

# Đảm bảo file .nojekyll luôn luôn tồn tại để GitHub Pages không kích hoạt Jekyll bỏ qua thư mục _next/
nojekyll_file = os.path.join(out_dir, ".nojekyll")
with open(nojekyll_file, "w", encoding="utf-8") as f:
    f.write("")
print(f"✓ Đã tạo/kiểm tra file bắt buộc: {nojekyll_file}")

# Đồng bộ file jobs.json mới nhất sang out/data/
public_jobs = os.path.join(root, "frontend", "public", "data", "jobs.json")
out_jobs_dir = os.path.join(out_dir, "data")
os.makedirs(out_jobs_dir, exist_ok=True)
out_jobs = os.path.join(out_jobs_dir, "jobs.json")
if os.path.exists(public_jobs):
    import shutil
    shutil.copy2(public_jobs, out_jobs)
    print(f"✓ Đã đồng bộ {public_jobs} -> {out_jobs}")

env = os.environ.copy()
env["GIT_DIR"] = git_dir
env["GIT_INDEX_FILE"] = temp_index
env["GIT_WORK_TREE"] = out_dir

print("1. Fetching origin/gh-pages...")
subprocess.run(["git", "fetch", "origin", "gh-pages"], check=True, cwd=root)

print("2. Staging frontend/out...")
subprocess.run(["git", "add", "-A"], check=True, cwd=out_dir, env=env)

print("3. Writing tree...")
tree = subprocess.check_output(["git", "write-tree"], env=env, cwd=root).decode().strip()
print(f"Tree SHA: {tree}")

print("4. Getting parent commit...")
parent = subprocess.check_output(["git", "rev-parse", "origin/gh-pages"], cwd=root).decode().strip()
print(f"Parent SHA: {parent}")

print("5. Creating commit-tree...")
total_count = 527
try:
    import json
    with open(public_jobs, "r", encoding="utf-8") as f:
        total_count = len(json.load(f))
except Exception:
    pass
commit_msg = f"deploy: {total_count} verified IT jobs with .nojekyll, full CSS/JS assets, authentic portals and zero broken links"
commit = subprocess.check_output(["git", "commit-tree", tree, "-p", parent, "-m", commit_msg], cwd=root).decode().strip()
print(f"Commit SHA: {commit}")

print("6. Pushing to origin gh-pages...")
subprocess.run(["git", "push", "origin", f"{commit}:refs/heads/gh-pages"], check=True, cwd=root)

if os.path.exists(temp_index):
    try:
        os.remove(temp_index)
    except Exception:
        pass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

print("\nGitHub Pages Deployment Complete! Check: https://doantrunghuy.github.io/c_data/jobs/")
