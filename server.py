import os
import subprocess
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return "Server Running ✅"

#
@app.post("/geno")
async def post_sequence(req: Request):
    form = await req.form()
    file = form.get("file")
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    job_id = req.job_id or str(uuid.uuid4())

    # Save file
    input_filepath = f"uploads/{job_id}/{file.filename}"
    contents = await file.read()
    with open(input_filepath, "wb") as f:
        f.write(contents)

    output_dir = f"uploads/{job_id}"

    # Run ./selemenium.py
    subprocess.run(["python",
                    "/app/selemenium_python_geno2pheno.py",
                    input_filepath,
                    "/root/chromedriver",
                    output_dir])

    # Delete the input file
    os.remove(input_filepath)

    # Create a tar.gz file of the output directory
    tar_filepath = f"{output_dir}.tar.gz"
    subprocess.run(["tar", "-czf", tar_filepath, "-C", output_dir, "."])

    # Open the tar.gz file for streaming
    tar_stream = open(tar_filepath, "rb")
    return StreamingResponse(tar_stream, media_type="application/gzip", headers={"Content-Disposition": f"attachment; filename={job_id}.tar.gz"})