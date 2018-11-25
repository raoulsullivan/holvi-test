Main tasks
===
##Implement an API for fetching balance of an account
Challenges to requirements:
* Should be /accounts/?
* Why not return more information than just balance? Why have a separate endpoint for balance?

##3. Implement an API to POST a new transaction to account.
I think you wanted this done with a Django REST validator. I don't want to use a validator here as I think the business logic here should be enforced at a lower level than the API (Accounts shouldn't go into zero regardless of the method used to create the Transaction). Also it's really messy as the account isn't available to the validator in the way I've chosen to build the view and serialiser.


Optional tasks
===

##Client & features:
###3. Implement operations personnel access to the system. The system should allow operation personnel to find and view details of users, accounts and transactions, and to do corrections to the data.
###4. Implement a change to the account balance API so that it's possible to query the balance of the account at end of given date.

##Authentication and audit:
###1. Describe or implement authentication and authorisation solution for above APIs.
###2. Describe or implement an audit system for above APIs (a solution which allows one to see who did what in the system).

##Devops:
###2. Descrbe how you would implement CI for the application.
Personally, I'd use CircleCI (other tools are available!). You can see this implemented in its most basic form (tests and static analysis) in the Git repository.

Another useful thing to do would be automatic building of AWS instances for PR branches so you can do UAT on those before merging.

###3. Assume you would need to deploy the application in AWS. Which AWS features would you use to get the app running? How would you do the deployment?
This is for a *production* deployment - you could get away with less (e.g. skip Ansible, Terraform) for a proof-of-concept.

I'd use:
* A VPC (a couple of simple security groups such as DB client, DB server, webserver, etc)
* A DB2 instance (PostGRES by preference)
* A load balancer (might as well set it up now)
* A single EC2 instance behind the load balancer (with plans to add more)

Could also consider doing a VPN gateway into the VPC for added security, but key auth over SSH could be considered sufficient

I'd set this up with Terraform, so you also need to do stuff with IAM users, keys and permission groups in Terraform, but it's well documented.

Finally, I'd configure servers, handle migrations and deploy code using Ansible. You can hook this into CI easily for continuous deployment, if desired.

##Bookkeeping:
###1. Describe what it would mean to have a double entry bookkeeping system instead of the current single entry system. What would it imply on the data model side? Why would one want to use such a system for a bank account in general?
A double entry bookkeeping system involves having every positive transaction (a 'credit') matched by a corresponding negative transaction (a 'debit'). Debits and credits to a given account should 'balance' - hence the term, 'balance', in use in this application (it's the remaining balance after debits and credits have been summed).

In order to implement this on the data model side the simplest way is to have both the credit and debit representations stored in the same row in a transaction table, by adding a 'credited_account' and 'debited_account' relationship. Thus, every Transaction creates two entries in the bookkeeping system (the credit and it's matching debit).

In this context, the account is not a 'bank account' but a concept about where the value has ended up. Accounts can include things like 'goodwill' or 'losses'. You're going to want to consult a qualified professional here!

The advantages of using this system for a representation of a bank account include:

* It's a globally accepted standard dating back hundreds of years used by everyone doing it, including the banks you'll be interracting with. This is because...
* It's easy to validate and spot mistakes - if your credits and debits don't add up, something's gone wrong!