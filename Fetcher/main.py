import simplejson as json

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
  DeleteRowsEvent,
  UpdateRowsEvent,
  WriteRowsEvent,
)
from pymysqlreplication.event import (
    QueryEvent,
    RotateEvent
)

# DynamoDB Connection

# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.table('DataStitchingOpenHack')

from utils import concat_sql_from_binlog_event
import pymysql
import os
import sys
import logging
import argparse
import boto3

Keyname = "log_pos"
Keyname_2 = "binlog_file"

client = boto3.client(
    "sns",
    aws_access_key_id="AKIA4GMGWBHWEKGGK2FE",
    aws_secret_access_key="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",
    region_name="ap-southeast-1"

)

parser = argparse.ArgumentParser()

MYSQL_SETTINGS = {
    "host": "openhack-flydata.cdvbjpsetxhz.ap-southeast-1.rds.amazonaws.com",
    "port": 3306,
    "user": "shubug",
    "passwd": "Thumbsdown7320#"
}

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s %(message)s")


def getItem(Keyname):

    try:
    response = table.get_item(
        Key={
            'Keyname': Keyname,
        }
    )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        print("GetItem succeeded:")
        print(json.dumps(item))
        
    return item['Keyvalue']

def updateItem(pos, binlog_file):

    response = table.update_item(
        Key={
            'Keyname': Keyname,
        },
        UpdateExpression="set Keyvalue = :r",
        ExpressionAttributeValues={
            ':r': pos,
        },
        ReturnValues="UPDATED_NEW"
    )

    response = table.update_item(
        Key={
            'Keyname': Keyname_2,
        },
        UpdateExpression="set Keyvalue = :r",
        ExpressionAttributeValues={
            ':r': binlog_file,
        },
        ReturnValues="UPDATED_NEW"
    )

def main():

# DynamoDB ----------------------------

#     Keyvalue = ""
#     Keyvalue_2 = ""

#     response = table.put_item(
#    I   Item={
#             'Keyname': Keyname,
#             'Keyvalue': Keyvalue,
#         }
#     )
#     response = table.put_item(
#    I   Item={
#             'Keyname': Keyname_2,
#             'Keyvalue': Keyvalue_2,
#         }
#     )

#  ------------------------------------------
    parser.add_argument("--log_pos", "-p", help="enter the starting position")
    parser.add_argument("--log_file", "-f", help="enter the log file")
    args = parser.parse_args()
    if args.log_pos:
        args.log_pos = int(args.log_pos)

    # Get Item For DynamoDB ------------------------------
    # args.log_pos = getItem(Keyname)
    # args.log_file = getItem(Keyname_2)
    #-----------------------------------------------------

    conn = pymysql.connect(**MYSQL_SETTINGS)  
    cursor = conn.cursor()
    stream = BinLogStreamReader(connection_settings=MYSQL_SETTINGS,
                                server_id=3,
                                blocking=True,
                                only_events=[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent, QueryEvent,RotateEvent],
                                log_file=args.log_file,
                                log_pos=args.log_pos,
                                resume_stream=True
                                )
    next_binlog = ''
    delimit = ';'
    TopicArn = 'arn:aws:sns:ap-southeast-1:838337956332:Openhack-Data-Stiching'
    for binlogevent in stream:
        e_start_pos, last_pos = stream.log_pos, stream.log_pos
        if type(binlogevent).__name__ == 'RotateEvent':
            next_binlog = binlogevent.next_binlog
        else:
            result = concat_sql_from_binlog_event(cursor=cursor, binlog_event=binlogevent, row=None, e_start_pos=e_start_pos)
            result['next_binlog'] = next_binlog
            if 'Query' in result:
                result['Query'] = result['Query'].partition(delimit)[2]
            for k, v in result.items():
                if k == 'Query' and "rds_heartbeat2" not in v:
                    if v:
                        client.publish(
                            TopicArn=TopicArn,
                            Message=v
                        )
                        # Update Item For DynamoDB ------------------------------
                        # updateItem(result['position'], result['next_binlog'])
                        #------------------------------------------------------

            print(json.dumps(result))


    stream.close()


if __name__ == "__main__":
    main()

# May need later
    # else:
    #     for row in binlogevent.rows:
    #         event = {"schema": binlogevent.schema,
    #             "table": binlogevent.table,
    #             "type": type(binlogevent).__name__,
    #             "row": row
    #         }
    #         #if isinstance(binlog_event, QueryEvent) and binlog_event.query == 'BEGIN':
    #         #  e_start_pos = last_pos
    #         # print("/*", json.dumps(event), "*/")
    #         result = concat_sql_from_binlog_event(cursor=cursor, binlog_event=binlogevent, row=row, e_start_pos=e_start_pos)
    #         result['next_binlog'] = next_binlog
    #         # result['Query'] = result['Query'].partition(delimit)[2]
    #         # for k, v in result.items():
    #         #     if k == 'Query':
    #         #         print(v)
    #         # print(json.dumps(result))