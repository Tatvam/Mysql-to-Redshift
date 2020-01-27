import boto3
import subprocess
import os
import simplejson as json
import psycopg2

def main():
    sqs = boto3.client(
        "sqs",
        aws_access_key_id="XXXXXXXXXXXXX",
        aws_secret_access_key="XXXXXXXXXXXXXXXXXXXX",
        region_name="ap-southeast-1"
    )

    con=psycopg2.connect(dbname='openhack', host='openhack-redshift-cluster.XXXXXXXXXXX.ap-southeast-1.redshift.amazonaws.com',
                        port=5439, user='XXXXXXXXXXX', password='XXXXXXXXXX')

    #cur = con.cursor()
    queue_url = 'XXXXXXXXXXXXXXXXXXXXXXX/DataStitchingQueue'

    program_name = "./sqlines/./sqlines"
    arguments = ["-s=mysql", "-t=redshift", "-in=./SqlQueries.sql"]

    command=[program_name]
    command.extend(arguments)
    while True:
        #print("Debug")
        cur=con.cursor()
        resp = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=2
        )
        messages = []
        try:
            messages.extend(resp['Messages'])
        except KeyError:
            continue
        
        # print(resp['Messages'])

        entries = [
            {'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle'], 'Message': msg['Body']}
            for msg in resp['Messages']
        ]

        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=entries[0]['ReceiptHandle']
        )
        queryJ = json.loads(entries[0]['Message'])
        query = queryJ['Message']
        # print(query)
        if query !=' ':
            sqlFile = open("./sqlines/SqlQueries.sql","w+")
            sqlFile.write(query)
            sqlFile.close()
            output = subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]
            # f= open("./python-final/sqlines/SqlQueries_out.sql","w+").close()
            postgesqlFile = open("./sqlines/SqlQueries_out.sql","r")
            plsqlQuery = postgesqlFile.read()
            plsqlQuery = plsqlQuery[:plsqlQuery.find(";")]
            print(plsqlQuery)
            cur.execute(plsqlQuery)
            con.commit()
            #version = cur.fetchone()[0]
            #print(version)
            print (postgesqlFile.read())
            os.remove("./sqlines/SqlQueries.sql")
            os.remove("./sqlines/SqlQueries_out.sql")

if __name__ == "__main__":
    main()


