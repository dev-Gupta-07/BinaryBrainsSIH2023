import React,{useState,useEffect} from 'react'
import { useLocation } from 'react-router-dom'
import axios from 'axios'
import {franc} from 'franc-min'
import CustomButton from '../components/CustomButton'
const Announcement = () => {
    const { state } = useLocation();
    const [iniLang,setIniLang]=useState("")
    const [mainLanguage,setMainLanguage]=useState([])
    console.log(iniLang)
    function startListening() {
      console.log("Hello World!");
      if (
        "SpeechRecognition" in window ||
        "webkitSpeechRecognition" in window
      ) {
        const recognition = new (window.SpeechRecognition ||
          window.webkitSpeechRecognition)();

        recognition.lang = `${iniLang}-IN`;
        recognition.interimResults = false;

        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          console.log(`You said: ${transcript}`);
          const response = axios.get(
            
            `/announcement?query=${transcript}&toLang=${state}`
          );
          console.log(response);
       

          //console.log(voiceData);
          // const response=axios.get(`/voiceData?vData=${transcript}&toLang=${state}`);
          // console.log(response)
          // response.then((obj)=>{
          //   const res=obj.data;
          //   console.log(res)

          //  console.log(1);

          //    voicehandleSearchSourceStations(res.start);
          //    setTimeout(()=>{
          //      voicehandleSearchDestinationStations(res.dest)

          //    },30000)
          //    setJourneyDate(res.date);

          //  } )

          const lang = franc(transcript);
          const messages = {
            en: "You said: ",
            hi: "आपने कहा: ",
          };

          console.log(messages[lang] + transcript);
        };

        recognition.onerror = (event) => {
          console.error("Speech recognition error:", event.error);
        };

        recognition.start();

        setTimeout(() => {
          recognition.stop();
        }, 10000);
      } else {
        alert("Speech recognition is not supported in this browser.");
      }
    }

    const languages = [
      { name: "en", script: "English" },
      { name: "hi", script: "हिन्दी" },
      { name: "bn", script: "বাংলা" },
      { name: "te", script: "తెలుగు" },
      { name: "mr", script: "मराठी" },
      { name: "ta", script: "தமிழ்" },
      { name: "ur", script: "اُردو" },
      { name: "gu", script: "ગુજરાતી" },
      { name: "kn", script: "ಕನ್ನಡ" },
      { name: "or", script: "ଓଡ଼ିଆ" },
      { name: "pa", script: "ਪੰਜਾਬੀ" },
      { name: "ml", script: "മലയാളം" },
      { name: "as", script: "অসমীয়া" },
      { name: "mai", script: "मैथिली" },
      { name: "sat", script: "ᱥᱟᱱᱛᱟᱲᱤ" },
      { name: "ks", script: "کٲشُر" },
      { name: "ne", script: "नेपाली" },
      { name: "kok", script: "कोंकणी" },
      { name: "sd", script: "سنڌي" },
      { name: "doi", script: "ڈوگری" },
      { name: "brx", script: "बर’" },
    ];
   
   
   

  return (
    <div>
      <h1>Announcement</h1>
      <select
        title="Select lang"
        onChange={(e) => {
          setIniLang(e.target.value);
        }}
      >
        {languages.map((lang) => {
          return <option value={lang.name}>{lang.script}</option>;
        })}
      </select>

      <CustomButton title="Speak" handleClick={startListening} />
    </div>
  );
}

export default Announcement
