# Backend

## Build & Deploy

```bash
sam validate
sam build
sam deploy --stack-name interview-mentorship-backend --resolve-s3 --resolve-image-repos --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM
```

## Delete

```bash
sam delete --stack-name interview-mentorship-frontend
```
