import boto3
import json

def lambda_handler(event, context):

    # Get the specific EC2 instance.
    ec2_client = boto3.client('ec2')
    
    # Assume compliant by default
    compliance_status = "COMPLIANT"  
    
    # Extract the configuration item from the invokingEvent
    #The event Object (What Triggers This Lambda)
    #When AWS Config detects a change in your infrastructure, it calls this Lambda and sends an event dictionary. Here is what that event looks like:
    #######
    {
      "invokingEvent": "{\"configurationItem\":{\"configurationItemCaptureTime\":\"2024-01-15T10:30:00Z\",\"configurationItemStatus\":\"OK\",\"resourceType\":\"AWS::EC2::Instance\",\"resourceId\":\"i-0abc123def456\",\"configuration\":{\"instanceId\":\"i-0abc123def456\",\"instanceType\":\"t3.medium\",\"state\":{\"name\":\"running\"}}},\"notificationCreationTime\":\"2024-01-15T10:30:05Z\",\"messageType\":\"ConfigurationItemChangeNotification\"}",

      "resultToken": "myResultToken12345"
    }
    #######

    #It convert the json string into dictionary
    config = json.loads(event['invokingEvent'])
    
    configuration_item = config["configurationItem"]
    
    # Extract the instanceId
    instance_id = configuration_item['configuration']['instanceId']
    
    # Get complete Instance details
    # (InstanceIds=[instance_id])  ======  means filter only particular instanceId, means only one resevationId will be there.
    ######
    {
      "Reservations": [
        {
          "ReservationId": "r-001",
          "Instances": [
            { "InstanceId": "i-aaa111", "InstanceType": "t3.medium" },
            { "InstanceId": "i-bbb222", "InstanceType": "t3.medium" }
          ]
        {
      [    
    }
    ######
    instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    
    # Check if the specific EC2 instance has Cloud Trail logging enabled.
    
    if not instance['Monitoring']['State'] == "enabled":
        compliance_status = "NON_COMPLIANT"

    #### This is the result you are sending back to AWS Config. It looks like:
    evaluation = {
        'ComplianceResourceType': 'AWS::EC2::Instance',
        'ComplianceResourceId': instance_id,
        'ComplianceType': compliance_status,
        'Annotation': 'Detailed monitoring is not enabled.',
        'OrderingTimestamp': config['notificationCreationTime']
    }
    
    config_client = boto3.client('config')

    ### put_evaluations sends the compliance result to AWS Config.
    
    response = config_client.put_evaluations(
        Evaluations=[evaluation],
        ResultToken=event['resultToken']
    )  
    
    return response
