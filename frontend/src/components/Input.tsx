import { SetStateAction, useEffect, useRef, useState } from "react";

import FileUploadIcon from "@mui/icons-material/FileUpload";
import SendIcon from "@mui/icons-material/Send";
import TextareaAutosize from "react-textarea-autosize";
import Config from "../config";
import "./Input.css";
import Button from 'react-bootstrap/Button'
import { AudioConfig, AudioInputStream, PullAudioInputStreamCallback, AutoDetectSourceLanguageConfig,SpeechRecognitionEventArgs,SpeechConfig, SpeechRecognizer,Recognizer,ResultReason,CancellationReason } from 'microsoft-cognitiveservices-speech-sdk'

const API_KEY = "XXXXXXXXXXXXXX"
const API_LOCATION = "westus2"

// this will be used for continuous speech recognition

const speechConfig = SpeechConfig.fromSubscription(API_KEY, API_LOCATION)
const autoDetectSourceLanguageConfig = AutoDetectSourceLanguageConfig.fromLanguages(["zh-cn","en-US"]);

// recognizer must be a global variable
let recognizer:SpeechRecognizer


export default function Input(props: { onSendMessage: any, onStartUpload: any, onCompletedUpload: any }) {

  const [isRecognising, setIsRecognising] = useState(false)

  const toggleListener = () => {
    if (!isRecognising) {
      startRecognizer()
      setUserInput("")
    } else {
      stopRecognizer()
    }
  }

  useEffect(() => {
    var constraints = {
      video: false,
      audio: {
        channelCount: 1,
        sampleRate: 16000,
        sampleSize: 16,
        volume: 1
      }
    }
    const getMedia = async (constraints: MediaStreamConstraints) => {
      let stream = null
      try {
        stream = await navigator.mediaDevices.getUserMedia(constraints)
        createRecognizer(stream)
      } catch (err) {
        /* handle the error */
        alert(err)
        console.log(err)
      }
    }

    getMedia(constraints)

    return () => {
      console.log('unmounting...')
      if (recognizer) {
        stopRecognizer()
      }
    }

  }, [])


  // this function will create a speech recognizer based on the audio Stream
  // NB -> it will create it, but not start it
  const createRecognizer = (audioStream: AudioInputStream | PullAudioInputStreamCallback | MediaStream) => {

    // configure Azure STT to listen to an audio Stream
    const audioConfig = AudioConfig.fromStreamInput(audioStream)

    // recognizer is a global variable
    recognizer = SpeechRecognizer.FromConfig(speechConfig, autoDetectSourceLanguageConfig,audioConfig)

    recognizer.recognizing = (_s: any, e: { result: { text: SetStateAction<string>; }; }) => {

      // uncomment to debug
      // console.log(`RECOGNIZING: Text=${e.result.text}`)
      setUserInput(e.result.text)
    }

    (recognizer as Recognizer).recognized = (_s:any, e:SpeechRecognitionEventArgs) => {
      setUserInput("")
      if (e.result.reason === ResultReason.RecognizedSpeech) {

        // uncomment to debug
        // console.log(`RECOGNIZED: Text=${e.result.text}`)

        setUserInput((recognisedText) => {
          if (recognisedText === '') {
            return `${e.result.text} `
          }
          else {
            return `${recognisedText}${e.result.text} `
          }
        })
      }
      else if (e.result.reason === ResultReason.NoMatch) {
        console.log("NOMATCH: Speech could not be recognized.")
      }
    }

    (recognizer as SpeechRecognizer).canceled = (_s, e) => {
      console.log(`CANCELED: Reason=${e.reason}`)

      if (e.reason === CancellationReason.Error) {
        console.log(`"CANCELED: ErrorCode=${e.errorCode}`)
        console.log(`"CANCELED: ErrorDetails=${e.errorDetails}`)
        console.log("CANCELED: Did you set the speech resource key and region values?")
      }
      (recognizer as SpeechRecognizer).stopContinuousRecognitionAsync()
    }

    (recognizer as Recognizer).sessionStopped = (_s:any, _e:any) => {
      (recognizer as SpeechRecognizer).stopContinuousRecognitionAsync()
    }
  }

  // this function will start a previously created speech recognizer
  const startRecognizer = () => {
    (recognizer as Recognizer).startContinuousRecognitionAsync()
    setIsRecognising(true)
  }

  // this function will stop a running speech recognizer
  const stopRecognizer = () => {
    setIsRecognising(false);

    (recognizer as SpeechRecognizer).stopContinuousRecognitionAsync()
  }

  let fileInputRef = useRef<HTMLInputElement>(null);
  let [inputIsFocused, setInputIsFocused] = useState<boolean>(false);
  let [userInput, setUserInput] = useState<string>("");

  const handleInputFocus = () => {
    setInputIsFocused(true);
  };

  const handleInputBlur = () => {
    setInputIsFocused(false);
  };

  const handleUpload = (e: any) => {
    e.preventDefault();
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: any) => {
    if (e.target.files.length > 0) {
      const file = e.target.files[0];

      // Create a new FormData instance
      const formData = new FormData();

      // Append the file to the form data
      formData.append("file", file);

      props.onStartUpload(file.name);

      try {
        const response = await fetch(Config.WEB_ADDRESS + "/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const json = await response.json();
        props.onCompletedUpload(json["message"]);

      } catch (error) {
        console.error("Error:", error);
      }
    }
  };
  

  const handleSendMessage = async () => {
    props.onSendMessage(userInput);
    setUserInput("");
    stopRecognizer()
  }

  const handleInputChange = (e: any) => {
    setUserInput(e.target.value);
  };

  const handleKeyDown = (e: any) => {
    if (e.key === "Enter" && e.shiftKey === false) {
        e.preventDefault();
        handleSendMessage();
    }
  };

  return (
    <div className="input-parent">
      <div className={"input-holder " + (inputIsFocused ? "focused" : "")}>
        <form className="file-upload">
          <input
            onChange={handleFileChange}
            ref={fileInputRef}
            style={{ display: "none" }}
            type="file"
          />
          <Button variant={isRecognising ? "secondary" : "primary"}
            style={{ color: 'black' }}
            onClick={() => toggleListener()}>
            {isRecognising ? '语音输入...' : '文字输入...'}
          </Button>
          <button type="button" onClick={handleUpload}>
            <FileUploadIcon />
          </button>
        </form>
        <TextareaAutosize
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          value={userInput}
          rows={1}
          placeholder="Send a message"
        />
        <button className="send" onClick={handleSendMessage}>
          <SendIcon />
        </button>
      </div>
    </div>
  );
}
