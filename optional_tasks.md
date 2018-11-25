Main tasks
===
## Implement an API for fetching balance of an account
Challenges to requirements:
* Should be /accounts/?
* Why not return more information than just balance? Why have a separate endpoint for balance?

## 3. Implement an API to POST a new transaction to account.
I think you wanted this done with a Django REST validator. I don't want to use a validator here as I think the business logic here should be enforced at a lower level than the API (Accounts shouldn't go into zero regardless of the method used to create the Transaction). Also it's really messy as the account isn't available to the validator in the way I've chosen to build the view and serialiser.


General improvments
===
* More metadata for the API - I don't know my way around REST framework enough to show off here, 'options' isn't working properly for me.
* Tests are a bit rough and ready - could be split into smaller unit tests rather than these use-case based ones


Optional tasks
===

## Client & features:
### 3. Implement operations personnel access to the system. The system should allow operation personnel to find and view details of users, accounts and transactions, and to do corrections to the data.
Added via Django admin with a pretty random set of features. You can search, edit, view etc...

### 4. Implement a change to the account balance API so that it's possible to query the balance of the account at end of given date.
I did this at the API rather than model level, as 'balance at a specific date' seems to be a function of the API rather than the underlying business logic (unlike the validation!). Could move it to a method on account model.

## Authentication and audit:
### 1. Describe or implement authentication and authorisation solution for above APIs.
Depends on the use case - we already have authentication and authorisation in this example, via Django REST HTTP auth coupled with Django Users/Groups. So we could create a user for the 3rd party app, give it the permissions through the Django interface, and tell them to authenticate using username/password. Good enough for proof of concept.

However, I'd go for a token auth system. Customer logs in and creates a token via a web interface, customer then chooses a 3rd party service from a list and gives token to communicate with our API. 3rd party service authenticates itself using the customers's token (and possible whitelisting...). This allows us to revoke tokens at the service level, or for the customer to revoke individual access. System could be extended to allow us/the customer to specify levels of access dependent on the 3rd party, etc...

Or OAuth or similar - not sure about setting this up, so will shut up now.

### 2. Describe or implement an audit system for above APIs (a solution which allows one to see who did what in the system).
So out of time for this. I can think of several ways:

1. Request-level logging (Django-requests) including request data, possibly via ELK stack or similar, or JSON into PostGRES. Easy to set up, covers all routes in via the Django app, separate to the main data model, but difficult to join to main objects. More useful for 'forensic' than day to day use (e.g. "we have a problem with account X, what happened?" rather than "how many accounts have been read more than 3 times on a Sunday?")
2a. Separate audit table for each object (create via a common base class for the object), containing all the fields plus some metadata (user, session, IP) etc. Log to this on model save / delete etc. Trouble with this is it would tie fintech app to the API app very thoroughly. But it could be used to check for changes from multiple sources.
2b. What about a 'snapshots' feature, whereby the objects in each table are unique on uuid _and_ creation time. Updating them creates a new snapshot, retrieving them gets the latest snapshot. This gets very messy with queries, you need to be careful with prefetches, but is nice for objects that you expect to go through many revisions (e.g. documents). Not, however, Transactions!
3. A custom-built logging system for the API app, recording stuff that's API specific (user, session, IP, auth mechanism) plus blobs of submitted data. Log to this from the API views themselves. Trouble with this is you risk 'missing' a view or method. On the plus side, it's easy to present the information.

In this case I'd go for 1 until we have specific use/audit cases, then build 3 to suit _whilst keeping 1_.

## Devops:
### 2. Descrbe how you would implement CI for the application.
Personally, I'd use CircleCI (other tools are available!). You can see this implemented in its most basic form (tests and static analysis) in the Git repository.

Another useful thing to do would be automatic building of AWS instances for PR branches so you can do UAT on those before merging.

### 3. Assume you would need to deploy the application in AWS. Which AWS features would you use to get the app running? How would you do the deployment?
This is for a *production* deployment - you could get away with less (e.g. skip Ansible, Terraform) for a proof-of-concept.

I'd use:
* A VPC (a couple of simple security groups such as DB client, DB server, webserver, etc)
* A DB2 instance (PostGRES by preference)
* A load balancer (might as well set it up now)
* A single EC2 instance behind the load balancer (with plans to add more)

Could also consider doing a VPN gateway into the VPC for added security, but key auth over SSH could be considered sufficient

I'd set this up with Terraform, so you also need to do stuff with IAM users, keys and permission groups in Terraform, but it's well documented.

Finally, I'd configure servers, handle migrations and deploy code using Ansible. You can hook this into CI easily for continuous deployment, if desired.

## Bookkeeping:
### 1. Describe what it would mean to have a double entry bookkeeping system instead of the current single entry system. What would it imply on the data model side? Why would one want to use such a system for a bank account in general?
A double entry bookkeeping system involves having every positive transaction (a 'credit') matched by a corresponding negative transaction (a 'debit'). Debits and credits to a given account should 'balance' - hence the term, 'balance', in use in this application (it's the remaining balance after debits and credits have been summed).

In order to implement this on the data model side the simplest way is to have both the credit and debit representations stored in the same row in a transaction table, by adding a 'credited_account' and 'debited_account' relationship. Thus, every Transaction creates two entries in the bookkeeping system (the credit and it's matching debit).

In this context, the account is not a 'bank account' but a concept about where the value has ended up. Accounts can include things like 'goodwill' or 'losses'. You're going to want to consult a qualified professional here!

The advantages of using this system for a representation of a bank account include:

* It's a globally accepted standard dating back hundreds of years used by everyone doing it, including the banks you'll be interracting with. This is because...
* It's easy to validate and spot mistakes - if your credits and debits don't add up, something's gone wrong!