"""Deploy VoxCPM2 endpoint with custom Docker image.

Usage:
    python scripts/deploy.py [--env prod]
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MANIFEST = PROJECT / ".flash" / "flash_manifest.json"
ARTIFACT = PROJECT / ".flash" / "artifact.tar.gz"
CUSTOM_IMAGE = "ghcr.io/osvaldgerandro-ux/voxcpm2-runpod:latest"


def build():
    """Run flash build to generate artifact and manifest."""
    result = subprocess.run(
        ["flash", "build"],
        cwd=PROJECT,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(f"Build failed: {result.stderr[-500:]}")
    print("Build OK")


def patch_manifest():
    """Patch imageName in the manifest to use our custom image."""
    if not MANIFEST.exists():
        raise SystemExit(f"Manifest not found at {MANIFEST}")

    manifest = json.loads(MANIFEST.read_text())
    
    for name, res in manifest.get("resources", {}).items():
        old = res.get("imageName", "(none)")
        res["imageName"] = CUSTOM_IMAGE
        print(f"  {name}: imageName {old} -> {CUSTOM_IMAGE}")
    
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print("Manifest patched OK")


async def deploy(env_name: str):
    """Upload artifact and deploy with patched manifest."""
    from runpod_flash.core.resources.app import FlashApp
    from runpod_flash.cli.utils.deployment import deploy_from_uploaded_build, validate_local_manifest

    # Discover the app
    from runpod_flash.cli.utils.app import discover_flash_project
    project_dir, app_name = discover_flash_project()

    app = await FlashApp.from_name(app_name)
    envs = await app.list_environments()
    existing = {e["name"] for e in envs}

    if env_name not in existing:
        print(f"Creating environment '{env_name}'...")
        await app.create_environment(env_name)

    # Upload artifact
    import time as _time
    from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn

    archive_size = ARTIFACT.stat().st_size
    t0 = _time.monotonic()

    with Progress(
        BarColumn(bar_width=30), DownloadColumn(), TransferSpeedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("upload", total=archive_size)
        def _on_progress(n: int):
            progress.advance(task, n)
        app._upload_progress_callback = _on_progress
        try:
            build = await app.upload_build(ARTIFACT)
        finally:
            app._upload_progress_callback = None

    upload_s = _time.monotonic() - t0
    print(f"Uploaded {archive_size/1e6:.1f}MB in {upload_s:.1f}s")

    # Deploy
    local_manifest = json.loads(MANIFEST.read_text())
    print(f"Deploying with image: {CUSTOM_IMAGE}")
    
    result = await deploy_from_uploaded_build(
        app, build["id"], env_name, local_manifest
    )

    endpoints = result.get("resources_endpoints", {})
    for name, url in endpoints.items():
        print(f"\n  {name}: {url}/runsync")
    
    print(f"\ncurl test:\n  curl -X POST {list(endpoints.values())[0]}/runsync \\\n"
          f'    -H "Content-Type: application/json" \\\n'
          f'    -H "Authorization: Bearer $RUNPOD_API_KEY" \\\n'
          f'    -d \'{{"input": {{"text": "Hello world", "voice": "female_en"}}}}\'')


if __name__ == "__main__":
    env = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--env" else "production"
    build()
    patch_manifest()
    asyncio.run(deploy(env))
