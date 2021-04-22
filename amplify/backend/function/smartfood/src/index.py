import json
import boto3
# from usda import UsdaClient
# import noms
# import requests
# from requests.auth import HTTPBasicAuth
# from flask_cors import CORS
import urllib3

http = urllib3.PoolManager()
API_KEY="e9cl5VngIZPJ3rlP0TjbPfSNatfdGzsxHreADbFR"
NUTRIENTS_NUMBER_LIST = ["203", "204", "205", "606", "269",
"306", "291", "303", "307", "301", "601", "208", "328", "618"]

def recognizeImage():
    client = boto3.client("rekognition", region_name="us-west-2")
    s3 = boto3.client("s3")
    model='arn:aws:rekognition:us-west-2:766312307144:project/test_size_recognition2/version/test_size_recognition2.2021-04-18T12.53.24/1618775602186'
    # response = client.detect_labels(Image = {"S3Object": {"Bucket": "recognize13339-dev", "Name": "public/userUpload.png"}}, MaxLabels=5, MinConfidence=70)

    # response = client.detect_labels(Image = {"S3Object": {"Bucket": "custom-labels-console-us-west-2-060fcfbb0a", "Name": "public/upload.png"}}, MaxLabels=5, MinConfidence=70)
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': "custom-labels-console-us-west-2-73aca6ff8c", 'Name': "assets/testing/upload.png"}},
         MinConfidence=95,
        ProjectVersionArn=model)
    print(response)
    return response


def nutrientHelper():
    recognizedFoodList=[]
    try:
        imageResult = recognizeImage()
        if len(imageResult) > 0 :
            for i in imageResult["CustomLabels"]:
                nutrientList = []
                recognizedFood ={}
                if i["Name"] == "Food":
                    continue
                foodName = i["Name"]
                print("foodName")
                print(foodName)
                if foodName == "ice_cream":
                    foodName = "icecream"
                if foodName == "hot_dog":
                    foodName = "hotdog"
                if foodName == "club_sandwich":
                    foodName = "sandwich"
                if foodName == "french_fries":
                    foodName = "fries"
                # if('Burger' in foodName):
                #     url = "https://api.nal.usda.gov/fdc/v1/foods/search?"+ "api_key="+API_KEY+'&query="'+foodName+'" mcdonald'
                # else:
                url = "https://api.nal.usda.gov/fdc/v1/foods/search?"+ "api_key="+API_KEY+'&query="'+foodName+'"'
                # print(url)
                responseBody = http.request('GET', url)
                response = json.loads(responseBody.data)
                print(response)
                food = response['foods'][0]
                recognizedFood['description'] = food['description']

                for nutrient in food['foodNutrients']:
                    foodNutrients={}
                    if nutrient['nutrientNumber'] not in NUTRIENTS_NUMBER_LIST:
                        continue
                    elif nutrient['nutrientNumber'] == "618":
                        foodNutrients['nutrientName'] = "Trans Fat"
                    elif nutrient['nutrientNumber'] == "208":
                        foodNutrients['nutrientName'] = "Calories"
                    else:
                        foodNutrients['nutrientName'] = nutrient['nutrientName']
                    if nutrient['unitName'] == "KCAL":
                        foodNutrients['unitName'] = "CAL"
                    else:
                        foodNutrients['unitName'] = nutrient['unitName'].lower()
                    foodNutrients['value'] = nutrient['value']
                    nutrientList.append(foodNutrients)

                recognizedFood['foodNutrients'] = nutrientList
                recognizedFoodList.append(recognizedFood)

        return recognizedFoodList

    except Exception as e:
        return ("error: {}", e)

def handler(event, context):
    responseObject = nutrientHelper()
    return {
        'statusCode': 200,
        'body': json.dumps(responseObject),
        'headers': {
            'Content-Type' : 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Headers' : '*'
        }
    }

# def display_image(bucket,photo,response):
#     # Load image from S3 bucket
#     s3_connection = boto3.resource('s3')
#
#     s3_object = s3_connection.Object(bucket,photo)
#     s3_response = s3_object.get()
#
#     stream = io.BytesIO(s3_response['Body'].read())
#     image=Image.open(stream)
#
#     # Ready image to draw bounding boxes on it.
#     imgWidth, imgHeight = image.size
#     draw = ImageDraw.Draw(image)
#
#     # calculate and display bounding boxes for each detected custom label
#     print('Detected custom labels for ' + photo)
#     for customLabel in response['CustomLabels']:
#         print('Label ' + str(customLabel['Name']))
#         print('Confidence ' + str(customLabel['Confidence']))
#         if 'Geometry' in customLabel:
#             box = customLabel['Geometry']['BoundingBox']
#             left = imgWidth * box['Left']
#             top = imgHeight * box['Top']
#             width = imgWidth * box['Width']
#             height = imgHeight * box['Height']
#
#             fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
#             draw.text((left,top), customLabel['Name'], fill='#00d400', font=fnt)
#
#             print('Left: ' + '{0:.0f}'.format(left))
#             print('Top: ' + '{0:.0f}'.format(top))
#             print('Label Width: ' + "{0:.0f}".format(width))
#             print('Label Height: ' + "{0:.0f}".format(height))
#
#             points = (
#                 (left,top),
#                 (left + width, top),
#                 (left + width, top + height),
#                 (left , top + height),
#                 (left, top))
#             draw.line(points, fill='#00d400', width=5)
#
#     image.show()
#
# def show_custom_labels(model,bucket,photo, min_confidence):
#     client=boto3.client('rekognition')
#
#     #Call DetectCustomLabels
#     response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
#         MinConfidence=min_confidence,
#         ProjectVersionArn=model)
#
#     # For object detection use case, uncomment below code to display image.
#     # display_image(bucket,photo,response)
#
#     # return len(response['CustomLabels'])
#     return response
#
# def main():
#
#     bucket='custom-labels-console-us-west-2-060fcfbb0a'
#     photo='assets/testing/image 6.jpg'
#     model='arn:aws:rekognition:us-west-2:671636637184:project/Fast_Food_Image_Recognition4/version/Fast_Food_Image_Recognition4.2021-04-07T22.22.07/1617859327795'
#     min_confidence=95
#
#     label=show_custom_labels(model,bucket,photo, min_confidence)
#     print(label)
#     # print("Custom labels detected: " + str(label_count))
#
#
#
if __name__ == "__main__":
    print('testing')
    # response = handler("null", "null")
    # responseBody = json.loads(response['body'])
    # foodName = responseBody['Labels'][0]['Name']
    # foodName = "coffee"
    # main()
    responseObject = recognizeImage()
    print(responseObject)
    # print(responseObject)
    # print(json.dumps(responseObject, indent=4, sort_keys=True))
    # for i in responseObject["Labels"]:
    #     print(i)
    # print(len(responseObject))
    # print(json.dumps(responseObject))
