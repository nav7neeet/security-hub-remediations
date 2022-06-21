# security-hub-remediations

## About <br>

Security Hub reports a medium severity finding - SNS.1 SNS topics should be encrypted at-rest using AWS KMS if encrpytion is not enabled for SNS topics. The python script sns-topic-encryption-fix.py first assumes a role in the management account (Parent account) to get the list of AWS accounts. It then assumes a role in each account one by one and lists out all the SNS topics.

It then checks the encryption status of each SNS topic and builds a list of topics which does not have encryption enabled. It iterates through that list and enables encryption for the SNS topics.

## Required Configuration <br>

MANAGEMENT_ORG_ROLE = "list-accounts-role" --role in the management account to get account list with trust relationship to your Infra or some other account <br>
X_ACCOUNT_ROLE = "read-only-role" -- cross account role deployed in member accounts (child accounts) with trust relationship to your Infra or some other account <br>
MANAGEMENT_ACCOUNT_ID = "000000000000" -- Account number of management account <br>
ROLE_SESSION_NAME = "sns-topic-encrpytion" --role session name <br>
