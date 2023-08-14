#!/bin/bash

stack_name=streamlit-dashboard-MA

# Default aws region
AWS_DEFAULT_REGION=$(aws configure list | grep region | awk '{print $2}')

#  Variables set for stack
S3_BUCKET_NAME=${stack_name}-$(uuidgen | cut -d '-' -f 5)
DATABASE_NAME=${S3_BUCKET_NAME}
GLUE_CRAWLER_NAME=${stack_name}-glue-crawler
TABLE_NAME=$(echo ${S3_BUCKET_NAME} | tr - _)

# Coginto user paramater
COGNITO_USER=XYZ@XYZ.com

echo "stack name=${stack_name}"
echo "bucket name=${S3_BUCKET_NAME}" 
echo "crawler name=${GLUE_CRAWLER_NAME}"
echo "database name=${DATABASE_NAME}"
echo "table name=${TABLE_NAME}"
echo "region=${AWS_DEFAULT_REGION}"

echo "Create the Athena Workgroup"

aws cloudformation --region ${AWS_DEFAULT_REGION} create-change-set --stack-name ${stack_name}-athena --change-set-name ImportChangeSet --change-set-type IMPORT \
--resources-to-import "[{\"ResourceType\":\"AWS::Athena::WorkGroup\",\"LogicalResourceId\":\"AthenaPrimaryWorkGroup\",\"ResourceIdentifier\":{\"Name\":\"primary\"}}]" \
--template-body file://cfn/01-athena.yaml --parameters ParameterKey="DataBucketName",ParameterValue=${S3_BUCKET_NAME} > /dev/null

echo "Downloading and loading the data into S3"

# must be lower case for s3
S3_BUCKET_NAME=$(echo "$S3_BUCKET_NAME" | awk '{print tolower($0)}')

# Create an S3 bucket
aws s3 mb s3://${S3_BUCKET_NAME} > /dev/null

# Run the Python script to scrape data
python3 ./script/scrape_data.py

# Get the date for naming the S3 folder
TODAY_DATE=$(date +"%Y-%m-%d")

# Upload scraped data to the S3 bucket
aws s3 cp ./scraped_data.csv s3://${S3_BUCKET_NAME}/${TODAY_DATE}/scraped_data.csv > /dev/null

rm -rf ./data # Deleting the file from local directory once upload to S3 is complete

echo "Data scraping and upload complete"

echo "Executing the Athena Workgroup"

aws cloudformation --region ${AWS_DEFAULT_REGION} execute-change-set --change-set-name ImportChangeSet --stack-name ${stack_name}-athena > /dev/null

echo "Building Glue Crawler"

aws cloudformation --region ${AWS_DEFAULT_REGION} create-stack --stack-name ${stack_name}-glue \
--template-body file://cfn/02-crawler.yaml --capabilities CAPABILITY_NAMED_IAM \
--parameters ParameterKey=RawDataBucketName,ParameterValue=${S3_BUCKET_NAME} \
ParameterKey=CrawlerName,ParameterValue=${GLUE_CRAWLER_NAME} > /dev/null
