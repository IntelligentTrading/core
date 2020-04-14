# Connect Customer to ITF feed with signals

Intelligent Trading Foundation (ITF) uses Amazon Simple Notification Service (SNS) to deliver signals (aka ITF signals) to customers.
We recommend our customers to use AWS SQS queue to read ITF signals.
Other possibilities are HTTP/S, email, SMS, Lambda.

## How to subscribe customer's AWS SQS queue to our ITF signals 

1. Customer [creates AWS SQS standard queue](https://console.aws.amazon.com/sqs/) and sends us ARN for this queue (like: arn:aws:sqs:us-east-1:983584755688:my_sqs_queue). 
Our app will send signals to this SQS queue. 

2. We use AWS SNS console to subscribe client's SQS endpoint to our signal's SNS feed. 

    * Sign in to the AWS Management Console and open the [Amazon SNS console](https://console.aws.amazon.com/sns/v2/home).
    * In the navigation pane, select the topic (for production core app: itf-sns-core-signals-production,  for stage: itf-sns-core-signals-stage).
    * Choose Create Subscription, select Amazon SQS for Protocol, paste in the ARN for the queue that you want the topic to send messages to for Endpoint, and choose Subscribe.
    * After that, a message of type SubscriptionConfirmation is sent to the SQS queue and the subscription is displayed in the Amazon SNS console with its Subscription ID set to Pending Confirmation. To confirm the subscription, a customer must visit the URL specified in the SubscribeURL value in the message. Until the subscription is confirmed, no notifications published to the topic are sent to the queue. To confirm a subscription, you can use the Amazon SQS console or the ReceiveMessage API action.