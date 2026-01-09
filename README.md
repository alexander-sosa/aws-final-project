# Serverless File Gateway (API Gateway + Lambda + S3)

This project provides a simple Serverless File Gateway implemented with AWS SAM. It exposes two Lambda-backed API endpoints:

- `POST /files` — returns a presigned upload URL for a client to PUT a file to S3.
- `GET /files/{objectKey}` — returns a 307 redirect to a presigned download URL.

Files:

- [finallab.yaml](finallab.yaml) — Github Actions template to configure and deploy stack.
- [template.yaml](template.yaml) — SAM template defining the API, Lambda functions, and S3 bucket.
- [src/app.py](src/app.py) — Lambda handlers and logic.

Configuration Steps

- AWS account with permissions to create CloudFormation stacks, Lambda, API Gateway, and S3. This account will be used to connect with Open ID Connect (OIDC)
- Configure the account ARN into GH Actions variables. Go to Settings -> Secrets and variables -> Actions -> Variables -> Repository variables.
- Set the name as AWS_ROLE_ARN and the value as arn:aws:iam::{YOUR_ID}:role/GithubConnect (should be your account configured with OIDC)


Deployment Steps and How to run
- Fork the Github repo
- Make a little change on the repo (for example, in the readme)
- Commit and push the changes and Github Actions will automatically execute the workkflow
- Check Github actions logs to see the results
- After the execution, you can check in AWS CloudFormation for the output variables. After that you can start testing making requests to the API endpoints

- Upload flow (example):
  1. Request an upload URL:

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"filename":"example.txt","contentType":"text/plain"}' \
  {API_URL}/files
```

  2. Use the returned `uploadUrl` to PUT the file content (set `Content-Type` with the same data as the first request, otherwise it will not work). Also, refer to the path of an existing file and replace it into @filename.png to upload it

```bash
curl -X PUT "GENERATED_URL" -H "Content-Type: image/png" --data-binary @filename.png
```

- Download flow (example):

```bash
curl -L -o downloaded_name.png https://API_URL/files/OBJECT_KEY
```

The response will be a 307 redirect with a `Location` header pointing to the presigned S3 URL. With -L curl will follow the redirection and get to the file 

Link to the Google Docs file
https://docs.google.com/document/d/16ziKY-FBjq3budPgdzEmDtdg-F-LaHVfBPScC3Etsk4/edit?usp=sharing