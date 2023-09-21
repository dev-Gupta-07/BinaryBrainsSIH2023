from textblob import TextBlob
from googletrans import Translator
import spacy
import re
nlp = spacy.load("en_core_web_sm")

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
API_KEY = "0e08c6cc73msha55f83b3d8d091fp137db5jsn1bb5fd0fbd05"

def words_to_number(word_string):
    
    word_to_number = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
        'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
        'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
        'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
        'eighty': 80, 'ninety': 90
    }

    words = word_string.split()
    total = 0
    current_number = 0

    for word in words:
        if word in word_to_number:
            current_number += word_to_number[word]
        elif word == 'hundred':
            current_number *= 100
        elif word == 'and':
            pass 
        else:
            total += current_number
            current_number = 0

    total += current_number
    return total


def extract_info(sentence):
    doc = nlp(sentence)
    starting_point = []
    destination = []
    journey_date = None
    duration = 0.0
    Train_Num = 00000
    source_code = None
    dest_code = None
    pnr = 00000000

    station_codes = [
        "hwh", "agp", "koaa", "adi", "cdk", "vjpj", "kgp", "blda", "cnb", "sknp",
        "pryj", "pnbe", "dvd", "bza", "vjr", "gkp", "gkc", "lc", "ljn", "ddu",
        "mdd", "csmt", "ltt", "bdts", "bvi", "et", "bsp", "blqr", "ngp", "ajni",
        "brc", "cyi", "jp", "gadj", "rksh", "ju", "knw", "indb", "ms", "msb", "sdah",
        "ndls", "bsb", "agc", "aga", "sina", "snar", "cdg", "bnc", "sbc", "pdy",
        "ud", "krmi", "njp", "jpg", "ers", "ern", "mys", "bls", "kgm", "sml",
        "cph", "pta", "jat", "bbs", "stp", "udz", "ddn", "vskp", "vpr", "ghy",
        "aza", "dj", "umb", "asn", "jmt", "brdh", "bwn", "kkde", "snp", "pnp",
        "bpl", "gwl", "rkmp", "vglj", "cch", "pune", "hdp", "kyn", "tna", "pnvl",
        "oka", "szm", "dec", "kiv", "bprs", "hld", "gtd", "rdde", "rnt"]

    cities = [
        "howrah", "kolkata", "ahmedabad", "kharagpur", "kanpur", "allahabad", "patna", "vijayawada", "gorakhpur",
        "lucknow", "mughalsarai", "mumbai", "itarsi", "bilaspur", "nagpur", "mumbai", "vadodara", "jaipur", "rishikesh",
        "jodhpur", "chennai", "kolkata", "new delhi", "varanasi", "agra", "srinagar", "chandigarh", "bangalore", "puducherry",
        "karmali", "new jalpaiguri", "ernakulam", "mysore", "kathgodam", "shimla", "jammu tawi", "bhubaneswar", "udaipur",
        "dehradun", "visakhapatnam", "guwahati", "darjeeling", "ambala", "asansol", "barddhaman", "kurukshetra", "sonipat",
        "panipat", "bhopal", "pune","delhi"]

    month_map = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12",
    }

    encountered_on = False  # Flag to track the "on" keyword
    encountered_to = False
    encountered_from = False
    encountered_in = False
    another = False
    encountered_train = False
    encountered_pnr = False
    andp = False
    temp1 = ""
    temp2 = ""

    for token in doc:

        if token.text == "train":

            encountered_train = True
            encountered_in = False
            continue

        if token.text == "and":
            continue

        if token.text == "number" and encountered_train:
            encountered_train = True
            encountered_in = False
            continue

        if token.text == "pnr":
            encountered_pnr = True
            continue

        if encountered_pnr and token.text == "number":
            encountered_pnr = True
            continue

        if encountered_pnr:
            pnr = int(token.text)
            encountered_pnr = False

        if encountered_train:
            if token.text[0] >= '0' and token.text[0] <= '9':
                Train_Num = int(token.text)
            encountered_train = False

        if token.text == '.' or token.text == ',':
            encountered_from = False
            encountered_to = False
            continue
        elif token.text == "minutes":
            duration = duration / 60

        if token.text == "another" or token.text == "next" or token.text == "the next" or token.text == "the another":
            another = True
            continue

        if token.text == "in":
            encountered_to = False
            encountered_in = True

        elif encountered_in and another:
            if token.text[0] >= '0' and token.text[0] <= '9':
               duration = int(token.text)
            else:
               duration = words_to_number(token.text)
            encountered_in = False
        elif encountered_in and andp:
            if token.text in cities:
                encountered_in = False
            destination.append(token.text)
        elif encountered_in:
            temp1 += token.text + " "
            starting_point.append(token.text)
            if temp1.strip() in cities:
                andp = True
        elif "to" == token.text:
            encountered_to = True
            encountered_from = False

            # destination = [t.text for t in token.subtree if t.dep_ not in ('punct', 'prep')
        elif "from" == token.text:
            # starting_point = [t.text for t in token.subtree if t.dep_ not in ('punct', 'prep')]
            # print(starting_point)
            encountered_from = True
        elif "on" == token.text and journey_date == None:
            encountered_from = False
            encountered_to = False
            encountered_on = True
            temp1 = [t.text for t in token.subtree if t.dep_ not in (
                'punct', 'prep')]
            date_tokens = temp1

            if len(date_tokens) >= 2:
                day = date_tokens[1]

                if day[0] >= '0' and day[0] <= '9':
                   month = month_map.get(date_tokens[0])
                else:
                    day = date_tokens[0]
                    month = month_map.get(date_tokens[1])

                text = day
                inte = re.findall(r'\d+', text)

                if day and month:
                    journey_date = f"{inte[0]}-{month}-2023"

        elif encountered_from:

            if token.text in station_codes:
                source_code = token.text
                encountered_from = False
            else:
               if token.text in cities:
                   encountered_from = False
               starting_point.append(token.text)
        elif encountered_to:
            if token.text in station_codes:
                dest_code = token.text
                encountered_to = False
            else:
                if token.text in cities:
                    encountered_to = False
                destination.append(token.text)
        elif journey_date != None:
            encountered_on = False

    return " ".join(starting_point), " ".join(destination), journey_date, duration, Train_Num, source_code, dest_code, pnr





@app.route('/search_station', methods=['GET'])
def search_station():
    
    source_city = request.args.get("query")
    lang=request.args.get("toLang")
    print(source_city)
    print(lang)
    
    if not source_city:
        return jsonify({"error": "Please provide a query parameter 'query' with the source city."}), 400

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "irctc1.p.rapidapi.com",
    }
    
    translator = Translator()

   
    translated_source_city = translator.translate(
        source_city, dest="en").text

    print(translated_source_city)



    params = {"query": translated_source_city}
    url = "https://irctc1.p.rapidapi.com/api/v1/searchStation"

    try:
        response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()
        station_data = response.json()
        data=station_data.get('data')
        print(data)
        for item in data:
            print(".")
            item['name']=translator.translate(item['name'],dest=lang).text
        
        print(data)
        
     
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

irctc_api_url = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"


headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "irctc1.p.rapidapi.com",
}










@app.route('/get_pnr_status', methods=['GET'])
def get_pnr_status():
    # Get the PNR number from the request parameters
    pnr_number = request.args.get('pnrNumber')
    lang=request.args.get('lang')
    # Check if the PNR number is provided
    if not pnr_number:
        return jsonify({'error': 'PNR number is required'}), 400

    # Define the headers for the API request
    headers = {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': 'irctc1.p.rapidapi.com'
    }

    # Make the API request
    url = 'https://irctc1.p.rapidapi.com/api/v3/getPNRStatus'
    params = {'pnrNumber': pnr_number}

    try:
        response = requests.get(url, headers=headers, params=params)
        response_data = response.json()
        data=response_data.get('data')
        print(data)
        translator=Translator()
        data['TrainName']=translator.translate(data['TrainName'],dest=lang).text
        data['BoardingStationName'] = translator.translate(
            data['BoardingStationName'], dest=lang).text
        data['ReservationUptoName'] = translator.translate(
            data['ReservationUptoName'], dest=lang).text
        for item in data['PassengerStatus']:
            print(".")
            item['BookingStatus'] = translator.translate(
                item['BookingStatus'], dest=lang).text
            print("1")
            item['CurrentStatus'] = translator.translate(
                item['CurrentStatus'], dest=lang).text
            print("2")
            item['BookingStatusNew'] = translator.translate(
                item['BookingStatusNew'], dest=lang).text
            print("3")
            item['CurrentStatusNew'] = translator.translate(
                item['CurrentStatusNew'], dest=lang).text
            print("4")

        print(data)


        return jsonify(data)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Error connecting to the API'}), 500



@app.route('/get_train_schedule', methods=['GET'])
def get_train_schedule():
    # Get the train number from the request parameters
    train_no = request.args.get('trainNo')
    lang=request.args.get('lang')
    
    # Check if the train number is provided
    if not train_no:
        return jsonify({'error': 'Train number is required'}), 400

    # Define the headers for the API request
    headers = {
        'X-RapidAPI-Key': API_KEY,
        'X-RapidAPI-Host': 'irctc1.p.rapidapi.com'
    }

    # Make the API request
    url = 'https://irctc1.p.rapidapi.com/api/v1/getTrainSchedule'
    params = {'trainNo': train_no}

    try:
        response = requests.get(url, headers=headers, params=params)
        response_data = response.json()
        data=response_data.get('data')
        print(data)
        translator=Translator()
        data['trainType']=translator.translate(data['trainType'],dest=lang).text
        data['trainName'] = translator.translate(
            data['trainName'], dest=lang).text
        for item in data['route']:
            print(".")
            if (item['station_name'] != "" or item['station_name'] == None):
             item['station_name'] = translator.translate(
                item['station_name'], dest=lang).text
            if (item['state_name'] != "" or item['state_name'] == None):
             item['state_name'] = translator.translate(
                item['state_name'], dest=lang).text
        print(data)
        return jsonify(data)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Error connecting to the API'}), 500

@app.route('/queryDetails', methods=['GET'])
def get_all_Details():
    details=request.args.get('query')
    lang=request.args.get('toLang')
     
    translator=Translator()
    translated_text =translator.translate(details, "en").text


  
    starting_point, destination, journey_date, duration, Train_Num, source_code, dest_code, pnr = extract_info(
        translated_text.lower())
    
    dict1 = {

        "searchStation": ["find a station", "find stations", "what stations are there", "what stations are", "describe all stations", "describe stations", "stations list", "list of stations", "what are the stations", "which stations are"],
        "TrainsbetweenStations": ["find trains", "find all trains", "trains list", "what are the trains", "describe all tarins", "describe trains", "list of trains"],
        "TrainNumStatus": ["live status", "currently", "now", "at this moment", "at the moment"],
        "TrainNumSchedule": ["schedule", "on which days", "timings", "type"],
        "PNRNumber": ["pnr"]
    }


    dict2 = {

    "searchStation":  False,
    "TrainbetweenStations": False,
    "TrainNumStatus": False,
    "TrainNumSchedule": False,
    "PNRNumber": False
    }

    print(translated_text)
    sentence = translated_text.lower()
    print(sentence)

    flag = False
    fval = None

    for val in dict1:
       for val1 in dict1[val]:
         if val1 in sentence:
            dict2[val] = True
            fval = val
            flag = True

         if flag:
            break
       if flag:
        break
    print(fval) 
    if(fval=="searchStation"):
      print("dev")
      print(starting_point)
      print(destination)
      if (starting_point != "" and destination != ""):
          
          search_station_response = requests.get(
              f'http://localhost:5000/search_station?query={starting_point}&toLang={lang}')
          print(search_station_response.json())
          search_dest_station_response = requests.get(
              f'http://localhost:5000/search_station?query={destination}&toLang={lang}')
          print(search_dest_station_response.json())
          dict = {"srcStation": search_station_response.json(),
                  "destStation": search_dest_station_response.json()}
          return jsonify(dict)
      elif (starting_point != "" ):

          search_station_response = requests.get(
              f'http://localhost:5000/search_station?query={starting_point}&toLang={lang}')
          print(search_station_response.json())
          return jsonify(search_station_response.json())
      elif(destination!=""):
          search_dest_station_response = requests.get(
              f'http://localhost:5000/search_station?query={destination}&toLang={lang}')
          print(search_dest_station_response.json())
          return jsonify(search_dest_station_response.json())
      if(starting_point=="" and destination==""):
          return jsonify({'warning': 'Enter the details'})
      
    elif (fval == "TrainsbetweenStations"):
        print("ved")
        print(starting_point)
        print(destination)
        print(source_code)
        print(dest_code)
        if(source_code!=None and dest_code!=None and journey_date!=None):
            print("enter")
            trainbtwStations=requests.get(
                f'http://localhost:5000/trains?sourceStation={source_code}&destinationStation={dest_code}&journeyDate={journey_date}&lang={lang}')
            return jsonify(trainbtwStations.json())
        elif (source_code != None and dest_code != None and journey_date == None):
            print("enter 2")
            return jsonify({'warning':'Enter the journey date'})
        elif(starting_point!="" and destination!="" and journey_date!=None):
            print("enter3")
            print(starting_point)
            print(destination)
            search_station_response = requests.get(
              f'http://localhost:5000/search_station?query={starting_point}&toLang={lang}')
            print("enc")
            print(search_station_response.json())
            
            search_dest_station_response = requests.get(
              f'http://localhost:5000/search_station?query={destination}&toLang={lang}')
            print(search_dest_station_response.json())
            dict={"srcStation":search_station_response.json(),"destStation":search_dest_station_response.json(),"message":"Renter the query with cooresponding station codes"}
            print(dict)
            return jsonify(dict)
        elif(source_code!=None and destination!="" and journey_date!=None):
            print("enter4")
            search_dest_station_response = requests.get(
                f'http://localhost:5000/search_station?query={destination}&toLang={lang}')
            dict = {"destStation": search_dest_station_response.json(),
                    "message": "Renter the query with cooresponding destination station codes"}
            return jsonify(dict)
        elif(starting_point!="" and dest_code!=None and journey_date!=None):
            print("enter5")
            search_station_response = requests.get(
                f'http://localhost:5000/search_station?query={starting_point}&toLang={lang}')
            dict = {"srcStation": search_station_response.json(),
                    "message": "Renter the query with cooresponding source station codes"}
            return jsonify(dict)
        else:
            return jsonify({'warning':'Enter the proper details with station codes and journey date'})
        
    elif (fval == "TrainNumStatus"):
        if(Train_Num!=0 and (Train_Num>=10000 and Train_Num<=99999)):
            trainStatus = requests.get(
                f'http://localhost:5000/getLiveTrainStatus?train_num={Train_Num}&lang={lang}')
            return jsonify(trainStatus.json())
        else:
            return jsonify({'warning': 'Enter the proper details with correct train number'})
    
    elif (fval == "TrainNumSchedule"):
        if (Train_Num != 0 and (Train_Num >= 10000 and Train_Num <= 99999)):
            trainSchedule = requests.get(
                f'http://localhost:5000/get_train_schedule?trainNo={Train_Num}&lang={lang}')
            print(trainSchedule.json())
            return jsonify(trainSchedule.json())

        else:
            return jsonify({'warning': 'Enter the proper details with correct train number'})
        
    elif(fval=="PNRNumber"):
        print(pnr)
        if(pnr!=0 and (pnr>=1000000000 and pnr<=9999999999)):
            pnrNum=requests.get(
                f'http://localhost:5000/get_pnr_status?pnrNumber={pnr}&lang={lang}'
            )
            print(pnrNum.json())
            return jsonify(pnrNum.json())
        else:
            return jsonify({'warning': 'Enter the proper details with correct pnr number'})



        


    
 




























@app.route("/voiceData",methods=["GET"])
def get_voice_data():
    print("dev")
    vData=request.args.get("vData")
    lang=request.args.get("toLang")
    print(lang)
    print(vData)
    translator=Translator()
    transVdata=translator.translate(vData,dest="en").text
    print(transVdata)

    starting_point, destination, journey_date, duration, Train_Num ,source_code, dest_code, pnr= extract_info(transVdata)
    s_point=starting_point.split(' ')
    des_point=destination.split(' ')
    print("Starting Point:", s_point[0])
    print("Destination:", des_point[0])
    print("Journey Date:", journey_date)
    print("Duration Time: ", duration)
    
    dictionary={
        "start":translator.translate(s_point[0],src="en",dest=lang).text,
        "dest": translator.translate(des_point[0],src="en", dest=lang).text,
        "date":journey_date
    }

    print(dictionary)

    return jsonify(dictionary)


@app.route('/getLiveTrainStatus', methods=['GET'])
def get_live_station():
    st = request.args.get("train_num")
    lang=request.args.get("lang")
    print(st)
    try:
        url = 'https://irctc1.p.rapidapi.com/api/v1/liveTrainStatus'
        headers = {
            'X-RapidAPI-Key': API_KEY,
            'X-RapidAPI-Host': 'irctc1.p.rapidapi.com'
        }
        params = {
            'trainNo':st ,
            
        }

        response = requests.get(url, params=params, headers=headers)
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
           
            newdata = data.get("data")
            print(newdata)
            translator=Translator()
            if(newdata['new_alert_msg']!=""):
               
               
                newdata['new_alert_msg']=translator.translate(newdata['new_alert_msg'],dest=lang).text
                print("abc")
            for item in newdata['current_location_info']:
                if(item['hint']!=""):
                 item['hint']=translator.translate(item['hint'],dest=lang).text
                if(item['readable_message']!=""):
                 item['readable_message']=translator.translate(item['readable_message'],dest=lang).text
                print("asme")
           
            print(newdata)
            return jsonify(newdata)
        else:
            return jsonify({"error": "Failed to fetch data from the API"})

    except Exception as e:
        return jsonify({"error": str(e)})



@app.route("/trains", methods=["GET"])
def get_trains():
    
    source_station = request.args.get("sourceStation")
    destination_station = request.args.get("destinationStation")
    journey_date = request.args.get("journeyDate")
    lang=request.args.get("lang")
    
    print(source_station)


    params = {
        "fromStationCode": source_station,
        "toStationCode": destination_station,
        "dateOfJourney": journey_date,
    }

    try:
        response = requests.get(irctc_api_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            newdata=data.get('data')
            
            translator = Translator()
            for item in newdata:
                print("ak")
                item['train_name']=translator.translate(item['train_name'],dest=lang).text
                
                item['from_station_name']=translator.translate(item['from_station_name'],dest=lang).text
                item['to_station_name'] = translator.translate(item['to_station_name'], dest=lang).text
            print() 
            print(newdata)
            return jsonify(newdata)
        else:
            return jsonify({"error": "Failed to fetch data from IRCTC API"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)