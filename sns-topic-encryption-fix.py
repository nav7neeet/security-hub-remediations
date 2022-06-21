import logging
import boto3
from botocore.exceptions import ClientError

MANAGEMENT_ORG_ROLE = "list-accounts-role"
X_ACCOUNT_ROLE = "read-only-role"
MANAGEMENT_ACCOUNT_ID = "000000000000"
ROLE_SESSION_NAME = "sns-topic-encrpytion"
KMS_KEY = "alias/aws/sns"

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_role_arn(account_id, role_name):
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    return role_arn


def get_client(role_arn, service_name):
    sts_client = boto3.client("sts")
    response = sts_client.assume_role(
        RoleArn=role_arn, RoleSessionName=ROLE_SESSION_NAME
    )
    temp_creds = response["Credentials"]

    client = boto3.client(
        service_name,
        aws_access_key_id=temp_creds["AccessKeyId"],
        aws_secret_access_key=temp_creds["SecretAccessKey"],
        aws_session_token=temp_creds["SessionToken"],
    )
    return client


def get_aws_accounts(organizations):
    accounts_list = []
    paginator = organizations.get_paginator("list_accounts")
    pages = paginator.paginate()

    for page in pages:
        for account in page["Accounts"]:
            accounts_list.append({"name": account["Name"], "id": account["Id"]})

    return accounts_list


def get_topic_list(sns):
    topic_list = []
    paginator = sns.get_paginator("list_topics")
    response_iterator = paginator.paginate()
    for item in response_iterator:
        for topic in item["Topics"]:
            topic_list.append(topic["TopicArn"])
    return topic_list


def get_encryption_status(sns, TopicArn):
    response = sns.get_topic_attributes(TopicArn=TopicArn)
    encryption_status = False

    if "KmsMasterKeyId" in response["Attributes"]:
        encryption_status = True
    return encryption_status


def set_sns_topic_encryption(sns, TopicArn, KmsMasterKeyId):
    response = sns.set_topic_attributes(
        TopicArn=TopicArn, AttributeName="KmsMasterKeyId", AttributeValue=KmsMasterKeyId
    )


def main():
    role_arn = get_role_arn(MANAGEMENT_ACCOUNT_ID, MANAGEMENT_ORG_ROLE)
    client = get_client(role_arn, "organizations")
    accounts_list = get_aws_accounts(client)

    for account in accounts_list:
        try:
            logger.info("###Processing AWS account: " + account["id"])
            role_arn = get_role_arn(account["id"], X_ACCOUNT_ROLE)
            # if account["id"] == "000000000000":
            sns = get_client(role_arn, "sns")
            topic_list = get_topic_list(sns)

            for topic in topic_list:
                try:
                    encryption_status = get_encryption_status(sns, topic)
                    if encryption_status is False:
                        print(f"enabling encryption for topic -{topic}")
                        set_sns_topic_encryption(sns, topic, KMS_KEY)
                except Exception as error:
                    logger.error(f"*** An error occured ***" + str(error))

        except Exception as error:
            logger.error(f"*** An error occured *** \n: {role_arn} " + str(error))


if __name__ == "__main__":
    main()
